from BenchPilotSDK.orchestrators.containerOrchestrator import ContainerOrchestrator
from BenchPilotSDK.services.service import Service
from BenchPilotSDK.orchestrators.setup.setupSwarmOrchestrator import SetupSwarmOrchestrator
import subprocess, os, time, docker


class DockerSwarmOrchestrator(ContainerOrchestrator):
    """
    The containerOrchestrator is responsible to orchestrate the deployment. As for now
    it only supports Docker Swarm, but in the future we will extend it for Kubernetes as well.
    """

    def __init__(self, manager: str = None, cluster: list = None, docker_compose_version: str = "3.3"):
        super().__init__(manager, cluster)
        # todo: check docker compose version
        self.docker_compose_version = docker_compose_version
        self.setupOrchestrator = SetupSwarmOrchestrator(manager, cluster)

    @staticmethod
    def deploy_services():
        # remove first any service already exists and then deploy cluster
        if int(subprocess.check_output("docker service ls | wc -l", shell=True)) > 1:
            subprocess.run("docker service rm $(docker service ls -q)", shell=True)
        subprocess.run("docker stack deploy --prune --compose-file " + os.environ["BENCHPILOT_PATH"] + 'BenchPilotSDK/conf/docker-compose.yaml' + ' benchPilot', shell=True)

    @staticmethod
    def redeploy_service(service: Service):
        subprocess.run(
            "docker service update --force $(docker service ls | grep " + service.hostname + " | awk '{print $1}')",
            shell=True)

    def compose_yaml(self, services: Service):
        # delete existing docker-compose file (if exists) and create a new one with the needed services
        if os.path.exists(os.environ["BENCHPILOT_PATH"] + "BenchPilotSDK/conf/docker-compose.yaml"):
            os.remove(os.environ["BENCHPILOT_PATH"] + "BenchPilotSDK/conf/docker-compose.yaml")

        docker_compose_start = "version: '" + self.docker_compose_version + """'
services:"""
        docker_compose_end = """networks:
  benchPilot:
    external: true"""
        with open(os.environ["BENCHPILOT_PATH"] + 'BenchPilotSDK/conf/docker-compose.yaml', 'w+') as outfile:
            docker_services_str = docker_compose_start
            for docker_service in services:
                # check if service has other services inside:
                if hasattr(docker_service, "services"):
                    inner_services_str = ""
                    for inner_service in docker_service.services:
                        inner_services_str += self.service_str_compose(self.setupOrchestrator.cluster_nodes, inner_service)
                    docker_services_str += inner_services_str
                else:
                    docker_services_str += self.service_str_compose(self.setupOrchestrator.cluster_nodes, docker_service)
            docker_services_str += docker_compose_end
            outfile.write(docker_services_str)
        outfile.close()

    @staticmethod
    def service_str_compose(cluster_nodes, service: Service):
        # Declare IMAGE, HOSTNAME and RESTART conf
        string = "\n\n# " + service.hostname.upper()
        if not "manager" in service.placement:
            image_tag = service.image_arm_tag if "aarch64" in cluster_nodes[service.placement]["architecture"] else service.image_tag
        else:
            image_tag = service.image_tag
        string += "\n  " + service.hostname + ":\n    " + "image: " + service.image + ":" + image_tag + "\n    " + \
                  "hostname: " + service.hostname + "\n    " + "restart: " + service.restart + "\n"
        # Declare PORTS
        if hasattr(service, "ports") and len(service.ports) > 0:
            string += "    " + "ports:\n"
            for port in service.ports:
                string += "      - " + port + "\n"
        # Declare NETWORKS
        string += "    " + "networks:\n"
        networks = ["benchPilot"]
        for network in networks:
            string += "      - " + network + "\n"
        # Declare ENVIRONMENT
        if hasattr(service, "environment") and len(service.environment) > 0:
            string += "    " + "environment:\n"
            for env in service.environment:
                string += "      - " + env + "\n"
        # Declare COMMAND
        if hasattr(service, "command") and len(service.command) > 0:
            string += "    " + "command: " + service.command + "\n"
        # Declare VOLUMES
        if hasattr(service, "volumes") and len(service.volumes) > 0:
            string += "    " + "volumes:\n"
            for volume in service.volumes:
                string += "      - " + volume + "\n"
        # Declare DEPENDS_ON
        if hasattr(service, "depends_on") and len(service.depends_on) > 0:
            string += "    " + "depends_on:\n"
            for depend in service.depends_on:
                string += "      - " + depend + "\n"
        string += "    " + "deploy:" + "\n      " + "placement:" + "\n        " + "constraints:\n"
        # Declare DEPLOYMENT
        placement = "node."
        if "manager" in service.placement:
            placement += "role"
        else:
            placement += "hostname"
        placement += "==" + service.placement
        string += "          - " + placement + "\n"
        return string

    @staticmethod
    def container_wise_service_has_started(service: Service):
        # initialize seconds of waiting
        service.sec_waiting = 0
        container_name = service.hostname
        waiting_msg = "-------- Waiting to check if " + container_name + " has started --------"
        timeout_msg = "________ Docker Swarm Service: " + container_name + " timeout ________"
        while service.container_service_has_not_started:
            output = subprocess.check_output("docker service ls | awk '{print $2,$4}'", shell=True)
            if container_name in str(output):
                output = subprocess.check_output(
                    "docker service ls | awk '{print $2,$4}' | grep " + container_name, shell=True)
                if "1/1" in str(output):
                    service.container_service_has_not_started = False
                elif service.sec_waiting < 240:
                    # wait for 1 sec and retry
                    print(waiting_msg)
                    time.sleep(1)
                    service.sec_waiting += 1
                else:
                    print(timeout_msg)
                    return -1
            elif service.sec_waiting < 240:
                # wait for 1 sec and retry
                print(waiting_msg)
                time.sleep(1)
                service.sec_waiting += 1
            else:
                print(timeout_msg)
                return -1
        print("Docker Swarm Service: %s has been deployed" % container_name)

    @staticmethod
    def get_container_name(service: Service):
        # client = docker.from_env()
        containers = client.containers.list()
        for container in containers:
            if service.hostname in container.name:
                return container.name
        return -1

    @staticmethod
    def application_wise_service_has_started(service: Service):
        # initialize seconds of waiting
        service.sec_waiting = 0
        while service.application_service_has_not_started:
            logs = subprocess.check_output(
                "docker service logs $(docker service ls | awk '{print $2}' | grep " + service.hostname + ")",
                shell=True)
            if service.service_log in str(logs):
                service.application_service_has_not_started = False
            elif service.sec_waiting < 180:
                # wait for 1 sec and retry
                print("Waiting 1 seconds to retry to check if %s has started" % service.hostname)
                time.sleep(1)
                service.sec_waiting += 1
            else:
                print("Service: %s timeout" % service.hostname)
                print("Service's logs: %s" % str(logs))
                return -1
        print("Service: %s has started" % service.hostname)
