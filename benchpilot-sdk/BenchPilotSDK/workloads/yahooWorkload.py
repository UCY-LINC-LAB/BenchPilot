from abc import ABC

from BenchPilotSDK.workloads.sdpeWorkload import SDPEWorkload
from BenchPilotSDK.services.kafka import Kafka
from BenchPilotSDK.services.redis import Redis
from BenchPilotSDK.services.zookeeper import Zookeeper
from BenchPilotSDK.workloads.setup.yahooWorkloadSetup import YahooWorkloadSetup


class Yahoo(SDPEWorkload, ABC):
    """
    This class represents Yahoo Streaming Benchmark, it holds all of the extra needed services.
    - by extra we mean the services that are not DSPEs
    """

    def __init__(self, workload_yaml):
        super().__init__(workload_yaml, "marketing-campaign")
        self.services.append(Zookeeper())
        kafka = Kafka(len(self.nodes), self.manager_ip)
        self.services.append(kafka)
        self.restarting_services.append(kafka)
        redis = Redis()
        self.services.append(redis)
        self.restarting_services.append(redis)
        self.workload_setup = YahooWorkloadSetup(workload_yaml)
