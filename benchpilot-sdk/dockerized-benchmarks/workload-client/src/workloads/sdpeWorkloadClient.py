import os, requests, json
from abc import ABC
from exceptions import *
from workloads.workloadClient import WorkloadClient, WorkloadSetup

class Client:
    url: str
    job_name: str
    job_name_key: str
    running_key: str
    status_key: str

    def __init__(self, url, url_overview, overview_key, job_name, job_name_key, running_key, status_key):
        self.url = url
        self.overview_url = self.url + url_overview
        self.overview_key = overview_key
        self.job_name = job_name
        self.job_name_key = job_name_key
        self.job_id = "id"
        self.running_key = running_key
        self.status_key = status_key


class FlinkClient(Client):
    """
    This class represents the Flink Client. Holds all necessary attributes for interacting with flink ui and apis
    """

    def __init__(self):
        super().__init__(url='/jobs/', url_overview="overview", overview_key="properties.jobs", job_name='Flink Streaming Job', job_name_key='name', 
                         running_key="RUNNING", status_key="state")


class StormClient(Client):
    """
    This class represents the Storm Client. Holds all necessary attributes for interacting with storm ui and apis
    """

    def __init__(self):
        super().__init__(url='/api/v1/topology/', url_overview="summary", overview_key="topologies", job_name='streaming-topology', 
                         job_name_key='name', running_key="ACTIVE", status_key="status")


class SparkClient(Client):
    """
    This class represents the Spark Client. Holds all necessary attributes for interacting with spark ui and apis
    """

    # TODO: don't know the schema of spark, hence not sure if I sould be selecting "applications"
    def __init__(self):
        super().__init__(url='/api/v1/', url_overview="applications", overview_key="applications", job_name='KafkaRedisAdvertisingStream', 
                         job_name_key='name', running_key="FALSE", status_key="completed")


class SDPEWorkloadClient(WorkloadClient, ABC):
    client: Client

    def __init__(self, logger):
        super().__init__(logger)
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

    def is_job_still_running(self, get_id=False):
        session = requests.Session()
        session.trust_env = False
        response = session.get('http://' + self.ui_hostname + ':' + self.ui_port + self.client.overview_url)
        if response.status_code != 200:
            raise UiNotFoundException

        if not (self.client.job_name in response.text):
            return self.no_running_json

        response_json = json.loads(response.text)
        
        for key in self.client.overview_key.split("."):
            response_json = response_json[key]

        for job in response_json:
            if self.client.job_name in job[self.client.job_name_key]:
                if get_id:
                    return job["id"]
                elif self.client.running_key in job[self.client.status_key].upper():
                    return self.running_json
                else:
                    return self.no_running_json
    
    def print_job_statistics(self):
        session = requests.Session()
        session.trust_env = False
        response = session.get('http://' + self.ui_hostname + ':' + self.ui_port + self.client.url + self.is_job_still_running(get_id=True))
        if response.status_code != 200:
            raise UiNotFoundException

        if not (self.client.job_name in response.text):
            return self.no_running_json
        
        self.logger.info(response.text)


class SDPEWorkloadSetup(WorkloadSetup, ABC):

    def __init__(self):
        super().__init__()