import json
from abc import abstractmethod


class WorkloadClient:
    def __init__(self, logger):
        self.logger = logger
        self.setup = WorkloadSetup()
        self.workload_record: [] = []
        self.running_json = json.dumps({'status': 'success', 'message': 'Job still running'}), 200, {
            'ContentType': 'application/json'}
        self.no_running_json = json.dumps({'status': 'success', 'message': 'No job is currently running'}), 200, {
            'ContentType': 'application/json'}

    @staticmethod
    @abstractmethod
    def is_job_still_running():
        pass

    @staticmethod
    @abstractmethod
    def get_workload_collected_info(name):
        pass

    @abstractmethod
    def start_workload(self, name, request_body):
        pass

    @staticmethod
    @abstractmethod
    def stop_workload():
        pass


class WorkloadSetup(object):
    """
    The workloadSetup is responsible to set up the needed configuration files of a workload
    """
    workload_client_path: str = "/workload-client/"

    @staticmethod
    @abstractmethod
    def update_workload_configuration(parameters):
        # override depending on the workload
        pass
