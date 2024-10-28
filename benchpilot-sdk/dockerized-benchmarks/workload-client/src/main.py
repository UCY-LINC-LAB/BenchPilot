""" This is the BenchPilot's REST API, its purpose is to start the workloads by submitting the jobs """
import logging
from flask import Flask, request
from workloads.workloadClient import WorkloadClient
from workloads.workloadClientFactory import WorkloadClientFactory

# Create the application instance
app = Flask(__name__)
app.logger.setLevel(logging.INFO)
app.config["DEBUG"] = True
path = '/api/v1'
workload: WorkloadClient
###########################################################

workload = WorkloadClientFactory(app.logger).workload

"""
This method returns returns if the job is still running or not.
"""
@app.route(path + '/workload-status/', methods=['GET'])
def is_job_still_running():
    return workload.is_job_still_running()


"""
This method returns in a json format workload's latency
"""
@app.route(path + '/workload-collected-info/', methods=['GET'])
def get_workload_collected_info(timestamp):
    return workload.get_workload_collected_info(timestamp)


"""
With this method, entities submit the job.
"""
@app.route(path + '/workload/', methods=['POST', 'PUT'])
def start_workload(name:str = ""):
    body = request.get_json()
    return workload.start_workload(name, body)


"""
Method to force stop the job
"""
@app.route(path + '/stop-workload/', methods=['POST'])
def stop_workload():
    return workload.stop_workload()


app.run(host='0.0.0.0')