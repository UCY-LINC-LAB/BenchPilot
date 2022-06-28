import os, subprocess
from abc import ABC

from workloads.setup.workloadSetup import WorkloadSetup


class SDPEWorkloadSetup(WorkloadSetup, ABC):

    def __init__(self):
        super().__init__()

    def update_workload_configuration(self, parameters):
        self.update_storm_conf_cluster()

    @staticmethod
    def update_storm_conf_cluster():
        storm_folder = subprocess.check_output(['ls', '/', '|', 'grep', '-i', 'storm', '|', 'awk', "'{print $1}'"])
        storm_yaml = "/" + str(storm_folder) + "/conf/storm.yaml"
        # delete existing conf file (if exists) and create a new one with the needed settings
        if os.path.exists(storm_yaml):
            os.remove(storm_yaml)

        with open(storm_yaml, 'w+') as outfile:
            benchmark_conf = "nimbus.seeds: [\"engine-manager\"]\n"
            benchmark_conf += "ui.port: 8080\n"
            benchmark_conf += "storm.zookeeper.servers:\n  - \"zookeeper\"\n"
            benchmark_conf += "storm.local.dir: \"" + storm_folder + "\"\n"
            outfile.write(benchmark_conf)
        outfile.close()

    def update_engine_parameters(self, workload_yaml):
        parameters = object()
        engine_parameters = None
        if "parameters" in workload_yaml["engine"]:
            engine_parameters = workload_yaml["engine"]["parameters"]

        # flink specific
        if "flink" in os.environ["engine"]:
            parameters.flink_buffer_timeout = engine_parameters[
                "buffer_timeout"] if "buffer_timeout" in engine_parameters else 100
            parameters.flink_checkpoint_interval = engine_parameters[
                "checkpoint_interval"] if "checkpoint_interval" in engine_parameters else 1000
            parameters.flink_partitions = engine_parameters[
                "buffer_timeout"] if "buffer_timeout" in engine_parameters else 1

        # storm specific
        elif "storm" in os.environ["engine"]:
            self.update_storm_conf_cluster()
            parameters.storm_workers = len(workload_yaml["cluster"]["nodes"])
            parameters.storm_ackers = engine_parameters["ackers"] if "ackers" in engine_parameters else 1
            parameters.storm_partitions = engine_parameters["partitions"] if "partitions" in engine_parameters else 1

        # spark specific
        elif "spark" in os.environ["engine"]:
            parameters.spark_batchtime = engine_parameters["batchtime"] if "batchtime" in engine_parameters else 10000
            parameters.spark_executor_cores = engine_parameters[
                'executor_cores'] if "executor_cores" in engine_parameters else 1
            parameters.spark_executor_memory = engine_parameters[
                'executor_memory'] if "executor_memory" in engine_parameters else "1G"
            parameters.spark_partitions = engine_parameters['partitions'] if "partitions" in engine_parameters else 10

        return parameters
