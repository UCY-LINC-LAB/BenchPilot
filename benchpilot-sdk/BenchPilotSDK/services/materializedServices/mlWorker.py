from BenchPilotSDK.services.service import Service


class MlWorker(Service):
    """
    This class represents the MLWorker docker service, it holds some default variables for the container to be created
    """

    def __init__(self, image: dict, command: str, service_started_log: str):
        Service.__init__(self)
        self.hostname = "ml_worker"
        self.assign_image(image["image"], image["tag"], same_tag_for_all_arch=True)
        self.service_started_log = service_started_log
        self.command = command
        self.needs_placement = True
