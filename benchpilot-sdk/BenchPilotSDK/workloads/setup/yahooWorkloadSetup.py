import os, subprocess

from BenchPilotSDK.workloads.setup.sdpeWorkloadSetup import SDPEWorkloadSetup


class YahooWorkloadSetup(SDPEWorkloadSetup):

    def __init__(self, workload_yaml):
        super().__init__(workload_yaml)
        self.workload_client_path += 'yahoo-streaming-workloads/yahoo-common/conf/'
        self.benchmark_conf_file = os.environ["BENCHPILOT_PATH"] + "BenchPilotSDK/conf/benchmarkConf.yaml"

    def update_workload_configuration(self, parameters):
        # TODO: transfer this to the client, and here make a call to the client to update conf
        self.update_storm_conf_cluster(parameters)
        parameters = self.get_yahoo_configuration_parameters()
        # delete existing conf file (if exists) and create a new one with the needed settings
        if os.path.exists(self.benchmark_conf_file):
            os.remove(self.benchmark_conf_file)

        with open(self.benchmark_conf_file, 'w+') as outfile:
            benchmark_conf = ""
            for key in parameters:
                benchmark_conf += key.replace('_', '.') + ': '
                if "brokers" in key or "servers" in key:
                    benchmark_conf += "\n    - " + str(parameters["kafka_brokers"]) + "\n"
                else:
                    benchmark_conf += str(parameters[key]) + "\n"
            outfile.write(benchmark_conf)
        outfile.close()
        # copy file to the directory that the benchmark exists, since the manager/worker may need it as well
        subprocess.check_output(
            ['cp', self.benchmark_conf_file,
             self.workload_client_path + 'benchmarkConf.yaml'])

    def get_yahoo_configuration_parameters(self):
        parameters = {
            'number_campaigns': 1000,
            'view_capacity_per_window': 100,
            'kafka_event_count': 1000000,
            'time_divisor': 10000,
            'benchmark_tuples_per_second_emition': 10000,
            'benchmark_duration': 240,
            'kafka_brokers': 'kafka',
            'zookeeper_servers': 'zookeeper',
            'zookeeper_port': 2181,
            'kafka_topic': "ad-events",
            'kafka_port': 9094,
            'kafka_partitions': 1,
            'redis_host': 'redis',
            'flink_buffer_timeout': 100,
            'flink_checkpoint_interval': 1000,
            'flink_partitions': 1,
            'storm_workers': 1,
            'storm_ackers': 1,
            'storm_partitions': 1,
            'spark_batchtime': 10000,
            'spark_executor_cores': 1,
            'spark_executor_memory': '1G',
            'spark_partitions': 10
        }
        workload_parameters = self.workload_yaml["parameters"]
        # workload specific
        if "campaigns" in workload_parameters:
            parameters["number_campaigns"] = workload_parameters["campaigns"]
        if "capacity_per_window" in workload_parameters:
            parameters["view_capacity_per_window"] = workload_parameters["capacity_per_window"]
        if "kafka_event_count" in workload_parameters:
            parameters["kafka_event_count"] = workload_parameters["kafka.event.count"]
        if "maximize_data" in workload_parameters:
            parameters["number_campaigns"] *= int(workload_parameters["maximize_data"])
            parameters["view_capacity_per_window"] *= int(workload_parameters["maximize_data"])
            parameters["kafka_event_count"] *= int(workload_parameters["maximize_data"])

        if "time_divisor" in workload_parameters:
            parameters["time_divisor"] = workload_parameters["time_divisor"]
        if "tuples_per_second" in workload_parameters:
            parameters["benchmark_tuples_per_second_emition"] = workload_parameters["tuples_per_second"]
        if "duration" in workload_parameters:
            parameters["benchmark_duration"] = self.workload_yaml["duration"] 
    
        if "kafka_hostname" in workload_parameters:
            parameters["kafka_brokers"] = workload_parameters["kafka_hostname"]
        if "zookeeper_hostname" in workload_parameters:
            parameters["zookeeper_servers"] = workload_parameters["zookeeper_hostname"]

        if "zookeeper_port" in workload_parameters:
            parameters["zookeeper_port"] = workload_parameters["zookeeper_port"]
        if "kafka_topic" in workload_parameters:
            parameters["kafka_topic"] = workload_parameters["kafka_topic"]
        if "kafka_port" in workload_parameters:
            parameters["kafka_port"] = workload_parameters["kafka_port"]
        if "kafka_partitions" in workload_parameters:
            parameters["kafka_partitions"] = workload_parameters["kafka_partitions"]
        if "redis_host" in workload_parameters:
            parameters["redis_host"] = workload_parameters["redis_host"] 

        engine_parameters = None
        if "parameters" in self.workload_yaml["engine"]:
            engine_parameters = self.workload_yaml["engine"]["parameters"]

        # flink specific
        if "flink" in self.workload_yaml["engine"]["name"]:
            if "buffer_timeout" in engine_parameters:
                parameters["flink_buffer_timeout"] = engine_parameters["buffer_timeout"]
            if "checkpoint_interval" in engine_parameters:
                parameters["flink_checkpoint_interval"] = engine_parameters["checkpoint_interval"]
            if "buffer_timeout" in engine_parameters:
                parameters["flink_partitions"] = engine_parameters["buffer_timeout"] 

        # storm specific
        if "storm" in self.workload_yaml["engine"]["name"]:
            self.update_storm_conf_cluster(parameters)
            parameters["storm_workers"] = len(self.workload_yaml["cluster"]["nodes"])
            if "ackers" in engine_parameters:
                parameters["storm_ackers"] = engine_parameters["ackers"] 
            if "partitions" in engine_parameters:
                parameters["storm_partitions"] = engine_parameters["partitions"]

        # spark specific
        if "spark" in self.workload_yaml["engine"]["name"]:
            if "batchtime" in engine_parameters:
                parameters["spark_batchtime"] = engine_parameters["batchtime"]
            if "executor_cores" in engine_parameters:
                parameters["spark_executor_cores"] = engine_parameters["executor_cores"]
            if "executor_memory" in engine_parameters:
                parameters["spark_executor_memory"] = engine_parameters["executor_memory"]
            if "partitions" in engine_parameters:
                parameters["spark_partitions"] = engine_parameters["partitions"] 
        return parameters