---
title: "Experiments"
weight: 3
# bookFlatSection: false
# bookToc: true
# bookHidden: false
# bookCollapseSection: false
# bookComments: false
# bookSearchExclude: false
---
# <strong style="color: #40897B">Experiments</strong>
Before starting the benchmarking process, you need to define (i) <strong style="color: #40897B">the cluster</strong> under test, and (ii) <strong style="color: #40897B">the experiments</strong> you want to perform.

## Defining your Cluster
By defining you cluster, Benchpilot removes the effort of you needing to download docker, docker compose and every docker image you may need for your benchmarking on your worker devices. All you need to do is define your cluster inside the <em>/BenchPilotSDK/conf/bench-cluster.yaml</em>.

Inside the "bench-cluster.yaml" we define our cluster nodes. So as we can see below, we define our cluster with the keywoard "<strong style="color: #40897B">cluster</strong>", and afterwards we define each worker with the keyword "<strong style="color: #40897B">node</strong>".

For each worker, it is needed to define their <strong style="color: #40897B">ip</strong>, <strong style="color: #40897B">hostname</strong>, and <strong style="color: #40897B">authentication credentials</strong>. These credentials include the <strong style="color: #40897B">username</strong>, and <strong style="color: #40897B">password</strong> or the <strong style="color: #40897B">path to an ssh key</strong>.

On each node there is also the option to <strong style="color: #40897B">skip the orchestration setup</strong>. For example, if in an experiment we use Docker Swarm as our orchestrator, and that node is already registered as a worker in our swarm, then it will skip the registration process.
````yaml
cluster:
  - node:
      ip: "xx.xx.xx.xx"
      hostname: "raspberrypi0"
      username: "your_username"
      password: "your_password"
      orchestrator_setup: "false"
  - node:
      ip: "xx.xx.xx.xx"
      hostname: "server0"
      username: "your_username"
      ssh_key_path: "/BenchPilotSDK/conf/ssh_key.pem" # this is an example of ssh key path
  ..

````
** Please keep in mind that every hostname and ip you declare needs to be accessible by the node you will run the BenchPilot client on. 

## Defining your Experiments
After defining our cluster, our final step before starting the benchmarking process is to define our experiments! All you need to is define them inside the <em>/BenchPilotSDK/conf/bench-experimens.yaml</em> file using the BenchPilot Model. 

The <em>BenchPilot model</em> is composed with <strong style="color: #40897B">experiments</strong>, where <strong style="color: #40897B">workloads</strong> are described.

For each <em>workload</em>, you have to define the following:
- <strong style="color: #40897B">name</strong>, which will be selected from the supported <a href="https://ucy-linc-lab.github.io/BenchPilot/docs/workloads/">workload list</a>, e.g. "marketing-campaign",
- <strong style="color: #40897B">record name</strong>, so that you can later on retrieve monitoring metrics based on it,
- number of <strong style="color: #40897B">repetitions</strong>, 
- workload <strong style="color: #40897B">duration</strong>, 
- specific workload <strong style="color: #40897B">parameters</strong>, 
- <strong style="color: #40897B">cluster</strong> under test, including the control plane's node public IP, and the list of the worker nodes' hostnames,
- <strong style="color: #40897B">engine</strong> configurations, in case of streaming distributed-based workloads

An example of the <em>bench-experimens.yaml</em> can be found below:

````yaml
experiments:
  - workload:
      name: "marketing-campaign"
      record_name: "storm_x1"
      repetition: 1
      duration: "10m"
      parameters:
        campaigns: 100
        tuples_per_second: 1000
        capacity_per_window: 10
        time_divisor: 10000
      cluster:
        manager: "xx.xx.xx.xx" # control-plane node public ip
        nodes: [ "raspberrypi0", "server0" ] # workers' hostnames
        # define http(s)_proxy only if your BenchPilot client is placed behind a proxy
        http_proxy: "${http_proxy}"
        https_proxy: "${https_proxy}"
      engine:
        name: "storm"
        parameters:
          partitions: 5
          ackers: 2
  - workload:
      name: "marketing-campaign"
      record_name: "flink_x1"
      repetition: 5
      duration: "30m"
        ..

````
** BenchPilot will run the experiments with the order you described them.