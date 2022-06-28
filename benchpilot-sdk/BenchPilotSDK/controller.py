import os, yaml
from BenchPilotSDK.workloads.workloadFactory import WorkloadFactory
from BenchPilotSDK.utils.exceptions import *


class Controller(object):
    """
    The BenchPilot Controller, it acts also as a controller in an MVC architecture, handles user's experiments.
    """
    workload_factory: WorkloadFactory
    workloads: []

    def __init__(self, bench_experiments_file: str):
        benchpilot_path = os.environ["BENCHPILOT_PATH"] if "BENCHPILOT_PATH" in os.environ else '/'
        os.environ["BENCHPILOT_PATH"] = benchpilot_path
        if len(bench_experiments_file) == 0:
            bench_experiments_file = benchpilot_path + 'BenchPilotSDK/conf/bench-experiments.yaml'
        settings_file = open(os.environ['EXPERIMENT_FILE'] if 'EXPERIMENT_FILE' in os.environ else bench_experiments_file, "r")
        try:
            configs = yaml.safe_load(settings_file)
        except yaml.YAMLError:
            raise BenchExperimentInvalidException()
        if not "experiments" in configs:
            raise MissingBenchExperimentAttributeException("The configuration file needs to have 'experiments'")
        self.experiments = configs.get("experiments")
        self.file = benchpilot_path + "BenchPilotSDK/conf/docker-compose.yaml"
        self.workloads = []

    # Starts experiment one-by-one or a specific one by its name
    def start_experiment(self, workload_record_name: str = None):
        for i in range(0, len(self.experiments)):
            experiment = self.experiments[i]["workload"]
            if workload_record_name is None or (
                    not (workload_record_name is None) and experiment["record_name"] == workload_record_name):
                workload = WorkloadFactory(experiment).workload
                self.workloads.append(workload)
                for j in range(0, experiment["repetition"]):
                    workload.start_workload_job()
            else:
                continue

    # returns all or specific experiment's timestamps
    def get_experiment_timestamps(self, workload_record_name: str = None):
        workload_record_history = []
        for workload in self.workloads:
            if workload_record_name is None or (
                    not (workload_record_name is None) and workload.record_name == workload_record_name):
                workload_record = {
                    'workload_record_name': workload.record_name,
                    'workload_record': workload.workload_record.get_starting_ending_timestamps()
                }
                workload_record_history.append(workload_record)
        return workload_record_history

    @staticmethod
    def check_required_parameters(main_attribute, required_attributes, yaml):
        for att in required_attributes:
            if not att in yaml:
                raise MissingBenchExperimentAttributeException(main_attribute + " " + att)
