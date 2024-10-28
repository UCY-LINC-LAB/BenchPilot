from BenchPilotSDK.services.service import Service


class Kafka(Service):
    """
    This class represents the kafka docker service, it holds some default variables for the container to be created
    """

    def __init__(self, num_partitions: int = 1, manager_ip="kafka"):
        Service.__init__(self)
        self.hostname = "kafka"
        self.assign_image(image_name="wurstmeister/kafka", image_tag="2.13-2.8.1", same_tag_for_all_arch=True)
        self.add_environment('KAFKA_ZOOKEEPER_CONNECT', 'zookeeper:2181')
        self.add_environment('KAFKA_ADVERTISED_LISTENERS', 'INSIDE://kafka:9092,OUTSIDE://kafka:9094')
        self.add_environment('KAFKA_LISTENERS', 'INSIDE://:9092,OUTSIDE://:9094')
        self.add_environment('KAFKA_LISTENER_SECURITY_PROTOCOL_MAP', 'INSIDE:PLAINTEXT,OUTSIDE:PLAINTEXT')
        self.add_environment('KAFKA_INTER_BROKER_LISTENER_NAME', 'INSIDE')
        self.add_environment('KAFKA_CREATE_TOPICS', 'ad-events:' + str(num_partitions) + ':1')
        self.add_environment('KAFKA_NUM_PARTITIONS', str(num_partitions))
        self.add_environment('TOPIC_PRESERVE_PARTITIONS', str(num_partitions))
        #self.add_environment('LOG4J_ROOTLOGGER', 'INFO,kafkaAppender')
        self.depends_on = ["zookeeper"]
        self.service_started_log = "Connected"
