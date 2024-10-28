import requests
from abc import abstractmethod
from time import sleep
from BenchPilotSDK.workloads import Workload


class ClientBasedWorkload(Workload):

    def __init__(self, **workload_definition):
        super().__init__(**workload_definition)
        self.workload_client_url = 'http://' + self.record_name + '-client:5000/api/v1'

    def submit_workload(self):
        parameters = {"parameters": self.parameters}
        submitted_workload = False
        # adding session variable in order to override proxies
        session = requests.Session()
        session.trust_env = False
        while not submitted_workload and self.workload_timeout < 180:
            response = session.post(self.workload_client_url + '/workload/', json=parameters)
            self.logger.debug(response.text)
            self.workload_timeout += 1
            if response.status_code == 200:
                submitted_workload = True

        if self.workload_timeout >= 180:
            self.logger.error("Workload client not running")
            self.loader.stop()
            raise Exception("Workload Client is not running")

        self.workload_timeout = 0
        # check if workload has started
        while self.__workload_has_started() == -1 and self.workload_timeout < 180:
            self.workload_timeout += 1

        if self.workload_timeout >= 180:
            self.logger.error('Workload timeout')
            self.loader.stop()
            raise Exception("Workload Client Timeout")

    def wait_workload_to_finish(self):
        workload_is_running = True
        self.logger.info("-- Waiting for workload to finish --")
        # adding session variable in order to override proxies
        session = requests.Session()
        session.trust_env = False
        while workload_is_running:
            response = session.get(self.workload_client_url + '/workload-status/')
            if 'Job still running' in response.text:
                continue
            else:
                workload_is_running = False
                self.logger.info('Workload Finished')

        self.declare_workload_as_finished()

    def stop_workload(self):
        session = requests.Session()
        session.trust_env = False
        try:
            response = session.post(self.workload_client_url + '/stop-workload/')
            self.logger.debug(response.text)
        except requests.exceptions.ConnectionError:
            print("client error...")
        # wait a bit before ending experiment
        sleep(60)
        super().stop_workload()

    def __workload_has_started(self):
        sec_waiting = 0
        job_not_started = True
        session = requests.Session()
        session.trust_env = False
        while job_not_started:
            response = session.get(self.workload_client_url + '/workload-status/')
            if "No job is currently running" in response.text:
                if sec_waiting < 180:
                    # wait for 1 sec and retry
                    self.logger.info("Waiting 1 seconds to retry to check if workload has started")
                    sleep(1)
                    sec_waiting += 1
                else:
                    self.logger.error("Workload timeout")
                    return -1
            else:
                self.logger.info("Workload has started")
                return 0
