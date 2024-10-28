from BenchPilotSDK.services.service import Service


class Engine:
    """
    This class works as an Engine representative, holds the objects of the manager, client and worker(s)
    Service Specification:
    - Flink: {engine-manager: job-manager, engine-worker: task-manager}
    - Storm: {engine-manager: [nimbus, ui], engine-worker: supervisor}
    - Spark: {engine-manager: spark master, engine-worker: spark slave}
    * For engine workers the port that is mapped as default is the starting port number, depending on the threads that
    the user has selected the port numbers will range differently.
    """
    image: str
    workers: []
    client: Service
    manager: Service
    services: []
    service_started_log: str

    def __init__(self, num_of_workers: int, engine: str, workload_name: str = None, parameters: [] = []):
        self.services = []
        self.workers = []
        self.parameters = []
        self.manager = Service()
        self.manager.hostname = self.name = "engine-manager"
        engine_parameters = parameters["engine_parameters"] if "engine_parameters" in parameters else []
        engine_commands = engine_parameters["engine_commands"] if "engine_commands" in engine_parameters else []
        worker_environment_var = engine_parameters[
            "worker_environment_var"] if "worker_environment_var" in engine_parameters else []
        if len(engine_commands["manager"]) > 0:
            self.manager.command = engine_commands["manager"]
        self.client = Service()
        self.needs_proxy = True
        self.version = parameters["version"]
        self.client.hostname = workload_name + "-client"
        self.client.name = "client"
        self.client.needs_proxy = self.needs_proxy
        self.manager.needs_proxy = self.needs_proxy
        self.client.depends_on = ['engine-manager']
        self.client.service_started_log = "Serving"
        self.services.append(self.manager)
        self.services.append(self.client)
        for worker in range(num_of_workers):
            self.workers.append(Service())
            self.workers[worker].needs_placement = True
            self.services.append(self.workers[worker])
            self.workers[worker].depends_on = ['engine-manager']
            self.workers[worker].hostname = self.name = "engine-worker_" + str(worker)
            if len(engine_commands["worker"]) > 0:
                self.workers[worker].command = engine_commands["worker"]
            if len(worker_environment_var) > 0:
                self.workers[worker].add_environment(env_name=worker_environment_var[worker]["env_name"],
                                                     env_value=worker_environment_var[worker]["env_value"])
        self.__assign_image(engine)

    def __assign_image(self, engine: str):
        for service in self.services:
            image_name = "benchpilot/benchpilot"
            if "client" in service.hostname:
                image_tag = "workload-cli-" + engine + "-" + self.version
            else:
                image_tag = "sdpe-" + engine + "-" + self.version
            service.assign_image(image_name, image_tag, same_tag_for_all_arch=True)
