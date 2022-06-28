import os, requests, json
from abc import ABC

from exceptions import *
from workloads.setup.sdpeWorkloadSetup import SDPEWorkloadSetup
from workloads.workloadClient import WorkloadClient

class Client:
    url: str
    job_name: str
    job_name_key: str
    running_key: str
    status_key: str

    def __init__(self, url, job_name, job_name_key, running_key, status_key):
        self.url = url
        self.job_name = job_name
        self.job_name_key = job_name_key
        self.running_key = running_key
        self.status_key = status_key


class FlinkClient(Client):
    """
    This class represents the Flink Client. Holds all necessary attributes for interacting with flink ui and apis
    """

    def __init__(self):
        super().__init__(url='/jobs/overview', job_name='', job_name_key='id', running_key="RUNNING",
                         status_key="state")


class StormClient(Client):
    """
    This class represents the Storm Client. Holds all necessary attributes for interacting with storm ui and apis
    """

    def __init__(self):
        super().__init__(url='/api/v1/topology/summary', job_name='streaming-topology', job_name_key='name',
                         running_key="ACTIVE", status_key="status")


class SparkClient(Client):
    """
    This class represents the Spark Client. Holds all necessary attributes for interacting with spark ui and apis
    """

    def __init__(self):
        super().__init__(url='/api/v1/applications', job_name='KafkaRedisAdvertisingStream', job_name_key='name',
                         running_key="FALSE", status_key="completed")


class SDPEWorkloadClient(WorkloadClient, ABC):
    client: Client

    def __init__(self):
        super().__init__()
        self.setup = SDPEWorkloadSetup()
        # set engine
        if not ("engine" in os.environ):
            raise EngineMissingException

        self.engine = os.environ["engine"]
        if "flink" in self.engine:
            self.client = FlinkClient()
        elif "storm" in self.engine:
            self.client = StormClient()
        else:
            self.client = SparkClient()

        # set ui hostname and port
        if not ("ui_hostname" in os.environ) or not ("ui_port" in os.environ):
            raise UiHostnameAndPortMissingException
        self.ui_hostname = os.getenv('ui_hostname')
        self.ui_port = os.getenv('ui_port')

    def is_job_still_running(self):
        response = requests.get('http://' + self.ui_hostname + ':' + self.ui_port + self.client.url)
        if response.status_code != 200:
            raise UiNotFoundException
        if not (self.client.job_name in response.text):
            return self.no_running_json

        response_json = json.loads(response.text)
        if self.engine == 'storm':
            response_json = response_json["topologies"]

        for job in response_json:
            if self.client.job_name in job[self.client.job_name_key]:
                if self.client.running_key in job[self.client.status_key].upper():
                    return self.running_json
                else:
                    return self.no_running_json
