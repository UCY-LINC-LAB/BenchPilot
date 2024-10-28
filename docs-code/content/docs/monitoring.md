---
title: "Monitoring"
weight: 5
# bookFlatSection: false
# bookToc: true
# bookHidden: false
# bookCollapseSection: false
# bookComments: false
# bookSearchExclude: false
---
# <strong style="color: #40897B">BenchPilot Monitoring System</strong>
BenchPilot Monitoring divides its services on the **Control Plane**, where BenchPilot Client and core monitoring services will run on, and its **workers**, where the benchmarking will happen.

On the **Control Plane**, BenchPilot reuses the following existing projects:
* *[Consul](https://www.consul.io/)*, for service registration
* *[Prometheus](https://prometheus.io/)*, for keeping metrics
* *[Influxdb](https://www.influxdata.com/)*, for long-term storing metrics

On each **Worker** device, BenchPilot uses *[Netdata](https://www.netdata.cloud/)* for capturing its metrics, and *[meross smart plugs](https://www.meross.com/en-gc/product)* for retrieving energy consumption. You can use any smart plug you wish for capturing energy consumption by exposing its measures to Netdata. Additionally, since we've been recently experimenting on co-located scenarios, we decided to expose *[cadvisor](https://github.com/google/cadvisor)* metrics to netdata, as to retrieve metrics per docker container (benchmark service). 

You can find everything that you might need for the the monitoring stack in our repository, under the <code>monitoring</code> folder.

## <strong>Setup Monitoring System</strong>
First of all, you need to download or clone our <a href="https://github.com/UCY-LINC-LAB/BenchPilot">GitHub Repository</a>.

### <strong>Install Docker & Docker Compose</strong>
If you haven't installed docker and docker-compose on your devices yet (control plane & workers), just execute the following command on each one of them: 
````
sh install-docker.sh
````

### <strong>Start Control-Plane Services</strong>
When you have docker and docker-compose installed, all you need to run on the **Control Plane** is the following command:
````
docker-compose up -f docker-compose-monitoring.yaml
````
*Don't forget to replace the environment variables however you would wish to (e.g. "${database_name}")*

### <strong>Start Worker Services</strong>
On each **Worker** you can start and setup Netdata by just running:
````
docker-compose up -f docker-compose.yaml
````
*If you will not use any kind smart plugs, just comment-out the smart plug docker service, otherwise, please update (i) your meross account's information and (ii) the smart plug's unique name/number.*


#### <strong>Changing smart plug configuration</strong>
There are two things needed for this process:
1) First you should <strong style="color: #40897B">remove/change the "smart-plug" service</strong> from docker-compose.yaml
2) <strong style="color: #40897B">Update the netdata/prometheus.conf</strong>. You should update accordingly the "smart_plug" configuration, which is defined in the end of the "prometheus.conf". This setup is responsible for exposing the power consumption measurements to netdata.

#### <strong>Register Worker nodes to Consul</strong>
After you have started the worker services, on each worker, enter the **<code>Consul</code>** folder and execute the following command:
````
sh register_to_consul.sh
````
*Please, don't forget to replace the IPs and ports in the script(Consul Ip & Port, worker device IP and netdata port)*