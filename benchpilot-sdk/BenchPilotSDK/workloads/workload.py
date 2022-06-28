import requests, time
from abc import abstractmethod
from sys import exit
from BenchPilotSDK.services.service import Service
from BenchPilotSDK.orchestrators.orchestratorFactory import OrchestratorFactory
from BenchPilotSDK.orchestrators.containerOrchestrator import ContainerOrchestrator
from BenchPilotSDK.utils.exceptions import MissingBenchExperimentAttributeException
from BenchPilotSDK.utils.workloadRecord import WorkloadRecord
from BenchPilotSDK.workloads.setup.workloadSetup import WorkloadSetup


class Workload:
    """
    The class represents the workload abstract object
    """
    name: str
    record_name: str
    repetition: int
    repetition_count: int
    duration: int
    parameters: {}
    cluster: {}
    services: [] = []
    orchestrator: ContainerOrchestrator
    path_to_dockerfile_worker: str
    workload_record: WorkloadRecord = WorkloadRecord()
    workload_setup: WorkloadSetup
    restarting_services: [] = []
    workload_timeout: int = 0
    # please change the url if you have added a new client with a different url
    workload_client_url: str
    # set the configuration that the client may have to update on its container for the workload
    workload_client_conf: [] = []

    def __init__(self, workload_yaml):
        if workload_yaml is None:
            raise MissingBenchExperimentAttributeException("workload")
        required_attributes = ["name", "record_name", "repetition", "duration", "cluster"]
        self.workload_setup = WorkloadSetup(workload_yaml)
        self.workload_setup.check_required_parameters('workload', required_attributes, workload_yaml)
        self.name = workload_yaml["name"]
        self.record_name = workload_yaml["record_name"]
        self.repetition = workload_yaml["repetition"]
        self.duration = workload_yaml["duration"]
        self.parameters = workload_yaml["parameters"]
        self.cluster = workload_yaml["cluster"]
        required_attributes = ["manager", "nodes"]
        self.workload_setup.check_required_parameters('cluster', required_attributes, self.cluster)
        self.services = []
        self.restarting_services = []
        self.nodes = self.cluster["nodes"]
        self.manager_ip = self.cluster["manager"]
        self.workload_client_url = 'http://' + self.manager_ip + ':5000/api/v1'
        orchestrator = self.cluster["orchestrator"] if "orchestrator" in self.cluster else None
        self.orchestrator = OrchestratorFactory(orchestrator, self.manager_ip, self.cluster).orchestrator
        self.workload_record = WorkloadRecord(workload_yaml)
        self.list_of_services_images = {'manager': [], 'worker': []}
        self.repetition_count = 0

    @abstractmethod
    def setup(self):
        self.workload_setup.setup(self.parameters)
        self.__iterate_services(self.__assign_list_of_images, None)
        self.orchestrator.setup(self.list_of_services_images)

    def __compose_yaml(self):
        if "http_proxy" in self.cluster:
            http_proxy = self.cluster["http_proxy"]
        else:
            http_proxy = ''
        https_proxy = http_proxy
        if "https_proxy" in self.cluster:
            https_proxy = self.cluster["https_proxy"]
        if len(http_proxy) > 0 or len(https_proxy) > 0:
            self.__iterate_services(self.__assign_proxy, [http_proxy, https_proxy])

        if len(self.nodes) > 0:
            self.placement_count = 0
            self.__iterate_services(self.__assign_placement, None)

        self.orchestrator.compose_yaml(self.services)

    def add_service(self, service: Service):
        self.services.append(service)

    @abstractmethod
    def deploy_services(self):
        if self.repetition_count == 0:
            self.orchestrator.deploy_services()
        elif len(self.restarting_services) > 0:
            for service in self.restarting_services:
                self.orchestrator.redeploy_service(service)

    """
    Posts request to the client to submit job after every service is app and running.
    Please override in case of different implementation of workload.
    """

    @abstractmethod
    def start_workload_job(self):
        # compose yaml and setup orchestrator only if it's the first workload's trial
        if self.repetition_count == 0:
            self.setup()
            self.__compose_yaml()
        self.deploy_services()
        self.__iterate_services(self.__check_containers_have_started, None)
        self.__iterate_services(self.__check_services_have_started, None)
        # todo: fill workload's parameters in json format
        parameters = {}
        if self.workload_timeout < 180:
            response = requests.post(self.workload_client_url, json=parameters)
            if response.status_code != 200:
                print("Workload client not running")
                exit()

            # check if workload has started
            if self.__workload_has_started() == -1:
                self.workload_timeout += 1
                self.start_workload_job()
                return

            self.__workload_wait_to_finish()
            self.repetition_count += 1
        else:
            print('Workload timeout')
            exit()

    @abstractmethod
    def __workload_has_started(self):
        sec_waiting = 0
        job_not_started = True
        while job_not_started:
            response = requests.get(self.workload_client_url)
            if "The workload hasn't started yet" in response.text:
                if sec_waiting < 180:
                    # wait for 1 sec and retry
                    print("Waiting 1 seconds to retry to check if workload has started")
                    time.sleep(1)
                    sec_waiting += 1
                else:
                    print("Workload timeout")
                    return -1
            else:
                print("Workload has started")
                return 0

    def __workload_wait_to_finish(self):
        workload_is_running = True
        self.workload_record.workload_started()

        while workload_is_running:
            response = requests.get(self.workload_client_url)
            if 'Workload still running' in response.text:
                continue
            else:
                workload_is_running = False
                print('Workload Finished')
                self.workload_record.workload_finished()

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

    def __check_containers_have_started(self, service: Service):
        if self.orchestrator.container_wise_service_has_started(service) == -1:
            exit()

    def __check_services_have_started(self, service: Service):
        if self.orchestrator.application_wise_service_has_started(service) == -1:
            exit()

    @staticmethod
    def __assign_proxy(service: Service, parameters: []):
        service.assign_proxy(parameters[0], parameters[1])

    def __assign_placement(self, service: Service):
        if service.needs_placement:
            node = self.orchestrator.setupOrchestrator.cluster_nodes[self.nodes[self.placement_count]]
            service.reassign_placement(self.nodes[self.placement_count])
            if "arm" in node["architecture"]:
                service.image_tag = service.image_arm_tag
            self.placement_count += 1
            if self.placement_count >= len(self.nodes):
                self.placement_count = 0

    def __assign_list_of_images(self, service: Service):
        placement = 'worker' if service.needs_placement else 'manager'
        image = {'name': service.image, 'tag': service.image_tag, 'arm_tag': service.image_arm_tag}
        if not(image in self.list_of_services_images[placement]):
            self.list_of_services_images[placement].append(image)
