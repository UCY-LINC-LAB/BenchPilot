from abc import abstractmethod


class WorkloadSetup(object):
    """
    The workloadSetup is responsible to set up the needed configuration files of a workload
    """
    workload_client_path: str = "/workload-client/"

    @staticmethod
    @abstractmethod
    def update_workload_configuration(parameters):
        # TODO override depending on the workload
        pass
