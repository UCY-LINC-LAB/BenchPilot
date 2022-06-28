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
|<span style="color: #40897B">marketing-campaign</span>| A streaming distributed workload that features an application as a data processing pipeline with multiple and diverse steps that emulate insight extraction from marketing campaigns. The workload utilizes technologies such as Kafka and Redis. | <ul><li><i>campaigns</i>, which is the number of campaigns, the default number is 1000,</li> <li><i>tuples_per_second</i>, the number of emitted tuples per second, the default is 10000</li> <li><i>kafka_event_count</i>, the number of generated and published events on kafka, the default is 1000000</li> <li><i>maximize_data</i>, this attribute is used to automatically maximize the data that are critically affecting the workload's performance, the input that the user can put is in the format of x10, x100, etc.</li></ul>

## <strong>Distributed Processing Engine Parameters</strong>
In the case of streaming distributed workloads, the user needs to define specific engine parameters in their experiments. 

For each Streaming Distributed Processing Engine, the following attributes can be specified:
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

<strong>It's important to note that BenchPilot can be easily extended to add new workloads.</strong> 

For extending BenchPilot check this <a href="https://ucy-linc-lab.github.io/BenchPilot/docs/getting-framework/">section</a> out.