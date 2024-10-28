from BenchPilotSDK.services.materializedServices.sdpe.engine import Engine


class Flink(Engine):
    """
    Service Specification:
    - Flink: {engine-manager: job-manager, engine-worker: task-manager, engine-client: the service that will submit the job}

    * For engine workers the port that is mapped as default is the starting port number, depending on the threads that
    the user has selected the port numbers will range differently.
    """

    def __init__(self, num_of_workers: int, workload_name: str = None, parameters: {} = {}):
        parameters["engine_parameters"] = {
            "engine_commands": {"worker": "taskmanager start-foreground",
                                "manager": "jobmanager start-foreground engine-manager 8081"}}
        Engine.__init__(self, num_of_workers, "flink", workload_name, parameters)
        self.manager.service_started_log = 'Initializing cluster services'
        if len(parameters) > 0 and "ui_port" in parameters:
            self.manager.add_port(host_port=parameters["ui_port"], container_port="8081")
        self.client.add_environment(env_name="engine", env_value="flink")
        self.client.add_environment(env_name="ui_hostname", env_value='engine-manager')
        self.client.add_environment(env_name="ui_port", env_value="8081")
        self.client.add_environment(env_name="workload", env_value=workload_name)
        for worker in range(num_of_workers):
            self.workers[worker].service_started_log = 'Successful registration'
