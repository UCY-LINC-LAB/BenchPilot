from abc import ABC
from dataclasses import dataclass
from BenchPilotSDK.orchestrators.containerOrchestrator import ContainerOrchestrator
from BenchPilotSDK.orchestrators.materializedOrchestrators.setupSwarmOrchestrator import SetupSwarm
from BenchPilotSDK.services.service import Service
from BenchPilotSDK.utils.exceptions import WorkloadDeployTimeOut
from BenchPilotSDK.utils.loggerHandler import LoggerHandler
import BenchPilotSDK.utils.benchpilotProcessor as bp
import os, time


@dataclass
class Swarm(ContainerOrchestrator, ABC):
    """
    The containerOrchestrator is responsible to orchestrate the deployment. As for now
    it only supports Docker Swarm, but in the future we will extend it for Kubernetes as well.
    """
    compose_version: str = "3.3"
    cluster: dict = None

    def __post_init__(self):
        super().__post_init__()
        self.setupOrchestrator = SetupSwarm(self.cluster)
        self.commands = self.setupOrchestrator.commands
        self.timeout_wait = 2
        self.name = "Docker Swarm"

    def deploy_workload(self, workload_name: str):
        get_workload_network = bp.pipeline_kernel_commands([self.commands["get_networks"], "grep " + workload_name])
        network_exists = bp.pipeline_kernel_commands([get_workload_network, "wc -l"])
        result = bp.kernel_run(network_exists, get_output=True)
        create_network = bp.unite_kernel_commands([self.commands["network_create"], workload_name])

        if int(result) == 1:
            is_overlay = bp.pipeline_kernel_commands([get_workload_network, bp.get_nth_attribute_kernel_command(["3"])])
            result = bp.kernel_run(is_overlay, get_output=True)

            if not ("overlay" in str(result)):
                remove_existing_network = bp.unite_kernel_commands([self.commands["network_rm"], workload_name])
                command = bp.unite_kernel_commands([remove_existing_network, "&&", create_network])
                bp.kernel_run(command)
        else:
            bp.kernel_run(create_network, get_output=True)
        compose_file = self.compose_path + workload_name + ".yaml"
        deploy_workload_cmd = bp.unite_kernel_commands([self.commands["deploy"], compose_file, workload_name])
        bp.kernel_run(deploy_workload_cmd, get_output=True)
        # check if benchpilot client was already attached
        check_network_attached = bp.pipeline_kernel_commands([self.commands["network_inspect"] + " " + workload_name, "grep " + self.commands["benchPilot_cli_id"], "wc -l"])

        # attach benchpilot client to the benchmarks' network
        if int(bp.kernel_run(check_network_attached, get_output=True)) <= 0:
            attach_cli_command = bp.unite_kernel_commands(
                [self.commands["network_connect"], workload_name, self.commands["benchPilot_cli_id"]])
            bp.kernel_run(attach_cli_command)

    def undeploy_workload(self, workload_name: str):
        get_running_stacks = bp.unite_kernel_commands(
            [self.commands["get_stacks"], self.setupOrchestrator.orchestrator_format_command(["Name"])])
        stacks = bp.kernel_run(get_running_stacks, process_output=True)
        for stack in stacks:
            if workload_name == stack:
                rm_stack = bp.unite_kernel_commands([self.commands["stack_rm"], workload_name])
                bp.kernel_run(rm_stack)
                time.sleep(0.5)
                return

    def delete_experiment_leftovers(self, workload_name: str):
        get_workload_network = bp.pipeline_kernel_commands([self.commands["get_networks"], "grep " + workload_name])
        network_exists = bp.pipeline_kernel_commands([get_workload_network, "wc -l"])
        result = bp.kernel_run(network_exists, get_output=True)
        if int(result) == 1:
            rm_network = bp.unite_kernel_commands(
            [self.commands["network_disconnect"], workload_name, self.commands["benchPilot_cli_id"], "&&",
                self.commands["network_rm"], workload_name])
            # TODO: check why this doesn't work
            bp.kernel_run(rm_network)
        bp.kernel_run("rm " + self.compose_path + workload_name + ".yaml")

    def wait_workload_to_finish(self, workload_name: str, services: [], return_state: bool = False):
        get_stack_services = bp.unite_kernel_commands([self.commands["stack_services"], workload_name,
                                                       self.setupOrchestrator.orchestrator_format_command(["Name"])])
        service_names = bp.kernel_run(get_stack_services, process_output=True)
        if "Nothing found in stack" in service_names:
            return True
        for service_deployment_name in service_names:
            service_name = service_deployment_name.split(workload_name + "_")[1]
            for service in services:
                workload_service_name = service.hostname if service.name is None else service.name
                # if service has been deployed
                if workload_service_name == service_name:
                    service_finished = False
                    failed_service_count = bp.unite_kernel_commands(
                        [self.commands["stack_service_status"], service_deployment_name,
                         self.setupOrchestrator.orchestrator_format_command(["CurrentState"])])
                    failed_service_count = bp.pipeline_kernel_commands([failed_service_count, "grep Failed", "wc -l"])
                    while not service_finished:
                        service_finished = self.__is_service_still_running(service, service_deployment_name,
                                                                           failed_service_count)
                        if return_state:
                            return service_finished
                    return

    def __is_service_still_running(self, service, service_deployment_name, failed_service_count):
        service_finished = False
        # if it failed more than three times to start
        if int(bp.kernel_run(failed_service_count, get_output=True)) > 3:
            # declare that the workload has finished
            service.failed = service_finished = True
            LoggerHandler.coloredPrint(color_level="secondary",
                                       msg="-- Warning: the service '" + service_deployment_name +
                                           "' has failed to deploy on node '" + service.placement + "'. --")
            # remove service if it failed
            rm_service = bp.unite_kernel_commands([self.commands["service_rm"], service_deployment_name])
            bp.kernel_run(rm_service)
        else:
            get_logs = bp.unite_kernel_commands([self.commands["service_logs"], service_deployment_name, "--raw"])
            service_log = str(bp.kernel_run(get_logs, get_output=True)).lower()
            if hasattr(service, "service_finished_log") and len(
                    service.service_finished_log) > 0 and service.service_finished_log.lower() in service_log.lower():
                service_finished = True
        return service_finished

    def get_workload_service_logs(self, workload_name: str):
        service_logs = []
        get_services = bp.unite_kernel_commands([self.commands["stack_services"], workload_name,
                                                 self.setupOrchestrator.orchestrator_format_command(["Name"])])
        services = bp.kernel_run(get_services, process_output=True)

        if len(services) == 1 and "Nothing found in stack:" in services[0]:
            return []
        for service in services:
            get_service_logs = bp.unite_kernel_commands([self.commands["service_logs"], service, "--raw"])
            stack_service_logs = bp.kernel_run(get_service_logs, get_output=True)
            service_log = {service: str(stack_service_logs).replace('b\'', '').replace('\'', '').replace('\\n', '\n')}
            service_logs.append(service_log)
        return service_logs

    def compose_orchestrator_file(self, services: [], compose_file_name: str, workload_name: str):
        if compose_file_name is None or len(compose_file_name) <= 0:
            compose_file_name = "docker-compose.yaml"
        compose_file_name = self.compose_path + compose_file_name
        # delete existing docker-compose file (if exists) and create a new one with the needed services
        if os.path.exists(compose_file_name):
            os.remove(compose_file_name)

        if not compose_file_name in self.compose_files:
            self.compose_files.append(compose_file_name)

        prefix = "version: '" + self.compose_version + "'\nservices:"
        suffix = "networks:\n  " + workload_name + ":\n    external: true"
        with open(compose_file_name, 'w+') as outfile:
            services_str = prefix
            for service in services:
                # check if service has other services inside:
                if hasattr(service, "services"):
                    inner_services_str = ""
                    for inner_service in service.services:
                        inner_services_str += self.service_str_compose(workload_name,
                                                                       self.setupOrchestrator.cluster_nodes,
                                                                       inner_service)
                    services_str += inner_services_str
                else:
                    services_str += self.service_str_compose(workload_name, self.setupOrchestrator.cluster_nodes,
                                                             service)
            services_str += suffix
            outfile.write(services_str)
        outfile.close()

    def service_str_compose(self, workload_name: str, cluster_nodes, service: Service):
        # Declare IMAGE, HOSTNAME and RESTART conf
        name = service.hostname if service.name is None else service.name
        string = "\n\n# " + name.upper() + "\n  " + name + ":"
        architecture = ""
        if not "manager" == service.placement:
            architecture = cluster_nodes[service.placement]["architecture"]
        service_as_dict = service.get_service_definition(architecture)
        for att in service_as_dict:
            if (len(service_as_dict[att]) > 0) and (not service_as_dict[att] is None) and (str(service_as_dict[att]) != "") and (str(service_as_dict[att]) != "\"\""):
                string += "\n    " + att + ":"
                if type(service_as_dict[att]) is list:
                    string += "\n"
                    for i in range(0, len(service_as_dict[att])):
                        string += "      "
                        if not "environment" == att:
                            string += "- "
                        string += service_as_dict[att][i]
                        if i < len(service_as_dict[att]) - 1:
                            string += "\n"
                else:
                    string += " " + str(service_as_dict[att])
        string += "\n    networks: \n      - " + workload_name
        string += "\n    " + "deploy:" + "\n      " + "placement:" + "\n        " + "constraints:\n"
        # Declare DEPLOYMENT
        placement = "node.role"
        if not "manager" in service.placement:
            placement = "node.hostname"
        placement += "==" + service.placement
        string += "          - " + placement + "\n"
        return string

    def container_wise_service_has_started(self, workload_name: str, service: Service):
        logger = LoggerHandler().logger
        # initialize seconds of waiting
        service.sec_waiting = 0
        container_name = service.hostname if service.name is None else service.name
        container_deployment_name = workload_name + "_" + container_name
        waiting_msg = " Waiting to check if " + container_deployment_name + " has started "
        timeout_msg = " Docker Swarm Service: " + container_deployment_name + " timeout "
        while service.container_service_has_not_started:
            get_containers = bp.unite_kernel_commands([self.commands["stack_services"], workload_name,
                                                       self.setupOrchestrator.orchestrator_format_command(
                                                           ["Name", "Replicas"])])
            containers = bp.kernel_run(get_containers, process_output=True)
            if "Nothing found in stack:" in containers[0]:
                continue

            service_restarted = bp.unite_kernel_commands(
                [self.commands["stack_service_status"], container_deployment_name,
                 self.setupOrchestrator.orchestrator_format_command(["CurrentState"])])
            count_service_restarted = bp.pipeline_kernel_commands([service_restarted, "wc -l"])
            for container in containers:
                split_container = container.split(" ")
                container_has_started = (container_name in split_container[0] and "1/1" == split_container[1]) or (int(
                    bp.kernel_run(count_service_restarted, process_output=True)[0]) > 0)
                if container_has_started:
                    service.container_service_has_not_started = False
                elif service.sec_waiting < 240:
                    # wait for 1 sec and retry
                    logger.info(waiting_msg)
                    time.sleep(self.timeout_wait)
                    service.sec_waiting += self.timeout_wait
                else:
                    logger.error(timeout_msg)
                    raise WorkloadDeployTimeOut()
        logger.info("Docker Swarm Service: %s has been deployed" % container_name)

    def application_wise_service_has_started(self, workload_name: str, service: Service):
        logger = LoggerHandler().logger
        # initialize seconds of waiting
        service.sec_waiting = 0
        service_name = service.hostname if service.name is None else service.name
        service_deployment_name = workload_name + "_" + service_name
        while service.application_service_has_not_started:
            get_logs = bp.unite_kernel_commands([self.commands["service_logs"], service_deployment_name, "--raw"])
            logs = bp.kernel_run(get_logs, get_output=True)
            if service.service_started_log in str(logs):
                service.application_service_has_not_started = False
            elif service.sec_waiting < 180:
                # wait for 1 sec and retry
                logger.info("Waiting 1 seconds to retry to check if application %s has started" % service_name)
                time.sleep(3)
                service.sec_waiting += 1
            else:
                logger.error("Service: %s timeout" % service_name)
                raise WorkloadDeployTimeOut()
        logger.info("Application: %s has started" % service_name)
