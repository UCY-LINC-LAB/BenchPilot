import copy
from abc import ABC
from dataclasses import dataclass
from BenchPilotSDK.workloads.workload import Workload
from BenchPilotSDK.services.materializedServices.mongodb import Mongodb
from BenchPilotSDK.utils.exceptions import BenchExperimentInvalidException


class Database(Workload, ABC):
    """
    This class represents the Database Workload, which is the dockerized YCSB workload
    Please have in mind that as for now, only mongodb is available
    """

    @dataclass
    class Parameters:
        db: str
        threads: int = 1
        duration: str = "1200"
        extra_parameters: str = None

    def __init__(self, **workload_definition):
        super().__init__(**workload_definition)
        self.parameters = self.Parameters(**workload_definition["parameters"])
        service = self.parameters.db
        if service == "mongodb":
            service = Mongodb(self.parameters)
        else:
            raise BenchExperimentInvalidException("The database you defined is not supported")

        # append each service for each node
        for i in range(0, len(self.cluster)):
            new_service = copy.deepcopy(service)
            if not self.duration is "default":
                new_service.add_environment(env_name="DURATION", env_value=str(self.duration))
            new_service.add_environment(env_name="THREADS", env_value=str(self.parameters.threads))
            new_service.hostname = "db_" + str(i)
            self.add_service(new_service)

