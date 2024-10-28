from datetime import datetime
from BenchPilotSDK.utils.loggerHandler import LoggerHandler

timestamp_format: str = "%Y-%m-%dT%H:%M:%SZ"


def get_current_timestamp():
    now = datetime.now()
    now = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    return now


class ExperimentRecord(object):
    """
    This class holds for each experiment its start times, end times and configurations.
    The timestamp that its stored is in the same format that Prometheus Pandas receives.
    """
    startTime: []
    endTime: []
    fmt: str = timestamp_format

    @staticmethod
    def get_timestamp():
        return get_current_timestamp()

    def __init__(self, experiment_conf=None):
        if experiment_conf is None:
            experiment_conf = {}
        self.experiment_conf = experiment_conf
        self.startTime = []
        self.endTime = []

    def experiment_started(self):
        self.startTime.append(ExperimentRecord.get_timestamp())

    def get_last_experiment_starting_timestamp(self):
        return self.startTime[-1]

    def experiment_finished(self):
        self.endTime.append(ExperimentRecord.get_timestamp())

    def get_experiment_record_in_json(self, logs: bool = False, workloads: [] = []):
        experiment_record = []
        for trial in range(0, len(self.endTime)):
            workload_records_in_json = []
            for workload in workloads:
                workload_records_in_json.append(workload.record.get_workload_record_in_json(trial=trial, logs=logs))
            trial_record = {
                'trial_id': trial,
                'starting_timestamp': self.startTime[trial],
                'ending_timestamp': self.endTime[trial],
                'workload_records': workload_records_in_json
            }
            experiment_record.append(trial_record)
        return {'experiment_record': experiment_record, 'experiment_conf': self.experiment_conf}

    def print_configs(self):
        print(self.experiment_conf)


class WorkloadRecord(object):
    """
    This class holds for each workload its start times, end times and configurations.
    The timestamp that its stored is in the same format that Prometheus Pandas receives.
    """
    workload_name: str
    startTime: []
    endTime: []
    workload_conf: {}
    workload_logs: []
    fmt: str = timestamp_format

    def __init__(self, workload_name: str = None, workload_conf=None):
        self.workload_name = workload_name
        if workload_conf is None:
            workload_conf = {}
        self.workload_conf = workload_conf
        self.startTime = []
        self.endTime = []
        self.workload_logs = []

    @staticmethod
    def get_timestamp():
        return get_current_timestamp()

    def get_last_start_time(self):
        return self.startTime[-1]

    def workload_started(self):
        self.startTime.append(self.get_timestamp())

    def workload_finished(self):
        self.endTime.append(self.get_timestamp())

    def append_logs(self, service_logs: []):
        self.workload_logs.append(service_logs)

    def print_logs(self, trial: int = 0):
        LoggerHandler.coloredPrint("== Workload: " + self.workload_name + " ==")
        for service in self.workload_logs[trial]:
            service_name = list(service.keys())[0]
            service_value = list(service.values())[0]
            LoggerHandler.coloredPrint("-- Service: " + service_name + " logs --")
            print(service_value.replace("\\n", "\n").replace("b\"", "").replace("\"", ""))

    def get_workload_record_in_json(self, trial: int = 0, logs: bool = False):
        if trial > len(self.startTime) - 1:
            workload_record = {}
        else:
            workload_record = {
                'starting_timestamp': self.startTime[trial],
                'ending_timestamp': self.endTime[trial]
            }
        if logs:
            workload_record["logs"] = self.workload_logs[trial]
        return {self.workload_name: {'workload_record': workload_record, 'workload_conf': self.workload_conf}}

    def print_configs(self):
        print(self.workload_conf)
