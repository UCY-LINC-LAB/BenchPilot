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

On each **Worker** device, BenchPilot uses *[Netdata](https://www.netdata.cloud/)* for capturing its metrics, and meross smart plugs for retrieving energy consumption. You can use any smart plug you wish for capturing energy consumption by exposing its measures to Netdata. 

Every file that you may need for the monitoring stack, you can find in our repository, under the "monitoring" folder.

## <strong>Setup Monitoring System</strong>
First of all you need to download or clone our <a href="https://github.com/UCY-LINC-LAB/BenchPilot">GitHub Repository</a>.

### <strong>Install Docker & Docker Compose</strong>
If you haven't installed docker and docker-compose on your devices yet (control plane & workers), just execute the following command on each one of them: 
````
sh install-docker.sh
````

### <strong>Start Control-Plane Services</strong>
When you have docker and docker-compose installed, all you need to run on the **Control Plane** the following command:
````
docker-compose up -f docker-compose-monitoring.yaml
````
*Don't forget to replace the environment variables however you would wish to (e.g. "${database_name}")*

### <strong>Start Worker Services</strong>
On each **Worker** you can start and setup Netdata by just running:
````
docker-compose up -f docker-compose.yaml
````
*Keep in mind, that you need to define the smart plug's ip.*


#### <strong>Changing smart plug configuration</strong>
There are two things needed for this process:
1) First you should <strong style="color: #40897B">remove/change the "smart-plug" service</strong> from docker-compose.yaml
2) <strong style="color: #40897B">Update the netdata/prometheus.conf</strong>. You should update accordingly the "smart_plug" configuration, which is defined in the end of the "prometheus.conf". This setup if for exposing its metrics to netdata.

#### <strong>Register Worker nodes to Consul</strong>
On each worker, after you have started the worker services, just enter the **Consul** folder and execute the following command:
````
sh consul/register_to_consul.sh
````
*Please, don't forget to replace the IPs in the script with your IPs (Consul Ip, and worker device IP)*