from BenchPilotSDK.services.materializedServices.sdpe.engine import Engine


class Spark(Engine):
    """
    Service Specification:
    - Spark: {engine-manager: spark-master, engine-worker: spark-slave, engine-client: the service that will submit the job}

    * For engine workers the port that is mapped as default is the starting port number, depending on the threads that
    the user has selected the port numbers will range differently.
    """

    def __init__(self, num_of_workers: int, workload_name: str = None, parameters: {} = {}):
        parameters["engine_parameters"] = {
            "engine_commands": {"worker": "worker spark://$MANAGER_HOSTNAME:$MANAGER_PORT",
                                "manager": "master -h 0.0.0.0 -p $MANAGER_PORT"}}
        Engine.__init__(self, num_of_workers, "spark", workload_name, parameters)
        self.service_started_log = 'starting org.apache.spark'
        manager_ip = "engine-manager"
        if len(parameters) > 0 and "ui_port" in parameters:
            self.manager.add_port(host_port=parameters["ui_port"], container_port="4040")
            parameters["engine_parameters"]["engine_commands"]["manager"] += " --webui-port 4040"
        self.manager.add_environment(env_name="MANAGER_HOSTNAME", env_value=manager_ip)
        self.client.add_environment(env_name="engine", env_value="spark")
        self.client.add_environment(env_name="ui_hostname", env_value=manager_ip)
        self.client.add_environment(env_name="ui_port", env_value="4040")
        self.client.add_environment(env_name="workload", env_value=workload_name)
        for worker in range(num_of_workers):
            self.workers[worker].add_environment(env_name="MANAGER_HOSTNAME", env_value=manager_ip)
        # assign log
        for service in self.services:
            if not ('engine-client' in service.hostname):
                service.service_started_log = self.service_started_log
