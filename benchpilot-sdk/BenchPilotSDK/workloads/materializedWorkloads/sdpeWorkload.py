from abc import ABC
from dataclasses import dataclass
import BenchPilotSDK.utils.benchpilotProcessor as bp
from BenchPilotSDK.services.materializedServices.sdpe.engine import Engine
from BenchPilotSDK.services.materializedServices.sdpe.engines import *
from BenchPilotSDK.workloads.materializedWorkloads.clientBasedWorkload import ClientBasedWorkload


class SDPEWorkload(ClientBasedWorkload, ABC):
    """
    This class extends workload and adds the assign engine method in order to be able to assign
    a specific streaming distributed processing engine
    """

    engine: Engine

    @dataclass
    class SDPEParameters:
        engine: str = ""
        params: {} = None

        @dataclass
        class FlinkParameters:
            buffer_timeout: int = 100
            checkpoint_interval: int = 1000
            partitions: int = 1
            version: str = ""

        @dataclass
        class StormParameters:
            workers: int = 1
            ackers: int = 1
            partitions: int = 1
            executors_per_node: [] = None
            ui_port: str = ""
            version: str = ""

        @dataclass
        class SparkParameters:
            batchtime: int = 10000
            executor_cores: int = 1
            executor_memory: str = '1G'
            partitions: int = 10
            version: str = ""

        
        def __post_init__(self):
            self.params = self.engine["engine"]["parameters"]
            self.params.pop("engine_parameters")
            self.engine = self.engine["engine"]["name"]
            if self.engine.capitalize() == "Storm":
                self.engine_parameters = self.StormParameters(**self.params)
            elif self.engine.capitalize() == "Flink":
                self.engine_parameters = self.FlinkParameters(**self.params)
            elif self.engine.capitalize() == "Spark":
                self.engine_parameters = self.SparkParameters(**self.params)

        def get_engine_parameters(self):
            params = {}
            for att in self.engine_parameters.__dict__:
                params[self.engine + "_" + att] = self.engine_parameters.__dict__[att]
            params["engine"] = self.engine
            return params

    def __init__(self, **workload_definition):
        self.engine_default_version = workload_definition["engine_default_version"]
        workload_definition.pop("engine_default_version")
        super().__init__(**workload_definition)
        bp.check_required_parameters('parameters', ["engine"], self.parameters)
        engine_definition = self.parameters["engine"]
        bp.check_required_parameters('engine', ["name"], engine_definition)
        self.assign_engine(engine_definition, self.record_name)
        self.add_service(self.engine)
        params_temp = self.SDPEParameters(self.parameters)
        self.parameters.update(params_temp.get_engine_parameters())

    def assign_engine(self, engine, workload_name: str):
        engine_name = engine["name"].capitalize()
        if engine_name != "Storm" and engine_name != "Spark" and engine_name != "Flink":
            raise Exception("Unsupported engine")

        engine_param = engine["parameters"] if "parameters" in engine else []
        if not "version" in engine["parameters"]:
            engine["parameters"]["version"] = self.engine_default_version[engine_name.lower()]
        self.engine = globals()[engine_name](len(self.cluster), workload_name, engine_param)
