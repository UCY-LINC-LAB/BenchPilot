from BenchPilotSDK.services.sdpe.engine import Engine

class Spark(Engine):
    """
    Service Specification:
    - Spark: {engine-manager: spark-master, engine-worker: spark-slave, engine-client: the service that will submit the job}

    * For engine workers the port that is mapped as default is the starting port number, depending on the threads that
    the user has selected the port numbers will range differently.
    """
    def __init__(self, num_of_workers: int, manager_ip: str = "engine-manager", workload_name: str = None):
        Engine.__init__(self, num_of_workers, "spark")
        self.service_log = 'starting org.apache.spark'
        self.manager.ports = ["8081:8080", "7077:7077"]
        self.manager.environment = ["MANAGER_HOSTNAME=" + manager_ip, "MANAGER_PORT=7077"]
        self.client.environment = ["MANAGER_HOSTNAME=" + manager_ip, "MANAGER_PORT=7077", "engine=spark", "ui_hostname=" + manager_ip, "ui_port=4040", "workload=" + workload_name]
        self.client.ports = self.client.ports.append("4040:4040")
        for worker in range(num_of_workers):
            self.workers[worker].environment = self.manager.environment.copy()
        # assign log
        for service in self.services:
            if not ('engine-client' in service.hostname):
                service.service_log = self.service_log

