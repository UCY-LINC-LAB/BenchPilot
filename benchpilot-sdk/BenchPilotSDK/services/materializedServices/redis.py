from BenchPilotSDK.services.service import Service


class Redis(Service):
    """
    This class represents the redis docker service, it holds some default variables for the container to be created
    """

    def __init__(self):
        Service.__init__(self)
        self.hostname = "redis"
        self.assign_image(image_name="bitnami/redis", image_tag="6.0.10")
        self.add_environment("ALLOW_EMPTY_PASSWORD", "yes")
        self.service_started_log = "Ready to accept connections"
