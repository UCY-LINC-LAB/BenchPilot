from prometheus_pandas import query
from BenchPilotSDK.utils.exceptions import InvalidWorkloadName, UnloadedBenchmarkMetrics
from BenchPilotSDK.utils.loggerHandler import LoggerHandler
from BenchPilotSDK.utils.exceptions import PostExperimentMetricNotDefined
from math import pi
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import json, re, requests, os
import matplotlib.pyplot as plt
import matplotlib as mpl

"""
 This class facilitates with retrieving and processing the extracted ingishts from the experiments
"""

all_metrics = ["cpu", "power", "network_received", "network_sent", "disk_reads", "disk_writes", "memory", "temp", 
              "cpu_container", "network_received_container", "network_sent_container", "memory_container", "disk_reads_container",
              "disk_writes_container"]

class PostExperimentController(object):

    def __init__(self, db_ip: str = "", db_port: str = "9090",
                 api_prefix: str = "", folder_path: str = "/BenchPilotSDK/experiments/experiments_all/",
                 csv_path: str = "", figure_path: str = ""):
        self.db_conn = query.Prometheus('http://' + db_ip + ':' + db_port)
        self.api_prefix = api_prefix
        self.db_ip = db_ip
        self.db_port = db_port
        self.benchmark_metadata = {}
        self.keyword = {
            "mlperf": "mlperf",
            "marketing-campaign": "client",
            "database": "database"
        } 
        self.workload_rec = {
            "db": {"name": "mdb", "title": "DB", "service": "mdb_database_db", "worker": "db"},
            "mlN": {"name": "mlN", "title": "ML-N", "service": "mlN_mlperf_MlPerf_worker", "worker": "mlperf_MlPerf_worker"},
            "mlO": {"name": "mlO", "title": "ML-O", "service": "mlO_mlperf_MlPerf_worker", "worker": "mlperf_MlPerf_worker"},
            "mlTF": {"name": "mlTF", "title": "ML-TF", "service": "mlTF_mlperf_MlPerf_worker", "worker": "mlperf_MlPerf_worker"},
            "mlNStr": {"name": "mlNStr", "title": "MLSt-N", "service": "mlNStr_mlperf_MlPerf_worker", "worker": "mlperf_MlPerf_worker"},
            "mlOStr": {"name": "mlOStr", "title": "MLSt-O", "service": "mlOStr_mlperf_MlPerf_worker", "worker": "mlperf_MlPerf_worker"},
            "mlTFStr": {"name": "mlTFStr", "title": "MLSt-TF", "service": "mlTFStr_mlperf_MlPerf_worker", "worker": "mlperf_MlPerf_worker"},
            "storm": {"name": "stm", "title": "SA", "service": "stm_engine-worker", "worker": "engine-worker"},
            "sio": {"name": "sio", "title": "S-I/O", "service": "sio_simple", "worker": "simple"},
            "svm": {"name": "svm", "title": "S-VM", "service": "svm_simple", "worker": "simple"},
            "scpu": {"name": "scpu", "title": "S-CPU", "service": "scpu_simple", "worker": "simple"},
            "IP3": {"name": "IP3", "title": "S-Net", "service": "IP3_simple", "worker": "simple"},
        }
        self.folder_path = folder_path
        self.csv_path = csv_path if csv_path != "" else folder_path + "csv/"
        self.figure_path = figure_path if figure_path != "" else folder_path + "img/"
        plt.rcParams['axes.prop_cycle'] = mpl.cycler(color=['#40897B', '#57B6FF', '#505050', '#9673A6'])
        plt.rcParams.update({'figure.max_open_warning': 0})

    # returning plots and stats for a specific run with these parameters
    # please save the benchmarks into a csv first
    def get_benchmark_metrics(self, workload_name: str, metrics=None, export_results_to_csv: bool = False,
                              exported_result_path: str = ""):
        if metrics is None:
            metrics = all_metrics
        workload_metadata = self.__get_experiment_metadata(workload_name)
        df_exported_experiments = pd.DataFrame()
        nodes = self.__get_cluster_nodes(workload_metadata)
        trials = int(self.__get_experiment_trials(workload_metadata))
        workload_metadata = workload_metadata["experiment_record"]
        for i in range(0, trials):
            for j in range(0, len(metrics)):
                df_prometheus_all = pd.DataFrame()
                for k in range(0, len(nodes)):
                    if nodes[k] == "manager":
                        continue
                    api = self.__get_prefix_suffix(metrics[j], nodes[k])
                    if api is not None:
                        # getting results a minute before ending the experiment
                        ending_timestamp = workload_metadata[i]["starting_timestamp"]
                        ending_timestamp = datetime.strptime(ending_timestamp, "%Y-%m-%dT%H:%M:%SZ")
                        ending_timestamp = ending_timestamp + timedelta(minutes=20)
                        ending_timestamp = ending_timestamp.strftime("%Y-%m-%dT%H:%M:00Z")
                        df_prometheus = self.db_conn.query_range(api["prefix"] + nodes[k] + api["suffix"],
                                                                 workload_metadata[i]["starting_timestamp"],
                                                                 ending_timestamp, "1s")
                        if len(df_prometheus) > 0:
                            df_prometheus_all = pd.concat([df_prometheus.rename(columns=self.__get_renamed_title(metrics[j], nodes[k], df_prometheus)),
                                df_prometheus_all], axis=1)
                        elif metrics[j] == "temp":
                            api = self.__get_prefix_suffix(metrics[j], nodes[k], True)
                            if api != None:
                                df_prometheus = self.db_conn.query_range(api["prefix"] + nodes[k] + api["suffix"],
                                                                    workload_metadata[i]["starting_timestamp"],
                                                                    ending_timestamp, "1s")
                                if len(df_prometheus) > 0:
                                    df_prometheus_all = pd.concat([df_prometheus.rename(columns=self.__get_renamed_title(metrics[j], nodes[k], df_prometheus)),
                                        df_prometheus_all], axis=1)

                if len(df_prometheus_all) > 0:
                    df_exported_experiments = pd.concat([df_prometheus_all, df_exported_experiments], axis=1)

        df_exported_experiments = df_exported_experiments.reset_index()
        df_exported_experiments.drop(columns=['index'], inplace=True)

        if export_results_to_csv:
            exported_result_path = "/BenchPilotSDK/experiments/csv/" if len(exported_result_path) <= 0 else exported_result_path
            df_exported_experiments.to_csv(exported_result_path + workload_name + ".csv")


        return df_exported_experiments

    def load_benchmark_meta(self, benchmark_file_path: str):
        with open(benchmark_file_path, "r") as read_content:
            self.benchmark_metadata = json.load(read_content)


    def print_logs(self, experiment_name: str):
        self.__check_metadata_were_loaded()
        experiments = self.benchmark_metadata["experiments"]
        found_experiment = False
        for experiment in experiments:
            if experiment_name in experiment.keys():
                found_experiment = True
                services_record = experiment[experiment_name]["experiment_record"]
                LoggerHandler.coloredPrint("== Experiment: " + experiment_name + " ==", color_level="secondary")
                for trial in range(len(services_record)):
                    LoggerHandler.coloredPrint("== Trial: " + str(trial + 1) + " ==")
                    for workload in services_record[trial]["workload_records"]: 
                        workload_name = list(workload.keys())[0]
                        LoggerHandler.coloredPrint("== Workload: " + workload_name + " ==", color_level="yellow")
                        services_logs = list(workload.values())[0]["workload_record"]["logs"]

                        for service in services_logs:
                            service_name = list(service.keys())[0]
                            service_value = list(service.values())[0]
                            LoggerHandler.coloredPrint("-- Service: " + service_name + " logs --")
                            print(service_value.replace("\\n", "\n").replace("b\"", "").replace("\"", ""))
        if not found_experiment:
            print("The given workload name does not exist")

    def get_available_workloads_from_metadata(self):
        self.__check_metadata_were_loaded()
        experiments = []
        for experiment in self.benchmark_metadata["experiments"]:
            experiments.append(list(experiment.keys())[0])
        return experiments
    
    #### METHODS FOR UTILIZATION (GETTERS) METRICS ####
    
    def replace_keywords(self, att, res, res_nickname):
        if "simple" in att:
            new_att = att.split("simple")[0] + "simple"
            if ".1" in att:
                new_att = new_att + ".1"
            att = new_att
        for i in range(1,4):
            att = att.replace("database_" + str(i) + "_", "")
            att = att.replace("database_" + str(i) + "_", "")
            att = att.replace("marketing-campaign_" + str(i) + "_", "")
            att = att.replace("_marketing-campaign", "")
            att = att.replace("mlpref_" + str(i) + "_", "")
        att = att.replace(res + "_", "")
        att = att.replace(res_nickname + "_", "")
        att = att.replace("database_", "")
        #att = att.replace(".1", "")
        return att.replace("_0", "")

    def df_per_resource_util(self, csv_files, res, util):
        combined_data = pd.DataFrame()
        for csv_file in csv_files:
            file_path = os.path.join(self.csv_path, csv_file)
            if res["short_name"] + "." in csv_file:
                try:
                    df = pd.read_csv(file_path)
                    for att in df:
                        if "_" + util in att:
                            if ("monitoring-stack_smart-plug_1" in att or "sum_containers" in att):
                                df = df.drop([att], axis=1)
                            else:
                                if "power" in util or "temp" in util:
                                    final_name = util
                                    df = df.rename(columns={att: final_name})
                                else:
                                    final_name = att.split(res["name"] + "_" + util + "_")
                                if len(final_name) >= 2:
                                    final_name = final_name[1].split(".")[0]
                                    final_name = self.replace_keywords(final_name, res["name"], res["short_name"])
                                    df = df.rename(columns={att: final_name})
                                    # combine same name columns, since the exported csv just adds a new column for every new experiment
                                    df = df.T.groupby(level=0).sum().T
                                else:
                                    if res["name"] in att:
                                        df = df.rename(columns={att: util})
                        else:   
                            df = df.drop([att], axis=1)
                    
                    combined_data = pd.concat([combined_data, df], ignore_index=True)
                except:
                    print(f"File: {csv_file} not found")
                
        return combined_data

    def get_sums_df(self, df_metrics):
        sums = {}
        for column in df_metrics.columns:
            if "Time" in column:
                continue
            prefix = '_'.join(column.split('_', 2)[:2])  # Extract prefix
            if prefix in sums:
                sums[prefix]["total_sum"] += df_metrics[column].sum()
            else:
                sums[prefix] = {}
                sums[prefix]["total_sum"] = df_metrics[column].sum()
                sums[prefix]["services"] = []
            service = column.split("_")[-1]
            if "simple" in service:
                service = column.split('_')[1]
            if not service in sums[prefix]["services"]:
                sums[prefix]["services"].append({service: df_metrics[column].sum()})
        return sums
    #### /METHODS FOR UTILIZATION (GETTERS) METRICS ####

    #### METHODS FOR APPLICATION (GETTERS) METRICS ####
    
    def get_application_metrics(self, service, log):
        if "mlperf" in service:
            log = log.split("RESULTS:TestScenario.SingleStream ")
            if len(log) < 2:
                return None, None
            log = log[1]
            log = log.split("INFO")[0]
            accuracy = log.split("acc=")
            if len(accuracy) < 2:
                return None, None
            accuracy = accuracy[1].split(",")[0]
            accuracy = accuracy.split("%")[0]
            queries = log.split("queries=")[1]
            queries = queries.split(",")[0]
            return (float(accuracy), int(queries))
        elif "client" in service:
            spouts = (log.split("\"spouts\":[")[-1]).split("]")[0]
            spouts = spouts.split("* Serving Flask")[0]
            bolts = "[" + (log.split("\"bolts\":[")[-1]).split("]")[0] + "]"
            if len(spouts) > 1 and len(bolts) > 1:
                spouts_json = json.loads(spouts)
                bolts_json = json.loads(bolts)
                total_emitted = int(spouts_json["emitted"])
                total_latency = float(spouts_json["completeLatency"])
                for bolt in bolts_json:
                    total_emitted += int(bolt["emitted"])
                    total_latency += float(bolt["processLatency"])
                return (total_emitted, total_latency)
            else:
                print("empty result on service: " + str(service))
                return (0, 0)
        elif "database" in service:
            total_ops_sec = 0
            count = 0
            pattern = r'(\d+\.\d+) current ops/sec'
            # Parse log and calculate total ops/sec
            for line in log.split('\n'):
                match = re.search(pattern, line)
                if match:
                    ops_sec = float(match.group(1))
                    total_ops_sec += ops_sec
                    count += 1

            # Calculate average ops/sec
            average_ops_sec = total_ops_sec / count if count > 0 else 0
            
            return average_ops_sec


    def get_workload_application_metrics(self, exp_files, workload_name):
        application_metrics = {"nc1" : [], "nc8": [], "nc12": [], "rpi": []}
        workload_names = {"nc1" : [], "nc8": [], "nc12": [], "rpi": []}
        for file in exp_files:
            for exp in exp_files[file]['experiments']:
                for workload in exp:
                    for trial in exp[workload]["experiment_record"]: 
                        for rec in trial["workload_records"]:
                            for workload_rec in rec:
                                for log in rec[workload_rec]['workload_record']['logs']:
                                    for service in log:
                                        if self.__filter_out_service(service):
                                            if self.keyword[workload_name] in service:
                                                if "nc8" in service:
                                                    key = "nc8"
                                                elif "nc12" in service:
                                                    key = "nc12"
                                                elif "nc1" in service:
                                                    key = "nc1"
                                                else:
                                                    key = "rpi"
                                                found_metric = False
                                                if "mlperf" in workload_name:
                                                    accuracy, queries = self.get_application_metrics(service, log[service])
                                                    if not "accuracy" in application_metrics[key]:
                                                        application_metrics[key] = {"accuracy": [], "queries": []}
                                                    if accuracy != None and queries != None:
                                                        application_metrics[key]["accuracy"].append(accuracy)
                                                        application_metrics[key]["queries"].append(queries)
                                                        found_metric = True
                                                elif "database" in workload_name:
                                                    metrics = self.get_application_metrics(service, log[service])
                                                    if metrics != None:
                                                        application_metrics[key].append(metrics)
                                                        found_metric = True
                                                elif "marketing-campaign" in workload_name:
                                                    emitted, latency = self.get_application_metrics(service, log[service])
                                                    if not "emitted" in application_metrics[key]:
                                                        application_metrics[key] = {"emitted": [], "latency": []}
                                                    if emitted != None and latency != None:
                                                        application_metrics[key]["emitted"].append(emitted)
                                                        application_metrics[key]["latency"].append(latency)
                                                        found_metric = True
                                                if found_metric:
                                                    workload_names[key].append(service.split("_" + workload_name)[0])

        return (workload_names, application_metrics)

    def __filter_out_service(self, service):
        exclude_services = ["zookeeper", "kafka", "redis", "engine-manager", "engine-worker", "storm-ui", "simple"]
        return not any(exclude in service.lower() for exclude in exclude_services)

    #### /METHODS FOR APPLICATION (GETTERS) METRICS ####

    #### METHODS FOR STORING METRICS ####

    def __get_experiment_metadata(self, workload_name: str):
        self.__check_metadata_were_loaded()
        for experiment in self.benchmark_metadata["experiments"]:
            if workload_name in experiment.keys():
                return experiment[workload_name]
        print("The workload name: " + workload_name + " is not recorded in the file you have provided.")
        raise InvalidWorkloadName()

    def __check_metadata_were_loaded(self):
        if self.benchmark_metadata == {}:
            print("Please run the method 'load_benchmark_meta' first")
            raise UnloadedBenchmarkMetrics()

    @staticmethod
    def __get_cluster_nodes(workload_metadata):
        experiment_nodes = []
        for workload in workload_metadata["experiment_record"][0]["workload_records"]:
            workload_key = next(iter(workload))
            workload_value = workload[workload_key]
            nodes = workload_value["workload_conf"]["cluster"]
            for node in nodes:
                if node not in experiment_nodes:
                    experiment_nodes.append(node)
        return experiment_nodes

    @staticmethod
    def __get_experiment_trials(experiment_metadata):
        return experiment_metadata["experiment_conf"]["repetition"]

    # setting up metric names, its columns and titles
    # you can add more metrics if you would like
    @staticmethod
    def __get_renamed_title(metric, worker, df):
        columns = {}
        for i in range(len(df.columns)):
            net_or_disk_type = ""
            if "network" in metric:
                net_or_disk_type = "_received" if "received" in metric else "_sent"
            elif "disk" in metric:
                net_or_disk_type = "_writes" if "writes" in metric else "_reads"
            if "cpu" == metric or "power" in metric or metric == "memory" or "temp" in metric or ("disk" in metric and not "container" in metric) or "sum" in metric:
                columns[str(df.columns[i])] = worker + "_" + metric
            elif "container" in metric and not "sum" in metric:
                if len(df.columns[i].split('{')[1].split('name=')) <= 1:
                    print("empty result on metric: " + metric + ", worker: " + worker)
                    columns[str(df.columns[i])] = df.columns[i]
                else:
                    columns[str(df.columns[i])] = worker + "_" + metric.split("_")[0] + net_or_disk_type + "_" + df.columns[i].split('{')[1].split('name=')[1].split('"')[1].split(".")[0]
            elif "network" in metric:
                columns[str(df.columns[i])] = worker + '_network' + net_or_disk_type
        
        return columns


    # declaring prefix and suffix for prometheus for each metric
    def __get_prefix_suffix(self, metric: str, node_name: str = "", temp_case: bool = False):
        api = {"prefix": self.api_prefix}
        suffix = {"cpu": '_system_cpu_percentage_average{dimension!="idle"})',
                  "power": self.get_power_suffix(node_name), 
                  "network_received": '_system_net_kilobits_persec_average{dimension="received"}', 
                  "network_sent": '_system_net_kilobits_persec_average{dimension="sent"}', 
                  "memory": '_system_ram_MiB_average{dimension="used"}',
                  "disk_reads": '_disk_io_KiB_persec_average{dimension="reads"})',
                  "disk_writes": '_disk_io_KiB_persec_average{dimension="writes"})',
                  "temp": self.get_temperature_suffix(node_name) + ")",
                  "cpu_container": '_cgroup_cpu_percentage_average{cgroup_name!="[none]", cgroup_name!="netdata", cgroup_name!="monitoring-stack_stream-events_1", cgroup_name!="cadvisor"}',
                  "network_received_container": '_prometheus_cadvisor_container_network_receive_bytes_total_bytes_persec_average{name!="[none]", name!="netdata", name!="monitoring-stack_stream-events_1", name!="cadvisor"}',
                  "network_sent_container": '_prometheus_cadvisor_container_network_transmit_bytes_total_bytes_persec_average{name!="[none]", name!="netdata", name!="monitoring-stack_stream-events_1", name!="cadvisor"}', 
                  "memory_container": '_prometheus_cadvisor_container_memory_usage_bytes_bytes_average{name!="[none]", name!="netdata", name!="monitoring-stack_stream-events_1", name!="cadvisor"}',
                  "disk_reads_container": '_prometheus_cadvisor_container_fs_reads_bytes_total_bytes_persec_average{name!="[none]", name!="netdata", name!="monitoring-stack_stream-events_1", name!="cadvisor"}',
                  "disk_writes_container": '_prometheus_cadvisor_container_fs_writes_bytes_total_writes_persec_average{name!="[none]", name!="netdata", name!="monitoring-stack_stream-events_1", name!="cadvisor"}'
                 }
        suffix["cpu_sum_containers"] = suffix["cpu_container"] + ")"
        suffix["network_received_sum_containers"] = suffix["network_received_container"] + ")"
        suffix["network_sent_sum_containers"] = suffix["network_sent_container"] + ")"
        suffix["cpu_container"] = suffix["cpu_container"] + ") by (cgroup_name)"
        suffix["network_received_container"] = suffix["network_received_container"] + ") by (name)"
        suffix["network_sent_container"] = suffix["network_sent_container"] + ") by (name)"
        suffix["disk_reads_container"] = suffix["disk_reads_container"] + ") by (name)"
        suffix["disk_writes_container"] = suffix["disk_writes_container"] + ") by (name)"
        suffix["memory_sum_containers"] = suffix["memory_container"] + ")"
        if temp_case:
            temp_suffix = self.get_temperature_suffix(node_name, 1)
            if temp_suffix != None:
                suffix["temp"] = temp_suffix + ")"
            else:
                del suffix["temp"]
                print(f"temp for node: {node_name} is not available")
                return None

        # adding sum or avg infront of a specific metric
        if "cpu" in metric or "sum" in metric or "disk" in metric or "network_received_container" == metric or "network_sent_container" == metric or "disk_reads_container" == metric or "disk_writes_container" == metric:
            api["prefix"] = 'sum(' + api["prefix"]  
        elif "temp" in metric:
            api["prefix"] = 'avg(' + api["prefix"]

        # assigning suffix
        if metric not in suffix:
            raise PostExperimentMetricNotDefined("Metric '" + metric + "' Not Defined")
        api["suffix"] = suffix[metric]
        return api

    def get_power_suffix(self, resource: str = ""):
        query_params = {
            'match[]': '{__name__=~"' + self.api_prefix + resource + '_.*", job!="prometheus"}'
        }
        r = requests.get('http://' + self.db_ip + ':' + self.db_port + '/api/v1/label/__name__/values', params=query_params)
        power_metric = re.compile(".*power.*W_average")
        power_metric = list(filter(power_metric.match, r.json()['data']))[0]
        return power_metric.removeprefix(self.api_prefix + resource)

    def get_temperature_suffix(self, resource: str = "", possibility: int = 0):
        query_params = {
            'match[]': '{__name__=~"' + self.api_prefix + resource + '_.*", job!="prometheus"}'
        }
        r = requests.get('http://' + self.db_ip + ':' + self.db_port + '/api/v1/label/__name__/values', params=query_params)
        temp_metric = re.compile(".*_temperature_Celsius_average")
        temp_metric = list(filter(temp_metric.match, r.json()['data']))
        return temp_metric[possibility].removeprefix(self.api_prefix + resource) if possibility < len(temp_metric) else None

    #### /METHODS FOR STORING METRICS ####
