import json
from abc import abstractmethod

from workloads.setup.workloadSetup import WorkloadSetup


class WorkloadClient:
    def __init__(self):
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
    def get_workload_collected_info(timestamp):
        pass

    @abstractmethod
    def start_workload(self, starting_timestamp, request_body):
        pass

    @staticmethod
    @abstractmethod
    def stop_workload():
        pass
