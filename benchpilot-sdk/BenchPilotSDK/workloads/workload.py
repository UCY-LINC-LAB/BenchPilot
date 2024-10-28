import os
import BenchPilotSDK.utils.benchpilotProcessor as bp
from abc import abstractmethod
from time import sleep
from datetime import datetime
from dataclasses import dataclass
from BenchPilotSDK.services.service import Service
from BenchPilotSDK.utils.loggerHandler import LoggerHandler
from BenchPilotSDK.utils.experimentRecord import WorkloadRecord
from BenchPilotSDK.utils.exceptions import BenchExperimentInvalidException


@dataclass
class Workload:
    """
    The class represents the workload abstract object
    """
    name: str
    record_name: str
    cluster: {}
    duration: str = "default"
    shift: str = "0m"
    parameters: {} = None
    logger = LoggerHandler().logger
    orchestrator: str = "swarm"
    workload_timeout: int = 0
    started: bool = False
    finished: bool = False
    retrieved_logs: bool = False
    started_time: datetime = ""
    warm_up: str = "0m"

    """
    Abstract class for parameters. Override it depending on the workload's parameters.
    """

    @dataclass
    class Parameters:
        pass

    def __post_init__(self):
        self.logger = LoggerHandler().logger
        self.services = []
        self.workload_timeout = 0
        self.started = False
        self.finished = False
        self.retrieved_logs = False
        if self.parameters is None:
            self.parameters = {}
        # assigning cluster parameters
        self.__assign_cluster_parameters()
        if not "default" in self.duration:
            self.duration = bp.convert_to_seconds(self.duration)
            if int(self.duration) < 0:
                raise BenchExperimentInvalidException("Non Valid Duration Time")
        self.shift = bp.convert_to_seconds(self.shift)
        self.warm_up = bp.convert_to_seconds(self.warm_up)
        if int(self.shift) < 0:
            raise BenchExperimentInvalidException("Non Valid Cold Start Time")
        workload_conf = {'workload_name': self.name, 'duration': self.duration, 'shift': self.shift,
                         'parameters': self.parameters, 'cluster': self.cluster, 'orchestrator': self.orchestrator.name}
        self.record = WorkloadRecord(self.record_name, workload_conf)
        self.list_of_services_images = {'manager': [], 'worker': []}

    def __assign_cluster_parameters(self):
        params = {"cluster": self.cluster}
        self.orchestrator = bp.process_class_choice(class_name=self.orchestrator, class_type="orchestrator", **params)
        self.manager_ip = os.environ["MANAGER_IP"]

    # sets the workload up, and then calls the orchestrator to set up the cluster
    @abstractmethod
    def setup(self):
        self.__iterate_services(self.__assign_list_of_images, None)
        LoggerHandler.coloredPrint("-- Initiating BenchPilot Setup Process For Workload: " + self.record_name + " --")
        print(
            '(This process usually consists of installing docker, docker images and setting up the needed orchestrator)')
        print("It may take some time so please wait..")
        self.orchestrator.setup(self.list_of_services_images)

    def rewind(self):
        self.started = self.finished = self.retrieved_logs = False

    def add_duration(self, duration):
        self.duration += bp.convert_to_seconds(duration)

    # adds a service to its service list
    def add_service(self, service: Service):
        self.services.append(service)

    # shutdowns all of its services through its orchestrator
    def shutdown_all_services(self):
        self.orchestrator.undeploy_workload(self.record_name)

    # composes orchestrator file through the orchestrator
    def compose_orchestrator_file(self):
        self.__prepare_for_compose()
        self.orchestrator.compose_orchestrator_file(self.services, self.record_name + ".yaml", self.record_name)

    # deploys workload through its orchestrator, checks if the workload has started, submits it, and declares that it has start, then wait to finish.
    def deploy(self):
        if not self.started:
            self.orchestrator.deploy_workload(self.record_name)
            self.__iterate_services(self.__check_containers_have_started, None)
            self.__iterate_services(self.__check_services_have_started, None)
            self.submit_workload()
            self.record.workload_started()
            self.started_time = datetime.strptime(self.record.get_last_start_time(), WorkloadRecord.fmt)
            self.started = True

    def retrieve_logs(self):
        self.retrieved_logs = True
        self.record.append_logs(self.orchestrator.get_workload_service_logs(self.record_name))

    # declares the workload has finished and appends to the record its service logs
    def declare_workload_as_finished(self):
        self.logger.debug("Declaring workload as finished " + self.record_name)
        if not self.finished:
            self.record.workload_finished()
            self.finished = True
            if not self.retrieved_logs:
                self.retrieve_logs()
            self.logger.info('Workload Finished')

    # Abstract method of submitting workload, in this generic implementation we assume that the workload has started from the minute it has been deployed
    @abstractmethod
    def submit_workload(self):
        pass

    # Sleeps or checks that the workload is running properly. When it finishes, it declares it as finished.
    def wait_workload_to_finish(self):
        if type(self.duration) is str and "default" in self.duration:
            self.orchestrator.wait_workload_to_finish(workload_name=self.record_name, services=self.services,
                                                      return_state=False)
            self.declare_workload_as_finished()
        else:
            sleep(int(self.duration))
            self.stop_workload()

    def has_workload_finished(self):
        if type(self.duration) is str and "default" in self.duration:
            return self.orchestrator.wait_workload_to_finish(workload_name=self.record_name, services=self.services,
                                                             return_state=True)
        else:
            now_timestamp = datetime.strptime(WorkloadRecord.get_timestamp(), WorkloadRecord.fmt)
            current_experiment_time = int((now_timestamp - self.started_time).total_seconds())
            if current_experiment_time >= int(self.duration):
                self.logger.debug("Stopping Workload after: " + str(self.duration) + "s, with name: " + self.record_name)
                self.stop_workload()
                return True
        return False

    # Stops the workload, firstly, it un-deploys it, and then declares that it's finished.
    def stop_workload(self):
        self.logger.debug("Stopping workload from workload: " + self.record_name)
        if not self.retrieved_logs:
            self.retrieve_logs()
        self.orchestrator.undeploy_workload(self.record_name)
        self.declare_workload_as_finished()

    # Generic method of iterating workload's services
    def __iterate_services(self, function_to_call, parameters):
        for workload_service in self.services:
            if hasattr(workload_service, "services"):
                for service in workload_service.services:
                    if not parameters is None:
                        function_to_call(service, parameters)
                    else:
                        function_to_call(service)
            else:
                if not parameters is None:
                    function_to_call(workload_service, parameters)
                else:
                    function_to_call(workload_service)

    # Creates a list of images in order for the orchestrator to pull them on the appropriate cluster devices
    def __assign_list_of_images(self, service: Service):
        placement = 'worker' if service.needs_placement else 'manager'
        if not (service.image in self.list_of_services_images[placement]):
            self.list_of_services_images[placement].append(service.image)

    # Checks if the services have been deployed based on the orchestrator's output
    def __check_containers_have_started(self, service: Service):
        self.orchestrator.container_wise_service_has_started(service=service, workload_name=self.record_name)

    # Checks if the services have been deployed, application-wise, based on the orchestrator's output
    def __check_services_have_started(self, service: Service):
        self.orchestrator.application_wise_service_has_started(service=service, workload_name=self.record_name)

    # Assigns the proxy declaration in case of having a proxy in the network.
    def __assign_proxy(self, service: Service):
        service.assign_proxy(self.orchestrator.get_node_proxy(service.placement))

    # Assigns placement statement based on the workloads to each service and their according image.
    def __assign_placement(self, service: Service):
        node = "manager"
        if service.needs_placement:
            if self.cluster[self.placement_count] != "manager":
                node = self.orchestrator.setupOrchestrator.cluster_nodes[self.cluster[self.placement_count]]
                service.reassign_placement(self.cluster[self.placement_count])
                if "arm" in node["architecture"]:
                    service.image_tag = service.image["arm_tag"]
            self.placement_count += 1
            if self.placement_count >= len(self.cluster):
                self.placement_count = 0
        self.__assign_proxy(service)

    # It's called in order to prepare for composing the orchestration file. Specifically assigns proxy and placement parameters
    def __prepare_for_compose(self):
        if len(self.cluster) > 0:
            self.placement_count = 0
            self.__iterate_services(self.__assign_placement, None)
