from abc import abstractmethod


class Service(object):
    """
    The Service is an abstract class responsible to hold the necessary information
    """
    image: str
    hostname: str
    restart: str
    ports: []
    placement: str
    environment: []
    depends_on: []
    command: str
    service_log: str
    volumes: []
    image_tag: str
    image_arm_tag: str
    needs_proxy: bool = False
    needs_placement: bool = False

    def __init__(self):
        self.restart = "on-failure"
        self.placement = "manager"
        self.application_service_has_not_started = True
        self.container_service_has_not_started = True
        self.sec_waiting = 0
        self.image_tag = 'latest'
        self.image_arm_tag = 'not supported'

    @abstractmethod
    def reassign_placement(self, placement: str):
        self.placement = placement

    @abstractmethod
    def assign_proxy(self, http_proxy: str, https_proxy: str):
        if self.needs_proxy:
            if not hasattr(self, "environment"):
                self.environment = []
            if len(https_proxy) > 0:
                self.environment.append("http_proxy=" + http_proxy)
                self.environment.append("HTTP_PROXY=" + http_proxy)
            if len(https_proxy) > 0:
                self.environment.append("https_proxy=" + https_proxy)
                self.environment.append("HTTPS_PROXY=" + https_proxy)
