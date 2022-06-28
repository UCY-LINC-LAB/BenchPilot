from BenchPilotSDK.services.service import Service


class Redis(Service):
    """
    This class represents the redis docker service, it holds some default variables for the container to be created
    """

    def __init__(self):
        Service.__init__(self)
        self.hostname = "redis"
        self.image = "bitnami/redis"
        self.image_tag = "6.0.10"
        self.ports = ["6379:6379"]
        self.environment = ["ALLOW_EMPTY_PASSWORD=yes"]
        self.service_log = "Ready to accept connections"
