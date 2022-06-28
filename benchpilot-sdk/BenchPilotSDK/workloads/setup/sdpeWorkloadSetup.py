import os, subprocess

from BenchPilotSDK.workloads.setup.workloadSetup import WorkloadSetup


class SDPEWorkloadSetup(WorkloadSetup):

    def __init__(self, workload_yaml = None):
        super().__init__(workload_yaml)
        self.cluster_dockerfile_path = os.environ["BENCHPILOT_PATH"] + 'dockerized-benchmarks/engine-dockerfiles/'

    def update_workload_configuration(self, parameters):
        self.update_storm_conf_cluster(parameters)

    # TODO: our language does not really support this right now
    def update_storm_conf_cluster(self, parameters):
        if not "storm_version" in parameters:
            parameters["storm_version"] = '1.2.3'
        storm_yaml = self.cluster_dockerfile_path + "storm-engine/storm.yaml"
        
        # delete existing conf file (if exists) and create a new one with the needed settings
        if os.path.exists(storm_yaml):
            os.remove(storm_yaml)

        with open(storm_yaml, 'w+') as outfile:
            benchmark_conf = "nimbus.seeds: [\"engine-manager\"]\n"
            benchmark_conf += "ui.port: 8080\n"
            benchmark_conf += "storm.zookeeper.servers:\n  - \"zookeeper\"\n"
            benchmark_conf += "storm.local.dir: \"/apache-storm-" + parameters["storm_version"] + "\"\n"
            benchmark_conf += "supervisor.slots.ports:\n"
            # todo: will later on change according to user's preference in "executors_per_node"
            for port in range(0, 4):
                benchmark_conf += "    - 670" + str(port) + "\n"
            outfile.write(benchmark_conf)
        outfile.close()
        # copy file to the directory that the cluster exists, since the client may need it as well
        subprocess.check_output(
            ['cp', storm_yaml, self.workload_client_path + 'storm.yaml'])
