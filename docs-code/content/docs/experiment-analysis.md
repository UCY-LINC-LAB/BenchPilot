---
title: "Post-Experiment Analysis"
weight: 6
---
# <strong style="color: #40897B">Post-Experiment Analysis</strong>
After running all of our experiments, it's time to view our results! 

## Jupyter
For your ease of accessing and processing the results, we used Jupyter Notebook. 

## Prometheus Client
We have created under /BenchpilotSDK/controllers package a postExperimentController class. You can export the collected utilization metrics from the prometheus using the following code:
````python
from BenchPilotSDK.controllers.postExperimentController import PostExperimentController

postExpController = PostExperimentController()

exp_name = "Your given record_name of your experiment"
metadata_json_file = "/BenchPilotSDK/experiments/" + exp_name + ".json"
exp_file = "/BenchPilotSDK/conf/" + exp_name + ".yaml"

postExpController.load_benchmark_meta(metadata_json_file)
experiments = postExpController.get_available_workloads_from_metadata()
exported_benchmarks = []
for experiment in experiments:
    exported_benchmarks.append({experiment: postExpController.get_benchmark_metrics(experiment, export_results_to_csv=True)})
````
*Please remember to use the methods "assign_prometheus_prefix" and "assign_prometheus_suffix" in order to assign your prometheus' prefixes and suffixes.*

For more information about Jupyter, please visit their <a href="https://jupyter.org/">website</a>.