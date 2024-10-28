import inspect
from abc import ABC
from dataclasses import dataclass, asdict
from BenchPilotSDK.workloads.materializedWorkloads.sdpeWorkload import SDPEWorkload
from BenchPilotSDK.services.materializedServices.kafka import Kafka
from BenchPilotSDK.services.materializedServices.redis import Redis
from BenchPilotSDK.services.materializedServices.zookeeper import Zookeeper


class MarketingCampaign(SDPEWorkload, ABC):
    """
    This class represents Yahoo Streaming Benchmark, it holds all the extra needed services.
    - by extra we mean the services that are not DSPEs
    """

    @dataclass
    class Parameters:
        num_of_campaigns: int = 1000
        capacity_per_window: int = 100
        kafka_event_count: int = 1000000
        time_divisor: int = 10000
        workload_tuples_per_second_emission: int = 10000
        workload_duration: int = 240
        kafka_brokers: str = 'kafka'
        zookeeper_servers: str = 'zookeeper'
        zookeeper_port: int = 2181
        kafka_topic: str = "ad-events"
        kafka_port: int = 9094
        kafka_partitions: int = 1
        redis_host: str = 'redis'
        maximize_data: int = 1
        process_cores: int = 4

        @classmethod
        def from_dict(cls, env):
            return cls(**{
                k: v for k, v in env.items()
                if k in inspect.signature(cls).parameters
            })

        def __post_init__(self):
            if self.maximize_data > 1:
                self.num_of_campaigns *= self.maximize_data
                self.capacity_per_window *= self.maximize_data
                self.kafka_event_count *= self.maximize_data

    def __init__(self, **workload_definition):
        engine_default_version = {
            'spark': "3.3.0_2.7",
            'storm': "2.2.0",
            'flink': "1.11.3_2.12"
        }
        workload_definition["engine_default_version"] = engine_default_version
        super().__init__(**workload_definition)
        self.parameters.update(asdict(self.Parameters.from_dict(workload_definition)))
        self.add_service(Zookeeper())
        self.add_service(Kafka(len(self.cluster), self.manager_ip))
        self.add_service(Redis())
