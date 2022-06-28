import os, subprocess, paramiko, yaml
from abc import abstractmethod
from sys import exit
from BenchPilotSDK.utils.exceptions import InvalidSshKeyPath, MissingBenchExperimentAttributeException, \
    BenchClusterInvalidException, UnsupportedImageArchitectureException
from BenchPilotSDK.workloads.setup.workloadSetup import WorkloadSetup


class SetupOrchestrator:
    """
    This class contains methods that will facilitate with the setting up process of docker, docker images and orchestrator
    Please keep in mind that for specific orchestrator it is needed to setup the appropriate inherited class
    """
    cluster_nodes = {}
    node_required_attributes = []

    def __init__(self, manager: str, cluster: list):
        self.list_of_images = None
        cluster_file = open(os.environ['CLUSTER_FILE'] if 'CLUSTER_FILE' in os.environ else os.environ["BENCHPILOT_PATH"] + 'BenchPilotSDK/conf/bench-cluster-setup.yaml', "r")
        try:
            self.cluster = yaml.safe_load(cluster_file)
        except yaml.YAMLError:
            raise BenchClusterInvalidException()
        self.node_required_attributes.append("hostname")
        self.node_required_attributes.append("username")
        self.node_key_pass_attribute = ["password", "ssh_key_path"]
        self.manager = manager
        self.workload_cluster = cluster["nodes"]

    def setup_cluster(self, list_of_images):
        # for the orchestrator we assume that docker is already installed (since BenchPilot will be run on docker)
        self.list_of_images = list_of_images
        self.setup_orchestrator()
        self.build_docker_manager_images()
        self.setup_cluster_nodes()

    @abstractmethod
    def setup_orchestrator(self):
        # override for the appropriate orchestrator
        pass

    @abstractmethod
    def register_to_orchestrator(self, client: paramiko.SSHClient()):
        # override for the appropriate orchestrator
        pass

    def setup_cluster_nodes(self):
        WorkloadSetup.check_required_parameters('bench-cluster-setup.yaml:', ["cluster"], self.cluster)
        self.cluster = self.cluster["cluster"]
        
        for workload_node in self.workload_cluster:
            found_node = False
            for node in self.cluster:
                WorkloadSetup.check_required_parameters('bench-cluster-setup.yaml: cluster', ["node"], node)
                node = node["node"]
                if workload_node == node["hostname"]:
                    self.check_node_attributes(node)
                    ip = node["ip"]
                    hostname = node["hostname"]
                    username = node["username"]
                    client = paramiko.SSHClient()
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    print("Connecting on: " + hostname)
                    if "ssh_key_path" in node:
                        ssh_key = node["ssh_key_path"]
                        if not os.path.exists(ssh_key):
                            raise InvalidSshKeyPath(hostname)
                        client.connect(hostname=ip, username=username, key_filename=ssh_key)
                    else:
                        password = node["password"]
                        client.connect(hostname=ip, username=username, password=password)
                    stdin, stdout, stderr = client.exec_command('uname -m')
                    node["architecture"] = str(stdout.readlines())
                    self.setup_docker(hostname, client, node["architecture"])
                    self.cluster_nodes[hostname] = {"architecture": node["architecture"]}
                    self.register_to_orchestrator(client)
                    self.build_docker_worker_images(client, node["architecture"])
                    client.close()
                    found_node = True
            if not found_node:
                print("Setup Failed: The cluster node " + workload_node + " does not exist in bench-cluster-setup.yaml. Please update your cluster info.")
                exit()
                
    def check_node_attributes(self, node):
        WorkloadSetup.check_required_parameters('bench-cluster-setup.yaml: node', self.node_required_attributes, node)
        if not (self.node_key_pass_attribute[0] in node) and not (self.node_key_pass_attribute[1] in node):
            raise MissingBenchExperimentAttributeException(
                'node ' + self.node_key_pass_attribute[0] + " or " + self.node_key_pass_attribute[1])

    # returns docker hostname
    @staticmethod
    def setup_docker(hostname: str, client: paramiko.SSHClient, node_architecture):
        print("BenchPilot: --- Checking Docker is installed ---")
        stdin, stdout, stderr = client.exec_command("cat /etc/issue*")
        os_distr = str(stdout.readlines())
        if len(os_distr) < 1:
            print("Cannot get operating system -> please install docker manually")
            exit()
        os_distr = os_distr[0].lower()
        stdin, stdout, stderr = client.exec_command("docker --version")
        output = stdout.readlines()
        if len(output) == 0 or (len(output) > 1 and not ("Docker version" in output[1])):
            # todo: it never installs ..
            stdin, stdout, stderr = client.exec_command("sudo apt-get update")
            print(stdout.readlines())
            print(stderr.readlines())
            stdin, stdout, stderr = client.exec_command("sudo apt-get install ca-certificates curl gnupg lsb-release")
            print(stdout.readlines())
            print(stderr.readlines())
            if "ubuntu" in os_distr:
                client.exec_command(
                    "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg")
                client.exec_command('echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null')
                client.exec_command("sudo apt-get update")
                client.exec_command("sudo apt-get install docker-ce docker-ce-cli containerd.io")
            elif "raspbian" in os_distr:
                if len(node_architecture) < 1:
                    print("Cannot get node architecture")
                    exit()
                if not ("armv7l" in node_architecture[0].lower()):
                    print("Cannot install docker: Unsupported OS or architecture")
                    exit()
                stdin, stdout, stderr = client.exec_command("curl -fsSL https://get.docker.com -o get-docker.sh")
                print(stdout.readlines())
                print(stderr.readlines())
                client.exec_command("sudo sh get-docker.sh")
            else:
                print("Cannot install docker: Unsupported OS or architecture")
                exit()
        else:
            print("Docker already installed on: " + hostname)
            return
        stdin, stdout, stderr = client.exec_command("docker --version")
        stdout = stdout.readlines()
        if len(stdout) < 1 or not ("Docker version" in stdout[0]):
            print("Error installing docker on: " + hostname)
            exit()
        print("Docker successfully installed on: " + hostname)

    def build_docker_manager_images(self):
        node_architecture = subprocess.check_output("uname -m", shell=True)
        for image in self.list_of_images["manager"]:
            subprocess.run("docker pull " + image["name"] + ":" + self.__get_image_tag(image, node_architecture), shell=True)

    def build_docker_worker_images(self, client: paramiko.SSHClient, node_architecture):
        print("worker")
        for image in self.list_of_images["worker"]:
            print("docker pull " + image["name"] + ":" + self.__get_image_tag(image, node_architecture))
            stdin, stdout, stderr = client.exec_command("docker pull " + image["name"] + ":" + self.__get_image_tag(image, node_architecture))
            print(stdout.readlines())

    @staticmethod
    def __get_image_tag(image, node_architecture):
        # todo: support more tags and architectures
        image_tag = image["arm_tag"] if "aarch64" in str(node_architecture).lower() else image["tag"]
        if image_tag.lower() == 'not supported':
            raise UnsupportedImageArchitectureException()
        return image_tag
