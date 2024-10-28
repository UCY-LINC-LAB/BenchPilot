import os
from workloads.workloadClient import WorkloadClient
from workloads.marketingCampaignWorkloadClient import MarketingCampaignWorkloadClient
from exceptions import WorkloadMissingException

class WorkloadClientFactory:
    """
    This class works as a workload factory, trying to generalize the use of workloads.
    """
    workload: WorkloadClient

    def __init__(self, logger):
        # set workload
        if not ("workload" in os.environ):
            raise WorkloadMissingException
        workload_env = os.environ["workload"]
        if "marketing-campaign" in workload_env:
            self.workload = MarketingCampaignWorkloadClient(logger)
