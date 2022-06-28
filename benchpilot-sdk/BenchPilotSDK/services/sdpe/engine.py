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
    service_log: str

    def __init__(self, num_of_workers: int, engine: str, workload_name: str = None):
        self.services = []
        self.workers = []
        self.manager = Service()
        self.manager.command = "[\"/bin/bash\", \"-c\", \"./stream-bench.sh START_MANAGER && sleep infinity\"]"
        self.manager.hostname = "engine-manager"
        self.client = Service()
        self.needs_proxy = True
        self.client.hostname = "engine-client"
        self.client.depends_on = ['engine-manager']
        self.client.ports = ["5000:5000"]
        self.client.service_log = "Serving Flask app"
        self.services.append(self.manager)
        self.services.append(self.client)
        for worker in range(num_of_workers):
            self.workers.append(Service())
            self.workers[worker].needs_placement = True
            self.services.append(self.workers[worker])
            self.workers[worker].depends_on = ['engine-manager']
            self.workers[worker].hostname = "engine-worker_" + str(worker)
            self.workers[
                worker].command = "[\"/bin/bash\", \"-c\", \"./stream-bench.sh START_WORKER && sleep infinity\"]"
        self.__assign_image(engine)

    def __assign_image(self, engine: str):
        service.image = "benchpilot/benchpilot"
        for service in self.services:
            if "client" in service.hostname:
                service.image_tag = "workload-client-" + engine
            else:
                service.image_tag = "sdpe-cluster-" + engine
                service.image_arm_tag = service.image_tag + "-arm"
