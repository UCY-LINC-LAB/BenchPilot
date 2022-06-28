from abc import ABC

from workloads.sdpeWorkloadClient import SDPEWorkloadClient
from os.path import exists
from workloads.setup.yahooWorkloadSetup import YahooWorkloadSetup
import pandas, json, os

class YahooWorkloadClient(SDPEWorkloadClient, ABC):
    def __init__(self):
        super().__init__()
        self.setup = YahooWorkloadSetup()
        self.seen_file_path = '/workload-client/data/seen.txt'
        self.updated_file_path = '/workload-client/data/updated'
        # self.workload_record_path = '/workload-client/src/workloads.csv'

    def get_workload_collected_info(self, timestamp):
        collected_info = {}
        if len(timestamp) > 0 and timestamp in self.workload_record:
            df_updated = pandas.read_csv(self.updated_file_path + '_' + timestamp + '.txt')
            collected_info['updated'] = df_updated.to_json()

        topology = self.get_last_topology()
        if not (topology is None):
            collected_info["topology"] = topology
        return json.dumps(collected_info)

    def get_last_topology(self):
        if "storm" in self.engine:
            file_path = '/workload-client/src/topology.json'
            if os.path.exists(file_path):
                return json.dumps({'status': 'success', 'topology': pandas.read_json(file_path)}), 200, {
                    'ContentType': 'application/json'}
        return None

    def start_workload(self, starting_timestamp, request_body):
        # TODO: to check if the body includes scheduler configuration
        # TODO: this will later on change if we will support running workloads simultaneously

        self.setup.update_workload_configuration(request_body)
        self.workload_record.append(starting_timestamp)
        # submit job
        os.system('nohup sh ./stream-bench.sh START_TEST &')
        return json.dumps({'status': 'success', 'message': 'Job Submitted'}), 200, {'ContentType': 'application/json'}

    def stop_workload(self):
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
        os.system('sh /workload-client/stream-bench.sh STOP_TEST')
        os.system("kill -9 $(ps -aef | grep 'stream-bench' | grep -v grep | awk '{print $2}')")
        os.system("kill -9 $(ps -aef | grep 'sleep' | grep -v grep | awk '{print $2}')")
        os.system("kill -9 $(ps -aef | grep '--configPath' | grep -v grep | awk '{print $2}')")
