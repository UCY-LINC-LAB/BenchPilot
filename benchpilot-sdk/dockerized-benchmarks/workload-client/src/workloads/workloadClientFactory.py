import os
from . import *
from exceptions import WorkloadMissingException

class WorkloadClientFactory:
    """
    This class works as a workload factory, trying to generalize the use of workloads.
    """
    workload: WorkloadClient

    def __init__(self):
        # set workload
        if not ("workload" in os.environ):
            raise WorkloadMissingException
        workload_env = os.environ["workload"]
        if "yahoo" in workload_env or "marketing-campaign" in workload_env:
            self.workload = YahooWorkloadClient()
