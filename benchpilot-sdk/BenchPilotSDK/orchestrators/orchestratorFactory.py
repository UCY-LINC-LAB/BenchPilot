from BenchPilotSDK.orchestrators import *
from BenchPilotSDK.services.service import Service
from BenchPilotSDK.utils.exceptions import UnsupportedOrchestratorException


class OrchestratorFactory:
    """
    This class works as an orchestrators factory, trying to generalize the use of orchestrators.
    """
    orchestrator: ContainerOrchestrator

    def __init__(self, orchestrator: str = None, manager: str = None, cluster: list = []):
        if orchestrator is None or "swarm" in orchestrator.lower():
            self.orchestrator = DockerSwarmOrchestrator(manager, cluster)
        elif "kubernetes" in orchestrator.lower():
            raise UnsupportedOrchestratorException('This orchestrator is not supported yet')
        else:
            raise UnsupportedOrchestratorException('This orchestrator is not supported yet')

    # kubectl get deployments
    @staticmethod
    def application_wise_service_has_started(service: Service):
        pass
