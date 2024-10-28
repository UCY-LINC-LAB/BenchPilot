import copy
from abc import ABC
import BenchPilotSDK.utils.benchpilotProcessor as bp
from BenchPilotSDK.utils.exceptions import BenchExperimentInvalidException
from BenchPilotSDK.workloads.workload import Workload
from BenchPilotSDK.services.materializedServices.iperf3 import IPerf3
from BenchPilotSDK.services.materializedServices.stress import Stress


class Simple(Workload, ABC):
    """
    This class represents the Simple Workload, it just creates a specific simple service.
    Please add in the if-case any services you would like to run.
    """

    def __init__(self, **workload_definition):
        super().__init__(**workload_definition)
        bp.check_required_parameters('workload > parameters', ["service"], workload_definition["parameters"])
        service = self.parameters["service"]
        options = {} if not "options" in self.parameters else self.parameters["options"]
        if service == "iperf3":
            service = IPerf3(options)
            service.assign_duration("0")
        elif service == "stress":
            service = Stress(options)
        else:
            raise BenchExperimentInvalidException("The simple service you defined is not supported")

        # append each service for each node
        for i in range(0, len(self.cluster)):
            new_service = copy.deepcopy(service)
            new_service.hostname = "simple_" + str(i)
            if "expose_ports" in self.parameters:
                ports = self.parameters["expose_ports"]
                new_service.ports = []
                for j in range(0, len(ports)):
                    for host_port in ports[j]:
                        container_port = ports[j][host_port]
                        new_service.add_port(container_port=container_port, host_port=host_port)
            self.add_service(new_service)

