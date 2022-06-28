---
title: "Post-Experiment Analysis"
weight: 6
---
# <strong style="color: #40897B">Post-Experiment Analysis</strong>
After running all of our experiments, it's time to view our results! 

## Jupyter
For your ease of accessing and processing the results, we used Jupyter Notebook. 

## Prometheus Client
We have created under /utils package a prometheus client. You can always retrieve your experiment results by calling the "<strong style="color: #40897B">get_benchmark_results</strong>" method, or export them in a csv format with the "<strong style="color: #40897B">xport_results_to_csv</strong>" method.

*Please remember to use the methods "assign_prometheus_prefix" and "assign_prometheus_suffix" in order to assign your prometheus' prefixes and suffixes.*

For more information about Jupyter, please visit their <a href="https://jupyter.org/">website</a>.