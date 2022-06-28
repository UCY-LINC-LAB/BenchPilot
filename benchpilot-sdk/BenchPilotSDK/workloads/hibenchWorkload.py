from BenchPilotSDK.workloads.sdpeWorkload import SDPEWorkload
from BenchPilotSDK.services.kafka import Kafka
from BenchPilotSDK.services.zookeeper import Zookeeper


class Hibench(SDPEWorkload):
    """
    This class represents Hibench Workload, it holds all of the extra needed services.
    - by extra we mean the services that are not SDPEs
    """

    def __init__(self, workload_yaml):
        super().__init__(workload_yaml, "hibench")
        self.services.append(Zookeeper())
        kafka = Kafka(len(self.nodes), self.manager_ip)
        self.services.append(kafka)
        self.restarting_services.append(kafka)
