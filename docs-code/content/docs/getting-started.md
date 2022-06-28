---
title: "Getting Started"
weight: 1
# bookFlatSection: false
# bookToc: true
# bookHidden: false
# bookCollapseSection: false
# bookComments: false
# bookSearchExclude: false
---
# <strong style="color: #40897B">BenchPilot</strong>
BenchPilot: Repeatable & Reproducible Benchmarking for Edge Micro-DCs

BenchPilot is a modular and highly customizable benchmarking framework for edge micro-DCs. 
BenchPilot provides a high-level declarative model for describing experiment testbeds and scenarios that automates the benchmarking process on Streaming Distributed Processing Engines (SDPEs). The latter enables users to focus on performance analysis instead of dealing with the complex and time-consuming setup. BenchPilot instantiates the underlying cluster, performs repeatable experimentation, and provides a unified monitoring stack in heterogeneous Micro-DCs. 

<p align="center">
   <img src="./BenchPilot_architecture.png" alt="BenchPilot Architecture" style="width: 70%">
</p> 

### <strong>Experiment Setup</strong>
A typical workflow starts with the user submitting in a yaml file their choice of experiments and their specific parameters.
The BenchPilot model is composed with <i>Experiments</i>, where <i>Workloads</i> are described. Each workload can have the following:
- <strong style="color: #40897B">name</strong>, which will be selected from the supported workload list. 
- <strong style="color: #40897B">record name</strong>, so that the user can later on retrieve its monitored metrics based on it
- <strong style="color: #40897B">number of repetitions</strong>,
- <strong style="color: #40897B">duration</strong>, 
- specific workload <strong>parameters</strong>, 
- <strong style="color: #40897B">cluster</strong> configurations including the manager node's IP, list of cluster nodes, etc. 
- <strong style="color: #40897B">engine</strong> configurations, in case of streaming distributed-based workloads

### <strong>Deployment</strong>
When the description is ready, the user deploys the application using the BenchPilotSDK through a Jupyter notebook.
If there's no validation error from the description, the Parser will parse the preferences to the BenchPilot Deployment Template Generator, where the preferences will be transformed into docker-compose templates. At last, the Deployment Coordinator will deploy each experiment to the underlying orchestrator and closely monitor its performance through the monitoring stack. At the beginning and end of each experiment, the Coordinator records the starting/ending timestamps, so that the user can retrieve the monitored information later on.

### <strong>Monitoring</strong>
For extracting various infrastructure utilization metrics, including CPU, Memory, and Network Utilization, BenchPilot offers a transparent, from the application under test, monitoring stack. To achieve this, BenchPilot, in the bootstrapping stage, instantiates a containerized monitoring agent on every node. The agent inspects system information (e.g., performance pseudofiles and cgroup files) and extracts the required metrics in a non-intrusive way. The agent starts various probes, one for each sub-component (e.g., cgroup probe, OS probe, etc.), and exposes an API through which a centralized monitoring server retrieves the data periodically and stores them to the monitoring storage. Furthermore, the monitoring agent offers probes for external resources as well. From the implementation perspective, we have selected <i><a href="https://www.netdata.cloud/">Netdata</a></i>, a widely known and used monitoring tool, and <i><a href="https://www.prometheus.io/">Prometheus</a></i>, an open-source and popular monitoring server, for our stack. For a monitoring storage backend, <i><a href="https://www.influxdata.com/">InfluxDB</a></i> is used.

### <strong>Post-Experiment Analysis</strong>
To create an end-to-end interactive analytic tool for benchmarking, BenchPilot utilizes the Jupyter Notebook stack. Specifically, after the experimentation process is over, the user can request the monitored metrics of each execution from the monitoring storage based on the provided experiments' starting/ending timestamps. Users can apply high-level analytic models to the retrieved metrics of each experiment and have a clear overview of their deployments. <!--For the latter, BenchPilotSDK stores metrics to an in-memory data structure, namely panda's dataframe, providing exploratory analysis methods that produce plots and summary statistics. -->

### <strong>Workload List</strong>
As for now BenchPilot only supports the following containerized workloads:
|Name|Description|Specific Configuration Parameters|
|----|-----------|---------------------------------|
|<span style="color: #40897B">marketing-campaign</span>| A streaming distributed workload that features an application as a data processing pipeline with multiple and diverse steps that emulate insight extraction from marketing campaigns. The workload utilizes technologies such as Kafka and Redis. | <ul><li><i>campaigns</i>, which is the number of campaigns, the default number is 1000,</li> <li><i>tuples_per_second</i>, the number of emitted tuples per second, the default is 10000</li> <li><i>kafka_event_count</i>, the number of generated and published events on kafka, the default is 1000000</li> <li><i>maximize_data</i>, this attribute is used to automatically maximize the data that are critically affecting the workload's performance, the input that the user can put is in the format of x10, x100, etc.</li></ul>

<strong>It's important to note that BenchPilot can be easily extended to add new workloads.</strong>

## <strong>Resources</strong>

### <strong>The Team</strong>
The creators of the BenchPilot are members of the [Laboratory for Internet Computing (LInC), University of Cyprus](http://linc.ucy.ac.cy/).
You can find more information about our research activity visit our publications' [page](http://linc.ucy.ac.cy/index.php?id=12) and our [on-going projects](http://linc.ucy.ac.cy/index.php?id=13).


### <strong>Acknowledgements</strong>
This work is partially supported by the EU Commission through [RAINBOW](https://rainbow-h2020.eu/)  871403 (ICT-15-2019-2020) project 
and by the Cyprus Research and Innovation Foundation through COMPLEMENTARY/0916/0916/0171 project, and from [RAIS](https://rais-itn.eu/) (Real-time analytics for the Internet of Sports), Marie Skłodowska-Curie Innovative Training Networks (ITN), under grant agreement No 813162.

### <strong>License</strong>
The framework is open-sourced under the Apache 2.0 License base. The codebase of the framework is maintained by the authors for academic research and is therefore provided "as is".

<a href="https://ucy-linc-lab.github.io/BenchPilot/docs/installation/"><strong>Start experimenting by installing Benchpilot now!</strong></span>