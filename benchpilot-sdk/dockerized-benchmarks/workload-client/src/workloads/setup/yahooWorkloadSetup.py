import os

from workloads.setup.sdpeWorkloadSetup import SDPEWorkloadSetup


class YahooWorkloadSetup(SDPEWorkloadSetup):

    def __init__(self):
        super().__init__()
        self.workload_client_conf_path = '/workload-client/src/conf/'

    def update_workload_configuration(self, parameters):
        parameters = self.get_yahoo_configuration_parameters(parameters)
        # delete existing conf file (if exists) and create a new one with the needed settings
        if os.path.exists(self.workload_client_conf_path + "benchmarkConf.yaml"):
            os.remove(self.workload_client_conf_path + "benchmarkConf.yaml")

        with open(self.workload_client_conf_path + "benchmarkConf.yaml", 'w+') as outfile:
            benchmark_conf = ""
            for key in parameters.__dict__:
                benchmark_conf += key.replace('_', '.') + ': '
                if "brokers" in key or "servers" in key:
                    benchmark_conf += "\n    - " + str(parameters.__dict__['kafka_brokers']) + "\n"
                else:
                    benchmark_conf += str(parameters.__dict__[key]) + "\n"
            outfile.write(benchmark_conf)
        outfile.close()

    def get_yahoo_configuration_parameters(self, workload_yaml):
        workload_parameters = workload_yaml["parameters"]
        parameters = self.update_engine_parameters(workload_parameters)
        # workload specific
        parameters.number_campaigns = workload_parameters["campaigns"] if "campaigns" in workload_parameters else 1000
        parameters.view_capacity_per_window = workload_parameters[
            "capacity.per.window"] if "capacity_per_window" in workload_parameters else 100
        parameters.kafka_event_count = workload_parameters[
            "kafka_event_count"] if "kafka_event_count" in workload_parameters else 1000000
        if "maximize_data" in workload_parameters:
            parameters.number_campaigns *= int(workload_parameters["maximize_data"])
            parameters.view_capacity_per_window *= int(workload_parameters["maximize_data"])
            parameters.kafka_event_count *= int(workload_parameters["maximize_data"])

        parameters.time_divisor = workload_parameters[
            "time_divisor"] if "time_divisor" in workload_parameters else 10000
        parameters.benchmark_tuples_per_second_emition = workload_parameters[
            "tuples_per_second"] if "tuples_per_second" in workload_parameters else 10000
        parameters.benchmark_duration = workload_yaml["duration"] if "duration" in workload_parameters else 240

        parameters.kafka_brokers = workload_parameters["kafka"] if "kafka" in workload_parameters else "kafka"
        parameters.zookeeper_servers = workload_parameters[
            "zookeeper"] if "zookeeper" in workload_parameters else "zookeeper"

        parameters.zookeeper_port = workload_parameters[
            "zookeeper_port"] if "zookeeper_port" in workload_parameters else 2181
        parameters.kafka_topic = workload_parameters[
            "kafka_topic"] if "kafka_topic" in workload_parameters else "ad-events"
        parameters.kafka_port = workload_parameters["kafka_port"] if "kafka_port" in workload_parameters else 9094
        parameters.kafka_partitions = workload_parameters[
            "kafka_partitions"] if "kafka_partitions" in workload_parameters else 1
        parameters.redis_host = workload_parameters["redis_host"] if "redis_host" in workload_parameters else "redis"

        return parameters
