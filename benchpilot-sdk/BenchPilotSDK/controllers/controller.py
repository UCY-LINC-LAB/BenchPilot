import os, yaml, os.path
from time import sleep
from BenchPilotSDK.utils.exceptions import *
from BenchPilotSDK.utils.loggerHandler import LoggerHandler
from BenchPilotSDK.utils.benchpilotProcessor import convert_to_seconds
from BenchPilotSDK.controllers.experiment import Experiment

class Controller(object):
    """
    The BenchPilot Controller, it acts also as a controller in an MVC architecture, handles user's experiments.
    """
    idle_between_experiments: float = 0
    experiments: []

    def __init__(self, bench_experiments_file: str = '', debug_mode: bool = False):
        benchpilot_path = os.environ["BENCHPILOT_PATH"] if "BENCHPILOT_PATH" in os.environ else '/'
        os.environ["BENCHPILOT_PATH"] = benchpilot_path
        os.environ["BENCHPILOT_DEBUG"] = "1" if debug_mode else "0"
        if len(bench_experiments_file) == 0:
            bench_experiments_file = benchpilot_path + 'BenchPilotSDK/conf/BenchPilot-experiments.yaml'
        settings_file = open(
            os.environ['EXPERIMENT_FILE'] if 'EXPERIMENT_FILE' in os.environ else bench_experiments_file, "r")
        try:
            configs = yaml.safe_load(settings_file)
        except yaml.YAMLError:
            raise BenchExperimentInvalidException()
        if not "experiments" in configs:
            raise MissingBenchExperimentAttributeException("The configuration file needs to have 'experiments'")
        if "idle_between_experiments" in configs:
            self.idle_between_experiments = convert_to_seconds(configs["idle_between_experiments"])
            if self.idle_between_experiments < 0:
                self.idle_between_experiments = 0
        self.experiment_conf = configs.get("experiments")
        self.experiments = []

    # Starts experiment one-by-one or a specific one by its name
    def start_experiment(self, experiment_record_name: str = None):
        LoggerHandler.coloredPrint("** Starting BenchPilot **")
        for i in range(0, len(self.experiment_conf)):
            experiment = self.experiment_conf[i]["experiment"]
            if experiment_record_name is None or (
                    not (experiment_record_name is None) and experiment["record_name"] == experiment_record_name):
                if not self.__experiment_record_name_is_unique(experiment["record_name"]):
                    LoggerHandler.coloredPrint("The experiment with record name: " + experiment["record_name"] + " is not unique, bypassing the second experiment..")
                    continue
                experiment = Experiment(**experiment)
                if experiment.validity:
                    self.experiments.append(experiment)
                    for j in range(0, experiment.repetition):
                        experiment.clean_start()
                        experiment.start_experiment(j)
                        if experiment.idle_between_repetition and self.idle_between_experiments > 0:
                            LoggerHandler.coloredPrint("** Sleeping for " + str(self.idle_between_experiments) + " **")
                            sleep(self.idle_between_experiments)
                    # let cluster nodes to cooldown
                    if self.idle_between_experiments > 0 and i < len(self.experiment_conf) - 1:
                        LoggerHandler.coloredPrint("** Sleeping for " + str(self.idle_between_experiments) + " **")
                        sleep(self.idle_between_experiments)
            else:
                continue
        
        # clean up compose files and their networks before exiting
        for experiment in self.experiments:
            experiment.cleanup_experiment()
        LoggerHandler.coloredPrint("** Thank you for choosing BenchPilot, bye! **")

    # returns all or specific experiment's records
    def get_experiment_records(self, experiment_record_name: str = None, logs: bool = False):
        experiment_record_history = []
        for experiment in self.experiments:
            if experiment_record_name is None or (
                    not (experiment_record_name is None) and experiment.record_name == experiment_record_name):
                experiment_record = {
                    experiment.record_name: experiment.record.get_experiment_record_in_json(logs, experiment.workloads)
                }
                experiment_record_history.append(experiment_record)
        return experiment_record_history

    def print_experiment_logs(self, experiment_record_name: str = ""):
        for experiment in self.experiments:
            if experiment_record_name == "" or (
                    not (experiment_record_name is None) and experiment.record_name == experiment_record_name):
                LoggerHandler.coloredPrint("-- Experiment " + experiment_record_name + " Logs --")
                for trial in range(0, int(experiment.repetition)):
                    LoggerHandler.coloredPrint("-- Trial " + str(trial) + "/" + str(experiment.repetition) + " --")
                    for workload in experiment.workloads:
                        workload.record.print_logs(trial)

    def export_benchmark_metadata(self, path: str = "./benchpilot_experiments.json", logs: bool = False):
        experiments = self.get_experiment_records(None, logs)
        experiments = {'experiments': experiments}

        import json
        with open(path, 'w') as f:
            json.dump(experiments, f)
        LoggerHandler.coloredPrint("** Successfully Exported Experiment Metadata **")

    def __experiment_record_name_is_unique(self, experiment_record_name: str):
        for experiment in self.experiments:
            if experiment_record_name == experiment.record_name:
                return False
        return True
