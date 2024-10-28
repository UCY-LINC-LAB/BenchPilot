---
title: "Workloads"
weight: 4
# bookFlatSection: false
# bookToc: true
# bookHidden: false
# bookCollapseSection: false
# bookComments: false
# bookSearchExclude: false
---
# <strong style="color: #40897B">Workloads</strong>
As for now BenchPilot only supports the following containerized workloads:
|Name|Description|Specific Configuration Parameters|
|----|-----------|---------------------------------|
|<span style="color: #40897B">[marketing-campaign](#ysb)</span>| A streaming distributed workload that features an application as a data processing pipeline with multiple and diverse steps that emulate insight extraction from marketing campaigns. The workload utilizes technologies such as [Kafka](https://kafka.apache.org/) and [Redis](https://redis.io/). | <ul><li><i>campaigns</i>, which is the number of campaigns, the default number is 1000.</li><li><i>tuples_per_second</i>, the number of emitted tuples per second, the default is 10000.</li> <li><i>kafka_event_count</i>, the number of generated and published events on kafka, the default is 1000000.</li> <li><i>maximize_data</i>, this attribute is used to automatically maximize the data that are critically affecting the workload's performance, the input that the user can put is in the format of x10, x100, etc.</li></ul>
|<span style="color: #40897B">[mlperf](#mlperf)</span>| An inference workload, that includes tasks such as image classification and object recognition.| <ul><li><i>dataset_folder</i>, which is the dataset folder, the one we have been using for our experiments is the imagenet2012,</li> <li><i>model_file</i>, the model file that the mlperf will use for inferencing the images, for e.g. resnet50_v1.pb</li><li><i>profile</i>, the mlperf's profile, e.g. resnet50-tf</li> <li><i>data_volume_path</i>, the path that will be used to volume the data from, this is done as to not avoid creating huge workload images, and due to having easier configuration</li></ul>
|<span style="color: #40897B">[db](#ycsb)</span>|A nosql database workload that keeps executing CRUD operations (Create, Read, Update and Delete).|<ul><li><i>db</i>, the database that will be used as the underlying once, for now, only mongodb is supported.</li><li><i>threads</i>, the number of threads to be used for executing the operations. The default number of threads is 1.</li><li><i>record_count</i>, the number of records that will be loaded as a starting dataset into the database. The default number is 2500000.</li> <li><i>operation_count</i>, the number of operations that will be executed during the workload - this can affect the time that the experiment will need to finish. The default number is 2500000.</li> <li><i>read_proportion</i>, this is a float number, that represents that percentage of read operations to be executed during the benchmark, the default is 0.5</li>  <li><i>update_proportion</i>, this is a float number, that represents that percentage of update operations to be executed during the benchmark, the default is 0.5</li>  <li><i>scan_proportion</i>, the percentage of read operations to be executed during the experiment. The default is 0.</li> <li><i>insert_proportion</i>, the proportion of insert operations to be executed. The default is 0.</li> <li><i>request_distribution</i>, the distribution of the pattern of data access. The default is zipfian.</li></ul>
|<span style="color: #40897B">simple</span>| This workload represents simple stressors that target a specific resource to stress. Underneath uses the linux command [stress](https://linux.die.net/man/1/stress) or [IPerf3](https://man.archlinux.org/man/iperf3.1.en). | <ul><li><i>service</i>, which can be either iperf3 or stress </li><li><i>options</i>, here you need to define the options as you would insert them while using the iperf3 or stress command. For e.g. for iperf3, the options should be "-c" to set the client's ip, or "-s" for the server ip, and "-p" for setting the targeted port. In case, of selecting stress, the options could be for example "--vm": "12", and "--vm-bytes": "1024M".</li></ul>

<strong>It's important to note that BenchPilot can be easily extended to add new workloads.</strong> 

For extending BenchPilot check this <a href="https://ucy-linc-lab.github.io/BenchPilot/docs/getting-framework/">section</a> out.

## <strong>Detailed Workload Information</strong>

### <strong id="ysb">Streaming Analytic Workload / Marketing-Campaign</strong>
For this workload, we have employed the widely known [Yahoo Streaming Benchmark](https://github.com/yahoo/streaming-benchmarks), which is designed to simulate a data processing pipeline for extracting insights from marketing campaigns. the pipeline executed on the edge device includes steps such as receiving advertising traffic data, filtering the data, removing any unnecessary values, combining the data with existing information from a key-value store, and storing the final results. All data produced by a data generator is pushed and extracted through a message queue ([Apache Kafka](https://kafka.apache.org/)), while intermediate data and final results are stored in an in-memory database ([Redis](https://redis.io/)).
This workload can be executed using any of the following distributed streaming processing engines: [Apache Storm](https://storm.apache.org/), [Flink](https://flink.apache.org/), [Spark](https://spark.apache.org/). 

#### <strong>Collected Performance Metrics</strong>
For evaluating <strong>the performance of this application</strong>, we extract the following measurements from the benchmarking log files:
<table>
  <tr align="center" style="border-bottom: 0.5px solid grey">
    <th style="border-right: 1px solid white; border-bottom: 0.5px solid white">Metric</th>
    <th style="border-bottom: 0.5px solid white">Description</th>
  <tr>
    <td><strong># of Tuples</strong></td>
    <td>The total number of tuples processed during execution</td>
  </tr>
  <tr>
    <td><strong>Latency</strong></td>
    <td>The total application latency, measured in ms, based on the statistics provided by the selected underlying processing engine for each deployed task</td>
  </tr>
</table>

#### <strong>Distributed Processing Engine Parameters</strong>
As mentioned, this workload can be executed using any of the following streaming distributed processing engines: Apache Storm, Flink or Spark. 

For each of those engine, the user can alter/define the following attributes:
<table style="overflow: visible" >
  <tr align="center" style="border-bottom: 0.5px solid grey">
    <th style="border-right: 1px solid white; border-bottom: 0.5px solid white">Engine</th>
    <td style="border-bottom: 0.5px solid white; color: #40897B"><strong>Storm</strong></td>
    <td style="border-bottom: 0.5px solid white; color: #40897B"><strong>Flink</strong></td>
    <td style="border-bottom: 0.5px solid white; color: #40897B"><strong>Spark</strong></td>
  </tr>
  <tr>
    <th style="border-right: 1px solid white; border-bottom: none">Parameters</th>
    <td><ol><li>partitions</li><li>ackers</li></ol></td>
    <td><ol><li>partitions</li><li>buffer_timeout</li><li>checkpoint_interval</li></ol></td>
    <td><ol><li>partitions</li><li>batchtime</li><li>executor_cores</li><li>executor_memory</li></ol></td>
  </tr>
</table>

### <strong id="mlperf">Machine Learning Inference Workload / MLPerf</strong>

We use [MLPerf](https://github.com/mlcommons/inference), a benchmark for machine learning training and inference, to assess the performance of our inference system. Currently, our focus is on two MLPerf tasks:
- <strong>Image Classification:</strong> This task uses the ImageNet 2012 dataset (resized to 224x224) and measures Top-1 accuracy. MLPerf provides two model options: ResNet-50 v1.5, which excels in image classification, and RetinaNet, which is effective in object detection and bounding box prediction.
- <strong>Object Detection:</strong> This task identifies and classifies objects within images, locating them with bounding boxes. MLPerf uses two model configurations: a smaller, 300x300 model for low-resolution tasks (e.g., mobile devices) and a larger, high-resolution model (1.44 MP). Performance is measured by mean average precision (mAP). The SSD model with a ResNet-34 backbone is the default for this task.

Additionally, we have extended MLPerf by adding network-serving capabilities to measure the impact of network overhead on inference. Our setup includes:

- A lightweight server that loads models and provides a RESTful API.
- A workload generator that streams images to the server one-by-one (“streaming mode”), contrasting with MLPerf's standard local loading (“default mode”).

For this workload, it is possible to flexibly and easily configure the dataset, latency, batch size, workload duration, thread count, and inference framework (ONNX, NCNN, TensorFlow, or PyTorch).
#### <strong>Collected Performance Metrics</strong>
For evaluating <strong>the performance of this application</strong>, we extract the following measurements from the benchmarking log files:
<table>
  <tr align="center" style="border-bottom: 0.5px solid grey">
    <th style="border-right: 1px solid white; border-bottom: 0.5px solid white">Metric</th>
    <th style="border-bottom: 0.5px solid white">Description</th>
  <tr>
    <td><strong>Accuracy %</strong></td>
    <td>The model's accuracy that was measured during the benchmarking period</td>
  </tr>
  <tr>
    <td><strong>Average and/or Total Queries per Second</strong></td>
    <td>The # of queries that were executing during the experiment - each query represents the processing a batch of images</td>
  </tr>
  <tr>
    <td><strong>Mean Latency</strong></td>
    <td>The application's mean latency, measured in ms</td>
  </tr>
</table>

### <strong id="ycsb">NoSQL Database Workload</strong>
Through the [Yahoo! Cloud Serving Benchmark (YCSB)](https://github.com/brianfrankcooper/YCSB) workload, one can evaluate NoSQL databases like MongoDB, Redis, Cassandra, and Elasticsearch under heavy load. YCSB tests basic operations—read, update, and insert—on each database using defined operation rates across an experiment’s duration.
Currently, BenchPilot only supports MongoDB as the underlying database. However, it can be easily adapted to the rest of the databases by containerizing them.

Additionally, YCSB supports three workload distributions:
- <strong>Zipfian:</strong> Prioritizes frequently accessed items.
- <strong>Latest:</strong> Similar to Zipfian but focuses on recently inserted records.
- <strong>Uniform:</strong> Accesses items randomly.

For this benchmark, users can adjust various parameters, including the number of records, total operations, load distribution, operation rate, and experiment duration. It also supports multiple threads for increased database load through asynchronous operations.

#### <strong>Collected Performance Metrics</strong>
For evaluating <strong>the performance of this application</strong>, we can extract the following measurements from the log files:
<table>
  <tr align="center" style="border-bottom: 0.5px solid grey">
    <th style="border-right: 1px solid white; border-bottom: 0.5px solid white">Metric</th>
    <th style="border-bottom: 0.5px solid white">Description</th>
  <tr>
    <td><strong>Count</strong></td>
    <td>Total number of operations per second for each minute of the experiment</td>
  </tr>
  <tr>
    <td><strong>Min</strong></td>
    <td>Min number of operations per second for each minute of the experiment</td>
  </tr>
  <tr>
    <td><strong>Max</strong></td>
    <td>Max number of operations per second for each minute of the experiment</td>
  </tr>
    <tr>
    <td><strong>Average</strong></td>
    <td>Average number of operations per second for each minute of the experiment</td>
  </tr>
</table>