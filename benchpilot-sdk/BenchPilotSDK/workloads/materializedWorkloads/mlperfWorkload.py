from abc import ABC
from dataclasses import dataclass
from BenchPilotSDK.workloads.workload import Workload
from BenchPilotSDK.services.materializedServices.mlWorker import MlWorker


class Mlperf(Workload, ABC):
    """
    This class represents MlPerf Workload, it holds all of the needed services.
    """

    @dataclass
    class Parameters:
        dataset_folder: str
        profile: str
        model_file: str
        data_volume_path: str = "/data"
        model_volume_path: str = "/model"
        output_volume_path: str = "/ml-output"
        worker_threads: int = 1
        accuracy: bool = False
        benchmark_mode: str = None
        extra_parameters: str = None

    def __init__(self, **workload_definition):
        super().__init__(**workload_definition)
        self.parameters = self.Parameters(**workload_definition["parameters"])
        self.env_parameters = "--mlperf_conf ./mlperf.conf --profile " + self.parameters.profile + \
        " --model /mlperf/model/" + self.parameters.model_file + " --dataset-path /mlperf/data/" + \
        self.parameters.dataset_folder + " --output /mlperf/output/" + " --threads " + str(self.parameters.worker_threads)

        if not "default" in str(self.duration):
            self.duration = self.duration - 2
            self.env_parameters += " --time " + str(self.duration)
            # Instead of assigning as default and not be able to find a way to stop, insted append 2min as to give it time to finish for sure
            self.add_duration("2m")
            if "TF" in self.parameters.profile:
            	# Tensorflow always needs a bit more time to print its metrics
                self.add_duration("3m")
        
        if self.parameters.accuracy:
            self.env_parameters += " --accuracy"

        streaming_mode = False
        cluster_str = ''
        if not self.parameters.benchmark_mode is None and "streaming" in self.parameters.benchmark_mode.lower():
            streaming_mode = True
        if not self.parameters.extra_parameters is None:
            self.env_parameters += self.env_parameters + " " + self.parameters.extra_parameters
            
        cpu_gpu = "cpu"
        command = ""
        image = {
            'image': 'benchpilot/benchpilot',
            'tag': 'mlperf-' + cpu_gpu,
        }
        service_started_log = "STARTING"
        service_finished_log = "ENDING"
        
        # append each service for each node
        for i in range(0, len(self.cluster)):
            if "tf" in self.parameters.profile:
                if "raspberrypi" in self.cluster[i]:
                    # for raspberrypis
                    image["tag"] = image["tag"] + '-tf-arm'
                    command = "/benchmark/entrypoint.sh"
                elif "old_server" in self.cluster[i]:
                    # older cpus 
                    image["tag"] = image["tag"] + '-tf-amd'
                    command = "/bin/bash -c 'source activate tf && /benchmark/entrypoint.sh'"
                else:
                    # for newer CPUs
                    image["tag"] = image["tag"] + "-amd"
            ml_worker = MlWorker(image, command, service_started_log)
            if not streaming_mode:
                ml_worker.service_finished_log = service_finished_log
                ml_worker.add_volume(container_path="/mlperf/data", host_path=self.parameters.data_volume_path)
            else:
                ml_worker.add_environment("BENCHMARK_MODE", "STREAMING")
                ml_worker.add_environment("TYPE", "worker")
                ml_worker.needs_proxy = True
            ml_worker.hostname = "MlPerf_worker_" + str(i)
            cluster_str += ml_worker.hostname + ","
            ml_worker.add_environment(env_name="opts", env_value=self.env_parameters)
            ml_worker.add_volume(container_path="/host_proc", host_path="/proc")
            ml_worker.add_volume(container_path="/mlperf/model", host_path=self.parameters.model_volume_path)
            ml_worker.add_volume(container_path="/mlperf/output", host_path=self.parameters.output_volume_path)
            self.add_service(ml_worker)

        if streaming_mode:
            # create one for workload generator
            image["tag"] = 'mlperf-' + cpu_gpu
            if "tf" in self.parameters.profile:
                image["tag"] = image["tag"] + "-amd"
            ml_worker = MlWorker(image, command, service_started_log)
            ml_worker.needs_placement = False
            ml_worker.service_finished_log = service_finished_log
            ml_worker.hostname = "MlPerf_server"
            ml_worker.add_volume(container_path="/mlperf/data", host_path=self.parameters.data_volume_path)
            ml_worker.add_environment("workers", cluster_str[:-1])
            ml_worker.add_environment("BENCHMARK_MODE", "STREAMING")
            ml_worker.add_environment(env_name="opts", env_value=self.env_parameters)
            self.add_service(ml_worker)
