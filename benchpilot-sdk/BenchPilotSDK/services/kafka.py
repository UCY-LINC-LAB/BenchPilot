from BenchPilotSDK.services.service import Service


class Kafka(Service):
    """
    This class represents the kafka docker service, it holds some default variables for the container to be created
    """

    def __init__(self, num_partitions: int = 1, manager_ip="kafka"):
        Service.__init__(self)
        self.hostname = "kafka"
        self.image = "wurstmeister/kafka"
        self.image_tag = self.image_arm_tag = "2.13-2.8.1"
        self.ports = ["9092:9092", "9094:9094"]
        self.environment = ['KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181',
                            'KAFKA_ADVERTISED_LISTENERS=INSIDE://kafka:9092,OUTSIDE://' + manager_ip + ':9094',
                            'KAFKA_LISTENERS=INSIDE://:9092,OUTSIDE://:9094',
                            'KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=INSIDE:PLAINTEXT,OUTSIDE:PLAINTEXT',
                            'KAFKA_INTER_BROKER_LISTENER_NAME=INSIDE',
                            'KAFKA_CREATE_TOPICS="ad-events:' + str(num_partitions) + ':1"',
                            'KAFKA_NUM_PARTITIONS=' + str(num_partitions),
                            ]
        self.depends_on = ["zookeeper"]
        self.service_log = "INFO [ZooKeeperClient] Connected. (kafka.zookeeper.ZooKeeperClient)"
