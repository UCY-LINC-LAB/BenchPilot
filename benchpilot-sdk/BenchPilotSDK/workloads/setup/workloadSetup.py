import os
from abc import abstractmethod

from BenchPilotSDK.utils.exceptions import MissingBenchExperimentAttributeException


class WorkloadSetup(object):
    """
    The workloadSetup is responsible to set up the needed configuration files of a workload
    """
    cluster_dockerfile_path: str =os.environ["BENCHPILOT_PATH"]
    workload_client_path: str = os.environ["BENCHPILOT_PATH"] + "dockerized-benchmarks/workload-client/"

    def __init__(self, workload_yaml = None):
        self.workload_yaml = workload_yaml

    @abstractmethod
    def setup(self, parameters = None):
        self.update_workload_configuration(parameters)

    @abstractmethod
    def update_workload_configuration(self, parameters):
        # TODO override depending on the workload when rebuilding image
        pass

    @staticmethod
    def check_required_parameters(main_attribute, required_attributes, yaml):
        for att in required_attributes:
            if not att in yaml:
                raise MissingBenchExperimentAttributeException(main_attribute + "> " + att)
