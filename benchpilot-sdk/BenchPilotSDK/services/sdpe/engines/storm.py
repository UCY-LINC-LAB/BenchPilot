from BenchPilotSDK.services.sdpe.engine import Engine
from BenchPilotSDK.services.service import Service

class Storm(Engine):
    """
    Service Specification:
    - Storm: {engine-manager: nimbus, engine-worker: supervisor, engine-client: the service that will submit the job}

    * For engine workers the port that is mapped as default is the starting port number, depending on the threads that
    the user has selected the port numbers will range differently.
    """

    def __init__(self, num_of_workers: int, manager_ip: str = "engine-manager", workload_name: str = None):
        Engine.__init__(self, num_of_workers, "storm")
        self.service_log = 'Running: /usr/lib/jvm/java-8-openjdk-amd64/bin/java -server'
        self.manager.ports = ["6627:6627"]
        self.client.environment = ["NIMBUS_SEEDS=" + manager_ip, "NIMBUS_THRIFT_PORT=6627", "engine=storm", "ui_hostname=" + manager_ip, "ui_port=8080", "workload=" + workload_name]
        self.ui = Service()
        self.ui.hostname = "storm-ui"
        self.ui.image = "benchpilot/benchpilot"
        self.ui.image_tag = "sdpe-cluster-storm"
        self.ui.depends_on = ['engine-manager']
        self.ui.ports = ["8080:8080"]
        self.services.append(self.ui)
        self.ui.command = "[\"/bin/bash\", \"-c\", \"./stream-bench.sh START_UI && sleep infinity\"]"
        # assign log
        for service in self.services:
            if not ('engine-client' in service.hostname):
                service.service_log = self.service_log