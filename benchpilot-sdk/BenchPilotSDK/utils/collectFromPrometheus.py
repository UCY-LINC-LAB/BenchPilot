from prometheus_pandas import query
import pandas as pd
import os

class PrometheusClient(object):
    """
    This class works as a Prometheus Client, retrieves experiments' results
    """

    def __init__(self, workloads = None, prometheus_prefix = None, prometheus_suffix = None):
        prometheus_ip = os.environ["PROMETHEUS_IP"] if "PROMETHEUS_IP" in os.environ else '0.0.0.0'
        print('Prometheus IP is set as: ' + prometheus_ip)
        self.prometheus_connection = query.Prometheus('http://' + prometheus_ip + ':9090')
        df_prometheus = {}
        self.assign_prometheus_prefix(prometheus_prefix)
        self.assign_prometheus_suffix(prometheus_suffix)
        self.assign_workload_timestamps(workloads)
        
    def assign_prometheus_prefix(prometheus_prefix):
        if prometheus_prefic is None:
            self.prometheus_prefix = os.environ["PROMETHEUS_PREFIX"] if "PROMETHEUS_PREFIX" in os.environ else 'netdata'
        else:
            self.prometheus_prefix = prometheus_prefix
        print('Prometheus Prefix set as: ' + self.prometheus_prefix)
        
            
    def assign_prometheus_suffix(list_of_suffixes):
        self.api_memory_suffix = list_of_suffixes["memory"] if "memory" in list_of_suffixes else '_system_ram_MiB_average{dimension="used"}'
        
        self.api_disk_suffix = list_of_suffixes["disk"] if "disk" in list_of_suffixes else '_disk_io_KiB_persec_average'
        
        self.api_power_suffix = list_of_suffixes["power"] if "power" in list_of_suffixes else {'raspberrypi': '_prometheus_smart_plug_', 'nc': '_snmp_r4spdu7_power_W_average'}
        
        self.api_network_suffix = list_of_suffixes["network"] if "network" in list_of_suffixes else '_system_net_kilobits_persec_average'
        
        self.api_temp_suffix = list_of_suffixes["temp"] if "temp" in list_of_suffixes else '_sensors_temperature_Celsius_average)'
        
        self.api_cpu_suffix = list_of_suffixes["cpu"] if "cpu" in list_of_suffixes else '_cpu_cpu_percentage_average)'
        
        
    def assign_workload_timestamps(workloads):
        self.df_workloads = workloads if not workloads is None else []
            
    # setting up metric names, its columns and titles
    def get_renamed_title(self, metric, worker, df):
        columns = df.columns
        if "cpu" in metric or "power" in metric or "memory" in metric or "temp" in metric:
            return {str(columns[0]): worker}
        elif "network" in metric:
            return {str(columns[0]): worker + ': Network Received', str(columns[1]): worker + ': Network Sent'}
        elif "disk" in metric:
            return {str(columns[0]): worker + ': Disk Reads', str(columns[1]): worker + ': Disk Writes'}

    def get_renamed_title_by_metric(self, metric, worker, df):
        columns = df.columns
        if "cpu" in metric or "memory" in metric or "temp" in metric:
            return {str(columns[0]): metric + "_" + str(columns[0])}
        if "power" in metric:
            return {str(columns[0]): metric + "_" + str(columns[0]), str(columns[1]): metric + "_" + str(columns[1]),}
        elif "network" in metric:
            return {str(columns[0]): str(columns[0]).split(":")[0] + '_network_received', str(columns[1]): str(columns[1]).split(":")[0] + '_network_sent'}
        elif "disk" in metric:
            return {str(columns[0]): str(columns[0]).split(":")[0] + '_disk_reads', str(columns[1]): str(columns[1]).split(":")[0] + '_disk_writes'}

    def get_metric_title_name(self, metric):
        if "memory" in metric:
            return metric.upper() + ' in MiB'
        elif "power" in metric:
            return metric.upper() + ' in W'
        elif "temp" in metric:
            return metric.upper() + ' in °C'
        else:
            return metric.upper()
        

    # declaring prefix and suffix for prometheus for each metric
    def get_prefix_suffix(self, metric: str, device_hostname: str = ""):
        api = {}
        api["prefix"] = self.prometheus_prefix

        if "raspberrypi" in device_hostname:
            if "cpu" in metric:
                api["prefix"] = 'sum(' + api["prefix"]
                api["suffix"] = self.api_cpu_suffix
            elif "power" in metric:
                api["suffix"] = api_power_suffix["raspberrypi"] + '_power_W_W_average'
            else:
                api["suffix"] = api_power_suffix["nc"]
            elif "network" in metric:
                api["suffix"] = self.api_network_suffix
            elif "memory" in metric:
                api["suffix"] = self.api_memory_suffix
            elif "disk" in metric:
                api["suffix"] = self.api_disk_suffix
            elif "temp" in metric:
                api["prefix"] = 'avg(' + api["prefix"]
                api["suffix"] = self.api_temp_suffix
        else: 
            return None
        return api

    # returning plots and stats for a specific run with these parameters
    def get_benchmark_results(self, index: int, metrics: [] = [], devices: [] = []):
        for i in range(0, len(metrics)):
            df_prometheus_all = pd.DataFrame()
            d_prometheus_sum = 0
            for k in range(0, len(devices)):
                api = self.get_prefix_suffix(metrics[i], devices[k])
                if api != None:
                    df_prometheus = self.prometheus_connection.query_range(api["prefix"] + api["suffix"], self.df_workloads[index].startTime, self.df_workloads[index].endTime, "1s")
                    if len(df_prometheus.sum()) > 0:
                        d_prometheus_sum += df_prometheus.sum().values[0]
                    if len(df_prometheus) > 0:
                        df_prometheus_all = pd.concat([df_prometheus.rename(columns=self.get_renamed_title(metrics[i], devices[k], df_prometheus)), df_prometheus_all], axis=1)
            if len(df_prometheus_all) > 0:
                df_prometheus_all.plot(title=self.get_metric_title_name(metrics[i]) + ' \nSUM: ' + str(d_prometheus_sum))


    # exporting results to csv
    def export_results_to_csv(self, experiment_name: str, metrics: [] = [], devices: [] = [], csv_path: str):
        df_exported_experiments = pd.DataFrame()
        
        # retrieve results
        for i in range(0, len(metrics)):
            df_prometheus_all = pd.DataFrame()
            for k in range(0, len(devices)):
                api = self.get_prefix_suffix(metrics[i], devices[k])
                if api != None:
                    df_prometheus = self.prometheus_connection.query_range(api["prefix"] + api["suffix"], self.df_workloads[index].startTime, self.df_workloads[index].endTime, "1s")
                    if len(df_prometheus) > 0:
                        df_prometheus_all = pd.concat([df_prometheus.rename(columns=self.get_renamed_title(metrics[i], devices[k], df_prometheus)), df_prometheus_all], axis=1)
            if len(df_prometheus_all) > 0:
                df_exported_experiments = pd.concat([df_prometheus_all.rename(columns=self.get_renamed_title_by_metric(metrics[i], '', df_prometheus_all)), df_exported_experiments], axis=1)
                    
        df_exported_experiments.to_csv(csv_path + experiment_name + ".csv")
    