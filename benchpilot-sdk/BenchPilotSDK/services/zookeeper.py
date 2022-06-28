from BenchPilotSDK.services.service import Service


class Zookeeper(Service):
    """
    This class represents the zookeeper docker service, it holds some default variables for the container to be created
    """

    def __init__(self):
        Service.__init__(self)
        self.hostname = "zookeeper"
        self.image = "wurstmeister/zookeeper"
        self.ports = ["2181:2181"]
        self.service_log = "binding to port 0.0.0.0/0.0.0.0:"
