from abc import ABC
import pandas, json, os
from os.path import exists
from workloads.sdpeWorkloadClient import SDPEWorkloadClient, SDPEWorkloadSetup

class MarketingCampaignWorkloadClient(SDPEWorkloadClient, ABC):
    def __init__(self, logger):
        super().__init__(logger)
        self.setup = MarketingCampaignWorkloadSetup()
        self.seen_file_path = '/workload-client/src/data/seen.txt'
        self.updated_file_path = '/workload-client/src/data/updated'

    def get_workload_collected_info(self, name):
        collected_info = {}
        if len(name) > 0 and name in self.workload_record:
            df_updated = pandas.read_csv(self.updated_file_path + '_' + name + '.txt')
            collected_info['updated'] = df_updated.to_json()

        topology = self.get_last_topology()
        if not (topology is None):
            collected_info["topology"] = topology
        return json.dumps(collected_info)

    def get_last_topology(self):
        if "engine" in os.environ and "storm" in os.environ["engine"]:
            file_path = '/workload-client/src/topology.json'
            if os.path.exists(file_path):
                return json.dumps({'status': 'success', 'topology': pandas.read_json(file_path)}), 200, {
                    'ContentType': 'application/json'}
        return None

    def start_workload(self, name, request_body):
        # TODO: to check if the body includes scheduler configuration
        self.setup.update_workload_configuration(request_body)
        self.workload_record.append(name)
        # submit job
        os.system('nohup /workload-client/src/stream-bench.sh START_TEST > output.log &')
        return json.dumps({'status': 'success', 'message': 'Job Submitted'}), 200, {'ContentType': 'application/json'}

    def stop_workload(self):
        self.print_job_statistics()
        self.__delete_previous_processes()
        return json.dumps({'status': 'success', 'message': "Workload Stopped Successfully"}), 200, {
            'ContentType': 'application/json'}

    def __delete_previous_processes(self):
        seen_txt = exists(self.seen_file_path)
        if seen_txt:
            os.system('rm ' + self.seen_file_path)
        updated_txt = exists(self.updated_file_path + '.txt')
        if updated_txt:
            os.system('mv ' + self.updated_file_path + '.txt ' + self.updated_file_path + self.workload_record[len(self.workload_record) - 1] + '.txt')
        os.system('/workload-client/src/stream-bench.sh STOP_TEST > output.log')
        os.system("kill -9 $(ps -aef | grep 'stream-bench' | grep -v grep | awk '{print $2}')")
        os.system("kill -9 $(ps -aef | grep 'sleep' | grep -v grep | awk '{print $2}')")
        os.system("kill -9 $(ps -aef | grep '--configPath' | grep -v grep | awk '{print $2}')")

class MarketingCampaignWorkloadSetup(SDPEWorkloadSetup):

    def __init__(self):
        super().__init__()
        self.workload_client_conf_path = '/workload-client/src/conf/'

    def update_workload_configuration(self, parameters):
        # delete existing conf file (if exists) and create a new one with the needed settings
        if os.path.exists(self.workload_client_conf_path + "benchmarkConf.yaml"):
            os.remove(self.workload_client_conf_path + "benchmarkConf.yaml")

        with open(self.workload_client_conf_path + "benchmarkConf.yaml", 'w+') as outfile:
            benchmark_conf = ""
            parameters = parameters["parameters"]
            for key, value in parameters.items():
                benchmark_conf += key.replace('_', '.') + ': '
                if "brokers" in key or "servers" in key:
                    benchmark_conf += "\n    - " + str(parameters[key]) + "\n"
                else:
                    benchmark_conf += str(parameters[key]) + "\n"
            outfile.write(benchmark_conf)
        outfile.close()
