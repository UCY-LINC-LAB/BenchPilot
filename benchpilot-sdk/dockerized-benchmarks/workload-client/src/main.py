""" This is the BenchPilot's REST API, its purpose is to start the workloads by submitting the jobs """
import json
from flask import Flask, request
from workloads.workloadClient import WorkloadClient
from workloads.workloadClientFactory import WorkloadClientFactory

# Create the application instance
app = Flask(__name__)
app.config["DEBUG"] = True
path = '/api/v1'
workload: WorkloadClient
###########################################################

workload = WorkloadClientFactory().workload

"""
This method returns returns if the job is still running or not.
"""
@app.route(path, methods=['GET'])
def is_job_still_running():
    return workload.is_job_still_running()


"""
This method returns in a json format workload's latency
"""
@app.route(path + "/workload-collected-info/", methods=['GET'])
def get_workload_collected_info(timestamp):
    return workload.get_workload_collected_info(timestamp)


"""
This method returns all of the workloads' timestamps have been executed till now
"""
@app.route(path + "/available-starting-workload-timestamps", methods=['GET'])
def get_available_benchmark_timestamps():
    return json.dumps({'status': 'success', 'workload-starting-timestamps': workload.workload_record}), 200, {
        'ContentType': 'application/json'}


"""
With this method, entities submit the job.
"""
@app.route(path + '/<starting_timestamp>', methods=['POST', 'PUT'])
def start_workload(starting_timestamp):
    body = request.get_json()
    return workload.start_workload(starting_timestamp, body)


"""
Method to force stop the job
"""
@app.route(path, methods=['DELETE'])
def delete_request():
    return workload.stop_workload()


app.run(host='0.0.0.0')
