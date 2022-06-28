from abc import ABC

from BenchPilotSDK.services.sdpe.engines import *
from BenchPilotSDK.services.sdpe.engine import Engine
from BenchPilotSDK.workloads.workload import Workload


class SDPEWorkload(Workload, ABC):
    """
    This class extends workload and adds the assign engine method in order to be able to assign
    a specific streaming distributed processing engine
    """
    engine: Engine

    def __init__(self, workload_yaml, workload_name: str):
        super().__init__(workload_yaml)
        self.workload_setup.check_required_parameters('workload', ["engine"], workload_yaml)
        self.workload_setup.check_required_parameters('engine', ["name"], workload_yaml["engine"])
        self.assign_engine(workload_yaml["engine"]["name"], workload_name)
        self.services.append(self.engine)

    def assign_engine(self, engine: str, workload_name: str):
        if not engine is None:
            if "spark" in engine.lower():
                self.engine = Spark(len(self.nodes), self.manager_ip, workload_name)
            elif "storm" in engine.lower():
                self.engine = Storm(len(self.nodes), self.manager_ip, workload_name)
            elif "flink" in engine.lower():
                self.engine = Flink(len(self.nodes), self.manager_ip, workload_name)
