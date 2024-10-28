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

Inside the "bench-cluster.yaml" we define our cluster nodes. So as we can see below, we define our cluster with the keywoard "<strong style="color: #40897B">cluster</strong>", and afterwards we define the manager, where the benchpilot client will be deployed on, and the nodes that are represented as workers.

For all nodes, it is needed to define their <strong style="color: #40897B">ip</strong>, and proxy - if needed, and for each worker it's required to define their <strong style="color: #40897B">hostname</strong>, and <strong style="color: #40897B">authentication credentials</strong>. These credentials include the <strong style="color: #40897B">username</strong>, and <strong style="color: #40897B">password</strong> or the <strong style="color: #40897B">path to an ssh key</strong>.

````yaml
cluster:
  manager:
      ip: "0.0.0.0" # assign the IP of the device that will run the benchpilot client
      # in case of not using a proxy - remove the following 3 lines
      proxies:
        http_proxy: "http://example.proxy.com:8080/"
        https_proxy: "https://example.proxy.com:8080/"
  nodes: # here define the nodes that you will benchmark
    - ip: "10.10.10.10" # example of ip
      hostname: "raspberrypi"
      username: "pi"
      password: "raspberrypi"
    - ip: "10.11.11.11" # another example using ssh key
      hostname: "old_server"
      username: "ubuntu"
      ssh_key_path: "BenchPilotSDK/conf/ssh_keys/ssh_key.pem" 
      proxies: # if your device is placed behind a proxy you should also include these
        http_proxy: "http://example.proxy.com:8080/"
        https_proxy: "https://example.proxy.com:8080/"
  ..

````
** Please keep in mind that every hostname and ip you declare needs to be accessible by the node you will run the BenchPilot client on. 

## Defining your Experiments
After defining our cluster, our final step before starting the benchmarking process is to define our experiments! All you need to is define them in a yaml file under <em>/BenchPilotSDK/conf/</em> using the BenchPilot Model. 

The <em>BenchPilot model</em> is composed with <strong style="color: #40897B">experiments</strong>, where each experiments consists of <strong style="color: #40897B">workload</strong> descriptions.

For each <em>experiment</em>, you have to define the following:
- <strong style="color: #40897B">record_name</strong>, so that you can later on retrieve monitoring metrics based on it,
- number of <strong style="color: #40897B">repetitions</strong> that the experiment will be conducted.
- the <strong style="color: #40897B">duration</strong> of the whole experiment.

On the other hand, every <em>workload</em>, needs to have the following descriptions:
- <strong style="color: #40897B">name</strong>, which will be selected from the supported <a href="https://ucy-linc-lab.github.io/BenchPilot/docs/workloads/">workload list</a>, e.g. "marketing-campaign".
- <strong style="color: #40897B">cluster</strong>, which consists the list of resources that will be used as workers to deploy the workload.
- <strong style="color: #40897B">orchestrator</strong>, this is optional. One can define the underlying orchestrator that will be used for the deployment, the default is docker swarm.
- <strong style="color: #40897B">duration</strong>: This parameter specifies the length of time that a particular workload will be deployed. It is important that this duration exceeds the duration of the experiment. Alternatively, you can simply enter "default" if preferred.
- specific workload <strong style="color: #40897B">parameters</strong>: you can find more information regarding the parameters <a href="https://ucy-linc-lab.github.io/BenchPilot/docs/workloads/">here</a>.

An example of the <em>/BenchPilotSDK/conf/demo.yaml</em> can be found below:

````yaml
idle_between_experiments: "2m"
experiments:
  - experiment:
      record_name: "mlStorm_old_server" # name must be < 63 characters
      repetition: 1
      duration: "default"
      workloads:
        - name: "mlperf"
          cluster: ["old_server"] # workers' hostnames
          orchestrator: "swarm"
          duration: "8m"
          parameters:
            dataset_folder: "imagenet2012"
            model_file: "resnet50_v1.onnx"
            profile: "resnet50-onnxruntime"
            data_volume_path: "/mlperf/data"
            model_volume_path: "/mlperf/model"
            output_volume_path: "/mlperf/output"
            worker_threads: 12
        - name: "marketing-campaign"
          cluster: ["old_server"] # workers' hostnames
          duration: "8m"
          parameters:
            num_of_campaigns: 100000
            capacity_per_window: 10000
            kafka_event_count: 100000000
            time_divisor: 10000
            workload_tuples_per_second_emission: 1000000
            engine:
              name: "storm"
              parameters:
                ackers: 2
                executors_per_node: [ 4 ]
                ui_port: "8080"
  - experiment:
      record_name: "mdb_scpu_rpi"
      repetition: 1
      duration: "default"
      workloads:
        - name: "database"
          duration: "20m"
          cluster: [ "raspberrypi" ] # workers' hostnames
          parameters:
            db: "mongodb"
            threads: 12
        - name: "simple"
          cluster: [ "raspberrypi" ] # workers' hostnames
          parameters:
            service: "stress"
            options:
              - "--cpu": "4"
        ..

````
** BenchPilot will run the experiments with the order you described them.