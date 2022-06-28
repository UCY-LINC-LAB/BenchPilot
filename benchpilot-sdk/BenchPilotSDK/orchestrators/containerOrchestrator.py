from abc import abstractmethod
from BenchPilotSDK.services.service import Service
from BenchPilotSDK.orchestrators.setup.setupOrchestrator import SetupOrchestrator


class ContainerOrchestrator:
    """
    The containerOrchestrator is responsible to orchestrate the deployment. As for now
    it only supports Docker Swarm, but in the future we will extend it for Kubernetes as well.
    """

    def __init__(self, manager: str = None, cluster: list = []):
        # define the specific setup class for each orchestrator
        self.setupOrchestrator = SetupOrchestrator(manager, cluster)

    # responsible to deploy the services after they have been composed in a yaml file
    @staticmethod
    @abstractmethod
    def deploy_services():
        pass

    # responsible to redeploy a specific service
    @staticmethod
    @abstractmethod
    def redeploy_service(service: Service):
        pass

    # responsible to compose - write in a yaml file the deployable services
    @abstractmethod
    def compose_yaml(self, services: Service):
        pass

    # responsible to return as a string the service, how it should be written on a yaml file
    @staticmethod
    @abstractmethod
    def service_str_compose(cluster_nodes, service: Service):
        pass

    # responsible to check and return (before timing out) if the container is up and running
    @staticmethod
    @abstractmethod
    def container_wise_service_has_started(service: Service):
        pass

    # responsible to check and return (before timing out) if the service has started
    @staticmethod
    @abstractmethod
    def application_wise_service_has_started(service: Service):
        pass

    @abstractmethod
    def setup(self, list_of_images):
        self.setupOrchestrator.setup_cluster(list_of_images)
