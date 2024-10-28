from BenchPilotSDK.services.service import Service


class Zookeeper(Service):
    """
    This class represents the zookeeper docker service, it holds some default variables for the container to be created
    """

    def __init__(self):
        Service.__init__(self)
        self.hostname = "zookeeper"
        self.assign_image(image_name="wurstmeister/zookeeper")
        #self.add_environment('LOG4J_ROOT_LOGGER', 'INFO')
        self.service_started_log = "binding to port 0.0.0.0/0.0.0.0:"
