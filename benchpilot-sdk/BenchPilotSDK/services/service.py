from abc import abstractmethod
from dataclasses import dataclass


@dataclass
class Service(object):
    """
    The Service is an abstract class responsible to hold the necessary information
    """
    hostname: str = ""
    command: str = ""
    depends_on: [] = None
    ports: [] = None
    volumes: [] = None
    environment: [] = None
    name: str = None  # it should be less than 63 characters
    placement: str = "manager"
    service_started_log: str = ""
    service_finished_log: str = ""
    needs_proxy: bool = False
    needs_placement: bool = False
    failed: bool = False
    tty: bool = False
    image = None

    def __post_init__(self):
        self.application_service_has_not_started = True
        self.container_service_has_not_started = True
        self.sec_waiting = 0
        self.__volumes = []
        self.__environment = []
        self.__ports = []
        self.depends_on = []
        self.image = {}

    def assign_image(self, image_name, image_tag="latest", image_arm_tag=None, same_tag_for_all_arch: bool = False):
        self.image["name"] = image_name
        self.image["tag"] = image_tag
        if same_tag_for_all_arch:
            self.image["arm_tag"] = image_tag
        else:
            self.image["arm_tag"] = image_arm_tag

    def add_environment(self, env_name: str, env_value: str):
        self.__environment.append({'env_name': env_name, 'env_value': env_value})

    def add_volume(self, container_path: str, host_path: str):
        self.__volumes.append({'container_path': container_path, 'host_path': host_path})

    def add_port(self, container_port: str, host_port: str):
        self.__ports.append({'container_port': container_port, 'host_port': host_port})

    @abstractmethod
    def reassign_placement(self, placement: str):
        self.placement = placement

    @abstractmethod
    def assign_proxy(self, proxies: []):
        if self.needs_proxy:
            if len(proxies) > 0:
                for proxy_k, proxy_v in proxies.items():
                    if len(proxy_v) > 0:
                        self.add_environment(proxy_k.lower(), proxy_v)
                        self.add_environment(proxy_k.upper(), proxy_v)

    def get_service_definition(self, architecture: str = ""):
        definition = {"hostname": self.hostname, "image": self.get_image(architecture),
                      "command": "\"" + self.command + "\"", "depends_on": self.depends_on,
                      "environment": self.get_environment(), "ports": self.get_ports(),
                      "volumes": self.get_volumes()}

        if self.tty:
            definition["tty"] = "true"

        return definition

    def get_environment(self):
        environment = []
        for env in self.__environment:
            environment.append(env['env_name'] + ": \"" + env['env_value'] + "\"")
        return environment

    def get_ports(self):
        ports = []
        for port in self.__ports:
            ports.append(port['host_port'] + ":" + port['container_port'])
        return ports

    def get_volumes(self):
        volumes = []
        for volume in self.__volumes:
            volumes.append(volume['host_path'] + ":" + volume['container_path'])
        return volumes

    def get_image(self, architecture: str):
        image_tag = self.image["tag"]
        if not "manager" in self.placement and not "x86_64" in architecture:
            image_tag = self.image["arm_tag"]
        return self.image["name"] + ":" + image_tag
