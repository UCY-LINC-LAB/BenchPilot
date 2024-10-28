import os
from abc import abstractmethod
from dataclasses import dataclass

from BenchPilotSDK.services.service import Service
from BenchPilotSDK.orchestrators.setupOrchestrator import SetupOrchestrator
from BenchPilotSDK.utils.loggerHandler import LoggerHandler


@dataclass
class ContainerOrchestrator:
    """
    The containerOrchestrator is responsible to orchestrate the deployment. As for now
    it only supports Docker Swarm, but in the future we will extend it for Kubernetes as well.
    """
    cluster: dict = None

    def __post_init__(self):
        # define the specific setup class for each orchestrator
        self.name = "Container Orchestrator"
        self.setupOrchestrator = SetupOrchestrator(self.cluster)
        self.logger = LoggerHandler().logger
        self.compose_path = os.environ["BENCHPILOT_PATH"] + 'BenchPilotSDK/conf/benchPilotExtraConf/'
        self.compose_files = []
        self.compose_files.append(self.compose_path + "docker-compose.yaml")

    '''
    If the orchestrator provides a specific command formatting, you can implement it with this method,
    returning with the right syntax the command for formatting the output.
    '''
    @staticmethod
    def orchestrator_format_command(atts:[]):
        pass

    '''
    Responsible to deploy the services after they have been composed in a yaml file, 
    in case of multiple compose files, then the user needs to pass the compose files
    '''

    @abstractmethod
    def deploy_workload(self, workload_name: str):
        pass

    '''
    Responsible to undeploy the services after they have been deployed.
    '''

    def undeploy_workload(self, workload_name: str):
        pass

    '''
    Responsible to delete everything that was created during the experiment.
    '''
    def delete_experiment_leftovers(self, workload_name: str):
        pass

    '''
    Responsible to wait for all workload's services to finish / stop.
    '''

    def wait_workload_to_finish(self, workload_name: str, services: [], return_state: bool = False):
        pass

    '''
    Responsible to add a new compose file in the list, in case of needing to deploy multiple compose files
    '''

    def add_new_compose_file(self, compose_file_name):
        self.compose_files.append(self.compose_path + compose_file_name)

    '''
    Responsible to clean-up all compose files that the orchestrator created
    '''

    @abstractmethod
    def delete_compose_files(self):
        for compose_file in self.compose_files:
            if os.path.exists(compose_file):
                os.remove(compose_file)

    '''
    Responsible to compose - write in a yaml file the deployable services. Expects the list of services
    '''

    @abstractmethod
    def compose_orchestrator_file(self, services: [], compose_file_name: str, workload_name: str):
        pass

    '''
    Responsible to return as a string the service, how it should be written on a yaml file
    '''

    @abstractmethod
    def service_str_compose(self, workload_name: str, cluster_nodes, service: Service):
        pass

    '''
    Responsible to return the logs for all experiment's services
    '''

    @abstractmethod
    def get_workload_service_logs(self, workload_name: str):
        pass

    '''
    Responsible to check and return (before timing out) if the container is up and running
    '''

    @abstractmethod
    def container_wise_service_has_started(self, workload_name: str, service: Service):
        pass

    '''
    Responsible to check and return (before timing out) if the service has started
    '''

    @abstractmethod
    def application_wise_service_has_started(self, workload_name: str, service: Service):
        pass

    '''
    Sets up cluster by calling the appropriate method
    '''

    @abstractmethod
    def setup(self, list_of_images):
        self.setupOrchestrator.setup_cluster(list_of_images)
        
    @abstractmethod
    def get_node_proxy(self, node):
        return self.setupOrchestrator.get_node_proxy(node)
