from BenchPilotSDK.services.sdpe.engine import Engine

class Flink(Engine):
    """
    Service Specification:
    - Flink: {engine-manager: job-manager, engine-worker: task-manager, engine-client: the service that will submit the job}

    * For engine workers the port that is mapped as default is the starting port number, depending on the threads that
    the user has selected the port numbers will range differently.
    """
    def __init__(self, num_of_workers: int, manager_ip: str = "engine-manager", workload_name: str = None):
        Engine.__init__(self, num_of_workers, "flink")
        self.manager.service_log = 'Starting taskexecutor daemon'
        self.manager.ports = ["6123:6123", "8081:8081"]
        self.client.environment = ["engine=flink", "ui_hostname=" + manager_ip, "ui_port=8081", "workload=" + workload_name]
        for worker in range(num_of_workers):
            self.workers[worker].service_log = 'taskmanager.sh'
