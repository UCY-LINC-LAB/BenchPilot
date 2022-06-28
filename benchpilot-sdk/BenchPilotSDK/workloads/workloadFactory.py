from BenchPilotSDK.workloads import *
from BenchPilotSDK.workloads.setup.workloadSetup import WorkloadSetup


class WorkloadFactory:
    """
    This class works as a workload factory, trying to generalize the use of workloads.
    """
    workload: Workload
    workloadSetup: WorkloadSetup

    def __init__(self, workload_yaml):
        workloadSetup = WorkloadSetup()
        workloadSetup.check_required_parameters('workload', ["name"], workload_yaml)
        workload_name = workload_yaml["name"].lower()
        if "yahoo" in workload_name or "marketing-campaign" in workload_name:
            self.workload = Yahoo(workload_yaml)
        elif "hibench" in workload_name:
            self.workload = Hibench(workload_yaml)
