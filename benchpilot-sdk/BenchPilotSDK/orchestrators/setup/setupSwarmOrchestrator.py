from BenchPilotSDK.orchestrators.setup.setupOrchestrator import SetupOrchestrator
import subprocess, paramiko


class SetupSwarmOrchestrator(SetupOrchestrator):
    """
    This class contains overrrides the appropriate methods in order to setup automatically a
    docker swarm cluster
    """
    def __init__(self, manager: str, cluster: list):
        super().__init__(manager, cluster)
        self.docker_swarm_join_token = ""

    def setup_orchestrator(self):
        print("---BenchPilot: Setting up Swarm---")
        # create a new docker swarm if there isn't one yet
        swarm_info = str(subprocess.check_output("docker info | grep Swarm", shell=True)).lower()
        
        # remove any previous docker swarm that wasn't configured correctly
        if not ("active" in swarm_info) and not ("inactive" in swarm_info):
            subprocess.run(["docker", "swarm", "leave"])
        
        # initiate new docker swarm
        if not (" active" in swarm_info):
            subprocess.run(["docker", "swarm", "init", "--advertise-addr", self.manager])

        # get swarm join worker token
        join_token = subprocess.check_output(["docker", "swarm", "join-token", "worker"])
        join_token = str(join_token).split("--token")[1]
        join_token = str(join_token).split(self.manager)[0]
        join_token = join_token.split(" ")[1]

        # create a new overlay network if it doesn't exist yet
        output = subprocess.check_output("docker network ls", shell=True)
        if "benchPilot" in str(output):
            output = subprocess.check_output("docker network ls | grep benchPilot", shell=True)
            if not ("overlay" in str(output) and "swarm" in str(output)):
                subprocess.run(
                    ["docker", "network", "rm", "benchPilot", "&&", "docker", "network", "create", "-d", "overlay",
                     "benchPilot"])
        else:
            subprocess.run(["docker", "network", "create", "-d", "overlay", "benchPilot"])
        self.docker_swarm_join_token = join_token

    def register_to_orchestrator(self, client: paramiko.SSHClient()):
        print("---BenchPilot: Worker registering on swarm---")
        client.exec_command('docker swarm leave')
        stdin, stdout, stderr = client.exec_command(
            'docker swarm join --token ' + self.docker_swarm_join_token + " " + self.manager + ':2377')
        print(stdout.readlines())
