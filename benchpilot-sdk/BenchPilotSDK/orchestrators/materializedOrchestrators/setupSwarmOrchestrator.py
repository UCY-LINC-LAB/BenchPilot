from BenchPilotSDK.orchestrators.setupOrchestrator import SetupOrchestrator
import BenchPilotSDK.utils.benchpilotProcessor as bp
import paramiko


class SetupSwarm(SetupOrchestrator):
    """
    This class contains overrrides the appropriate methods in order to setup automatically a
    docker swarm cluster
    """

    def __init__(self, cluster: dict):
        super().__init__(cluster)
        self.docker_swarm_join_token = ""
        self.commands = {
            "init": "docker swarm init --advertise-addr",
            "join": "docker swarm join",
            "leave": "docker swarm leave",
            "worker-token": "docker swarm join-token worker",
            "info": "docker info",
            "network": "docker network",
            "network_rm": "docker network rm",
            "network_connect": "docker network connect",
            "network_disconnect": "docker network disconnect",
            "network_inspect": "docker network inspect",
            "get_networks": "docker network ls",
            "network_create": "docker network create -d overlay --attachable",
            "force": "--force",
            "token": "--token",
            "node": "docker node",
            "deploy": "docker stack deploy --compose-file",
            "stack": "docker stack",
            "stack_rm": "docker stack rm",
            "get_stacks": "docker stack ls",
            "stack_services": "docker stack services",
            "stack_service_status": "docker service ps --no-trunc",
            "service_rm": "docker service rm",
            "service_logs": "docker service logs",
            "benchPilot_cli_id": "$(cat /etc/hostname)"
        }

    @staticmethod
    def orchestrator_format_command(atts: []):
        format_command = "--format \""
        for att in atts:
            format_command += " {{." + att + "}}"
        return format_command + "\""

    def setup_orchestrator(self):
        self.logger.info("--- BenchPilot: Setting up Swarm ---")
        # create a new docker swarm if there isn't one yet

        command = bp.unite_kernel_commands([self.commands["info"], self.orchestrator_format_command(["Swarm"])])
        swarm_status_command = bp.pipeline_kernel_commands([command, bp.get_nth_attribute_kernel_command(["3"])])
        swarm_manager_command = bp.pipeline_kernel_commands([command, bp.get_nth_attribute_kernel_command(["2"])])
        swarm_status = bp.kernel_run(swarm_status_command, process_output=True)[0]
        swarm_manager = bp.kernel_run(swarm_manager_command, process_output=True)[0]

        if swarm_manager == "inactive":
            swarm_status = swarm_manager
            swarm_manager = self.manager

        # remove any previous docker swarm that wasn't configured correctly
        if (not ("active" in swarm_status) and not ("inactive" in swarm_status)) or self.manager != swarm_manager:
            command = bp.unite_kernel_commands(
                [self.commands["leave"], self.commands["force"], "&&", self.commands["init"], self.manager])
            bp.kernel_run(command=command)
            print("--- Recreating Docker Swarm, in case of having error in this run, please restart the experiment ---")

        # initiate new docker swarm
        if "inactive" in swarm_status:
            command = bp.unite_kernel_commands([self.commands["init"], self.manager])
            bp.kernel_run(command=command, get_output=True)
            print("--- Creating Docker Swarm, in case of having error in this run, please restart the experiment ---")

        # get swarm join worker token
        self.docker_swarm_join_token = self.__get_join_token()

        # remove any 'down' nodes from swarm if they exist
        get_nodes = bp.unite_kernel_commands([self.commands["node"], "ls"])
        find_nodes_down = bp.get_nth_attribute_kernel_command(n_attributes=["1"], condition="$3 == \"Down\"")
        get_lines = bp.unite_kernel_commands(["wc", "-l"])
        command = bp.pipeline_kernel_commands([get_nodes, find_nodes_down, get_lines])
        result = bp.kernel_run(command, process_output=True)[0]

        if int(result) > 0:
            outer_command = bp.unite_kernel_commands([self.commands["node"], "rm"])
            inner_command = bp.pipeline_kernel_commands([get_nodes, find_nodes_down])
            command = bp.define_inner_command_kernel(outer_command=outer_command, inner_command=inner_command)
            bp.kernel_run(command)

        # remember already existing swarm nodes
        find_ready_nodes = bp.get_nth_attribute_kernel_command(n_attributes=["2"], condition="$3 == \"Ready\"")
        command = bp.pipeline_kernel_commands([get_nodes, find_ready_nodes])
        self.orchestrator_nodes = bp.kernel_run(command, process_output=True)

    def register_to_orchestrator(self, hostname: str, client: paramiko.SSHClient()):
        self.logger.info("BenchPilot: Registering worker: " + hostname)
        stdin, stdout, stderr = client.exec_command(self.commands["info"])
        if not self.manager in stdout and not 'active' in stdout:
            leave_previous_swarm = bp.unite_kernel_commands([self.commands["leave"], self.commands["force"]])
            stdin, stdout, stderr = client.exec_command(leave_previous_swarm)
            join_current_swarm = bp.unite_kernel_commands(
                [self.commands["join"], self.commands["token"], self.docker_swarm_join_token, self.manager + ':2377'])
            stdin, stdout, stderr = client.exec_command(join_current_swarm)
        else:
            self.logger.info("BenchPilot: Worker " + hostname + " was already registerd")

    def __get_join_token(self):
        join_token = bp.kernel_run(self.commands["worker-token"], get_output=True)
        join_token = str(join_token).split("--token")[1]
        join_token = str(join_token).split(self.manager)[0]
        return join_token.split(" ")[1]
