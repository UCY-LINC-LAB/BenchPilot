import BenchPilotSDK.utils.benchpilotProcessor as bp
from datetime import datetime
from dataclasses import dataclass
from BenchPilotSDK.services.service import Service
from BenchPilotSDK.utils.exceptions import BenchExperimentInvalidException
from BenchPilotSDK.utils.experimentRecord import ExperimentRecord
from BenchPilotSDK.utils.loggerHandler import LoggerHandler
from BenchPilotSDK.utils.loader import Loader
from BenchPilotSDK.utils.benchpilotProcessor import convert_to_seconds, process_class_choice, check_required_parameters

list_of_available_workloads = ["MarketingCampaign", "Simple", "Mlperf", "Perfharpamap2"]
@dataclass
class Experiment:
    """
    The class represents the experiment abstract object
    """
    record_name: str
    duration: float
    workloads: []
    warm_up: str = "0m"
    repetition: int = 1
    idle_between_repetition: bool = False
    validity: bool = True
    record: ExperimentRecord = None
    delayed_workloads: [] = None

    def __post_init__(self):
        self.logger = LoggerHandler().logger
        required_attributes = ["record_name", "workloads"]
        check_required_parameters('experiment', required_attributes, self.__dict__)
        self.repetition = int(self.repetition)
        if not (type(self.duration) is str and "default" in self.duration):
            self.duration = convert_to_seconds(self.duration)
            if self.duration < 0:
                raise BenchExperimentInvalidException("Non Valid Duration Time")
        if not hasattr(self, "idle_between_repetition"):
            print("Idle Between Repetition is not valid, so it's set to 'False' by default")
            self.idle_between_repetition = False
        experiment_conf = {'record_name': self.record_name, 'duration': self.duration, 'repetition': self.repetition}
        workload_definition = self.workloads
        self.warm_up = bp.convert_to_seconds(self.warm_up)
        self.workloads = []
        self.delayed_workloads = []
        self.record = ExperimentRecord(experiment_conf)
        self.__setup_workloads(workload_definition)
        self.__check_experiment_validity()

    """
    Posts request to the client to submit job after every service is app and running.
    Please override in case of different implementation of workload.
    """

    def start_experiment(self, repetition_count):
        self.__orchestrate_workloads()
        self.record.experiment_started()
        self.started_timestamp = datetime.strptime(self.record.get_last_experiment_starting_timestamp(),
                                                   ExperimentRecord.fmt)
        self.loader = Loader(
            desc="-- Waiting to deploy the non-delayed workloads ..--", end="-- Workloads Deployed! (Started at: " + str(self.started_timestamp) + ") --").start()
        self.deploy_workloads()
        self.loader.stop()
        self.loader = Loader(
            desc="-- Waiting for experiment: " + self.record_name + " (" + str(repetition_count + 1) + "/" + str(
                self.repetition) + ") to finish .. --",
            end="-- Experiment " + self.record_name + " (" + str(repetition_count + 1) + "/" + str(
                self.repetition) + ") Finished! --").start()
        self.__wait_experiment_to_finish()
        self.record.experiment_finished()
        self.loader.stop()

    def stop_experiment(self):
        for workload in self.workloads:
            self.logger.debug("Stopping workload from experiment: " + workload.record_name)
            workload.stop_workload()

    def cleanup_experiment(self):
        for workload in self.workloads:
            print("cleanup for: " + workload.record_name)
            workload.orchestrator.delete_experiment_leftovers(workload.record_name)

    def clean_start(self):
        for workload in self.workloads:
            workload.rewind()
            workload.shutdown_all_services()

    def deploy_workloads(self, workloads: [] = None):
        deploy_non_delayed = False
        if workloads is None:
            workloads = self.workloads
            deploy_non_delayed = True
        for workload in workloads:
            if (workload.shift == 0) or (not deploy_non_delayed):
                workload.loader = self.loader
                workload.deploy()

    def __setup_workloads(self, workload_definitions: []):
        workload_count = 0
        for workload_definition in workload_definitions:
            check_required_parameters('workload', ["name"], workload_definition)
            workload_name = workload_definition["name"]
            record_name = self.record_name + "_" + workload_name + "_" + str(workload_count)
            workload_definition["record_name"] = record_name
            check_required_parameters('workload', ["name"], workload_definition)
            workload = process_class_choice(class_name=workload_name, class_type="workload", **workload_definition)
            workload.setup()
            workload.compose_orchestrator_file()
            workload_count += 1
            self.workloads.append(workload)

    def __check_experiment_validity(self):
        # check duration and check exposed ports
        exposed_ports = []
        for workload in self.workloads:
            for service in workload.services:
                if self.duration == "default" and workload.duration == "default" and len(service.service_finished_log) == 0:
                    # TODO: remove the print
                    print("Experiment duration: " + self.duration + " workload-duration: " + workload.name + "-" + workload.duration + " service: " + service.name)
                    LoggerHandler.coloredPrint(
                        "Experiment with record name: " + self.record_name + " is NOT valid due to not finding a way to finish. Please add a duration either to the experiment, or its workloads.")
                    self.validity = False
                    return
                if hasattr(service, "services"):
                    for inner_service in service.services:
                        if self.__if_service_has_port(inner_service):
                            exposed_ports.extend(inner_service.ports)
                if self.__if_service_has_port(service):
                    exposed_ports.extend(service.ports)

        if len(exposed_ports) > 0:
            unique_exposed_ports = dict((v['host_port'], v) for v in exposed_ports).values()
            if len(unique_exposed_ports) != len(exposed_ports):
                LoggerHandler.coloredPrint(
                    "Experiment with record name: " + self.record_name + " exposes same ports. Please choose for each workload different ports.")
                self.validity = False

    @staticmethod
    def __if_service_has_port(service: Service):
        return hasattr(service, "ports") and not (service.ports is None) and len(service.ports) > 0

    """
    Waits for experiment to finish, but in between checks if a workload needs to start (checking cold-start time)
    (sleep wait till the experiment duration has finished, if duration is default, then wait for workloads to finish)
    """

    def __wait_experiment_to_finish(self):
        experiment_finished = False
        is_default_duration = type(self.duration) is str and "default" in self.duration
        while not experiment_finished:
            if len(self.delayed_workloads) > 0:
                self.__manage_delayed_workloads()

            workloads_finished = 0
            for workload in self.workloads:
                if workload.started:
                    if workload.finished:
                        workloads_finished += 1
                    elif workload.has_workload_finished():
                        self.logger.debug("Workload " + workload.record_name + " has finished!!")
                        workload.declare_workload_as_finished()
                        workloads_finished += 1

            if (not is_default_duration) and self.__get_current_experiment_time() >= self.duration:
                experiment_finished = True

            elif workloads_finished == len(self.workloads):
                experiment_finished = True

        self.stop_experiment()

    def __manage_delayed_workloads(self):
        current_experiment_time = self.__get_current_experiment_time()
        current_workload_delay = self.delayed_workloads[0].shift
        is_it_time_to_deploy_workload = current_workload_delay <= current_experiment_time
        if is_it_time_to_deploy_workload:
            current_delayed_workloads = [self.delayed_workloads[0]]
            if len(self.delayed_workloads) > 1:
                for i in range(1, len(self.delayed_workloads)):
                    if self.delayed_workloads[i].shift == current_workload_delay:
                        current_delayed_workloads.append(self.delayed_workloads[i])
                        self.delayed_workloads.remove(self.delayed_workloads[i])
                        self.logger.info(
                            "Preparing to deploy delayed workload " + self.delayed_workloads[i].record_name)
            self.deploy_workloads(workloads=current_delayed_workloads)

    # returns the in seconds, the amount of time it has passed since the experiment has started
    def __get_current_experiment_time(self):
        now_timestamp = datetime.strptime(ExperimentRecord.get_timestamp(), ExperimentRecord.fmt)
        return int((now_timestamp - self.started_timestamp).total_seconds())

    # Find the workloads that need cold start and start them and stack them
    def __orchestrate_workloads(self):
        self.logger.info("Orchestrating Delayed Workloads..")
        for workload in self.workloads:
            if workload.shift != 0 and workload not in self.delayed_workloads:
                self.logger.info("Delayed: " + workload.record_name + " with delay: " + str(workload.shift))
                self.delayed_workloads.append(workload)
        self.delayed_workloads.sort(key=lambda x: x.shift)
