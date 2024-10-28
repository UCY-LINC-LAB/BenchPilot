from BenchPilotSDK.services.materializedServices.sdpe.engine import Engine
from BenchPilotSDK.services.service import Service


class Storm(Engine):
    """
    Service Specification:
    - Storm: {engine-manager: nimbus, engine-worker: supervisor, engine-client: the service that will submit the job}
    * For engine workers the port that is mapped as default is the starting port number, depending on the threads that
    the user has selected the port numbers will range differently.
    """

    def __init__(self, num_of_workers: int, workload_name: str = None, parameters: {} = {}):
        engine_parameters = {"engine_commands": {"worker": "supervisor", "manager": "nimbus"}}
        if "executors_per_node" in parameters and len(parameters["executors_per_node"]) > 0:
            worker_environment_var = {}
            i = 0
            for worker in range(num_of_workers):
                worker_environment_var[worker] = {'env_name': "EXECUTORS",
                                                  'env_value': str(parameters["executors_per_node"][i])}
                i = i + 1 if i < len(parameters["executors_per_node"]) - 1 else 0
            engine_parameters["worker_environment_var"] = worker_environment_var
            parameters["engine_parameters"] = engine_parameters
        Engine.__init__(self, num_of_workers, "storm", workload_name, parameters)
        self.service_started_log = 'Running: '
        self.client.add_environment(env_name="engine", env_value="storm")
        self.client.add_environment(env_name="ui_hostname", env_value='storm-ui')
        self.client.add_environment(env_name="ui_port", env_value="8080")
        self.client.add_environment(env_name="workload", env_value=workload_name)
        self.client.add_environment(env_name="NIMBUS_SEEDS", env_value='engine-manager')
        self.client.add_environment(env_name="NIMBUS_THRIFT_PORT", env_value='6627')
        self.ui = Service()
        self.ui.hostname = "storm-ui"
        self.ui.assign_image(image_name="benchpilot/benchpilot", image_tag="sdpe-storm-" + self.version,
                             same_tag_for_all_arch=True)
        self.ui.depends_on = ['engine-manager']
        if len(parameters) > 0 and "ui_port" in parameters:
            self.ui.add_port(host_port=parameters["ui_port"], container_port="8080")
        self.services.append(self.ui)
        self.ui.command = "ui"
        # assign log
        for service in self.services:
            if not ('client' in service.hostname):
                service.service_started_log = self.service_started_log