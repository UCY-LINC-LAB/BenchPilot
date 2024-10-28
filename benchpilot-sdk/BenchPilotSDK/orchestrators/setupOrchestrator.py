import os, paramiko, yaml
from tqdm import tqdm, trange
from abc import abstractmethod
from BenchPilotSDK.utils.exceptions import *
import BenchPilotSDK.utils.benchpilotProcessor as bp
from BenchPilotSDK.utils.loggerHandler import LoggerHandler


class SetupOrchestrator:
    """
    This class contains methods that will facilitate with the setting up process of docker, docker images and orchestrator
    Please keep in mind that for specific orchestrator it is needed to setup the appropriate inherited class
    """
    cluster_nodes = {}
    orchestrator_nodes = []
    node_required_attributes = ["username", "hostname"]
    node_key_pass_attribute = ["password", "ssh_key_path"]

    def __init__(self, cluster: dict):
        self.logger = LoggerHandler().logger
        self.list_of_images = None
        cluster_file = os.environ["BENCHPILOT_PATH"] + 'BenchPilotSDK/conf/BenchPilot-cluster.yaml'
        if 'CLUSTER_FILE' in os.environ:
            cluster_file = os.environ['CLUSTER_FILE']
        cluster_file = open(cluster_file, "r")
        try:
            self.cluster = yaml.safe_load(cluster_file)
        except yaml.YAMLError:
            raise BenchClusterInvalidException()
        self.manager = self.get_manager()
        self.workload_cluster = cluster

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
    def register_to_orchestrator(self, hostname: str, client: paramiko.SSHClient()):
        # override for the appropriate orchestrator
        pass
    
    def get_manager(self):
        bp.check_required_parameters('BenchPilot-cluster.yaml:', ["cluster"], self.cluster)
        self.cluster = self.cluster["cluster"]
        bp.check_required_parameters('BenchPilot-cluster.yaml: cluster', ["manager"], self.cluster)
        os.environ["MANAGER_IP"] = self.cluster["manager"]["ip"]
        return self.cluster["manager"]["ip"]

    def setup_cluster_nodes(self):
        self.nodes = self.cluster["nodes"]
        i_node = 0
        with trange(len(self.workload_cluster)) as t:
            for i in t:
                workload_node = self.workload_cluster[i_node]
                self.setup_cluster_node(workload_node, t)
                i_node += 1

    def setup_cluster_node(self, workload_node, t):
        found_node = False
        if workload_node == self.manager or workload_node == "manager":
            return True
        for node in self.nodes:
            bp.check_required_parameters('BenchPilot-cluster.yaml: cluster > nodes', ["ip", "hostname"], node)
            if workload_node == node["hostname"]:
                self.check_node_attributes(node)
                ip = node["ip"]
                hostname = node["hostname"]
                username = node["username"]
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.logger.info("Connecting on: " + hostname)
                t.set_description('Connecting on Cluster Node ' + hostname)
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
                t.set_description('Setting Up Docker on a Cluster Node')
                self.setup_docker(hostname, client, node["architecture"])
                self.cluster_nodes[hostname] = {"architecture": node["architecture"]}
                t.set_description('Registering Cluster Node')
                self.logger.info("---BenchPilot: Registering Worker " + hostname + " to Orchestrator---")
                if not hostname in self.orchestrator_nodes:
                    self.register_to_orchestrator(hostname, client)
                else:
                    self.logger.info("Worker " + hostname + " was already registerd")

                t.set_description('Pulling Docker Images')
                self.build_docker_worker_images(client, node["architecture"])
                client.close()
                found_node = True
        if not found_node:
            self.logger.error(
                "Setup Failed: The cluster node " + workload_node + " does not exist in BenchPilot-cluster.yaml. Please update your cluster info.")
            raise BenchClusterInvalidException

    def check_node_attributes(self, node):
        bp.check_required_parameters('BenchPilot-cluster.yaml: node', self.node_required_attributes, node)
        if not (self.node_key_pass_attribute[0] in node) and not (self.node_key_pass_attribute[1] in node):
            raise MissingBenchExperimentAttributeException(
                'node ' + self.node_key_pass_attribute[0] + " or " + self.node_key_pass_attribute[1])

    # returns docker hostname
    @staticmethod
    def setup_docker(hostname: str, client: paramiko.SSHClient, node_architecture):
        logger = LoggerHandler().logger
        logger.info("BenchPilot: --- Checking Docker is installed ---")
        stdin, stdout, stderr = client.exec_command("docker --version")
        output = stdout.readlines()
        if len(output) == 0 or (len(output) > 1 and not ("Docker version" in output[1])):
            stdin, stdout, stderr = client.exec_command("sudo apt-get -y update && sudo apt-get -y upgrade")
            stdin, stdout, stderr = client.exec_command("sudo apt-get install -y curl")
            stdin, stdout, stderr = client.exec_command("curl -sSL https://get.docker.com | sh")
            stdin, stdout, stderr = client.exec_command("sudo usermod -aG docker ${USER}")
            stdin, stdout, stderr = client.exec_command("groups ${USER}")
            stdin, stdout, stderr = client.exec_command(
                "sudo apt-get -y install libffi-dev libssl-dev python3-dev python3 python3-pip")
            stdin, stdout, stderr = client.exec_command("sudo pip3 install docker-compose")
            stdin, stdout, stderr = client.exec_command("sudo systemctl enable docker")
            stdin, stdout, stderr = client.exec_command("newgrp docker")
        else:
            logger.info("Docker already installed on: " + hostname)
            return
        stdin, stdout, stderr = client.exec_command("docker --version")
        stdout = stdout.readlines()
        if len(stdout) < 1 or not ("Docker version" in stdout[0]):
            logger.error("Error installing docker on: " + hostname)
            raise DockerNotInstalled()
        logger.info("Docker successfully installed on: " + hostname)

    def build_docker_manager_images(self):
        # as for now it just pulls the images
        node_architecture = bp.kernel_run("uname -m", get_output=True)
        for image in self.list_of_images["manager"]:
            pulled_images = bp.kernel_run('docker image ls --format "{{.Repository}}:{{.Tag}}"', process_output=True)
            image = image["name"] + ":" + self.__get_image_tag(image, node_architecture)
            if not self.__check_if_images_exist(image, pulled_images):
                self.logger.info("docker pull " + image)
                bp.kernel_run("docker pull " + image)
            else:
                self.logger.info("Image " + image + " already pulled")

    def build_docker_worker_images(self, client: paramiko.SSHClient, node_architecture):
        # as for now it just pulls the images
        for image in self.list_of_images["worker"]:
            stdin, stdout, stderr = client.exec_command('docker image ls --format "{{.Repository}}:{{.Tag}}"')
            pulled_images = bp.process_check_output(stdout.read())
            image = image["name"] + ":" + self.__get_image_tag(image, node_architecture)
            if not self.__check_if_images_exist(image, pulled_images):
                self.logger.info("docker pull " + image)
                stdin, stdout, stderr = client.exec_command("docker pull " + image)
                # force - wait till the image is pulled
                output = stdout.read()
            else:
                self.logger.info("Image " + image + " already pulled")
    
    def get_node_proxy(self, node):
        proxies = {}
        if node == "manager" and "proxies" in self.cluster["manager"]:
            proxies = self.cluster["manager"]["proxies"]
        else:
            for i_node in self.nodes:
                if i_node["hostname"] == node and "proxies" in i_node:
                    proxies = i_node["proxies"]
        return proxies
            

    @staticmethod
    def __check_if_images_exist(image: str, pulled_images: []):
        for i in range(0, len(pulled_images)):
            if image == pulled_images[i]:
                return True
        return False

    @staticmethod
    def __get_image_tag(image, node_architecture):
        image_tag = image["arm_tag"] if "aarch64" in str(node_architecture).lower() or "armv7l" in str(
            node_architecture).lower() else image["tag"]
        if image_tag is None:
            raise UnsupportedImageArchitectureException(
                "The image " + image["name"] + " is not supported on " + str(node_architecture).lower())
        return image_tag
