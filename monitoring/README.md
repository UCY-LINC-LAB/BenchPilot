# <strong>BenchPilot Monitoring</strong>

BenchPilot Monitoring devides its services on the **Control Plane**, where BenchPilot Client and core monitoring services will run on, and its **workers**, where the benchmarking will happen.

On the **Control Plane**, BenchPilot reuses the following existing projects:
* *[Consul](https://www.consul.io/)*, for service registration
* *[Prometheus](https://prometheus.io/)*, for keeping metrics
* *[Influxdb](https://www.influxdata.com/)*, for long-term storing metrics

On each **Worker** device, BenchPilot uses *[Netdata](https://www.netdata.cloud/)* for capturing its metrics, and meross smart plugs for retrieving energy consumption. You can use whatever device you wish for capturing energy consumption by exposing its measures to Netdata. 


## <strong>Setup Monitoring System</strong>
### <strong>Install Docker & docker-compose</strong>
If you haven't installed docker and docker-compose on your devices yet (control plane & workers), just execute the following command on each one of them: 
````
sh install-docker.sh
````

### <strong>Start Control-Plane services</strong>
When you have docker and docker-compose installed, all you need to run on the **Control Plane** the following command:
````
docker-compose up -f docker-compose-monitoring.yaml
````

*Don't forget to replace the environment variables however you would wish to (e.g. "${database_name}")*

### <strong>Start Worker services</strong>
On each **Worker** you can start and setup Netdata by just running:
````
docker-compose up
````
*Keep in mind, that you need to define the smart plug's ip.*
#### <strong>Changing smart plug configuration</strong>
There are two things needed for this process:
1) First you should remove/change the "smart-plug" service from docker-compose.yaml
2) Update the netdata/prometheus.conf. You should update accordingly the "smart_plug" configuration, which is defined in the end of the "prometheus.conf". This setup if for exposing its metrics to netdata.
#### <strong>Register Worker nodes to Consul</strong>
On each worker, after you have started the worker services, just enter the **Consul** folder and execute the following command:
````
sh register_to_consul.sh
````
*Please, don't forget to replace the IPs in the script with your IPs (Consul Ip, and worker device IP)*


## <strong>Resources</strong>

### <strong>The Team</strong>
The creators of the BenchPilot are members of the [Laboratory for Internet Computing (LInC), University of Cyprus](http://linc.ucy.ac.cy/).
You can find more information about our research activity visit our publications' [page](http://linc.ucy.ac.cy/index.php?id=12) and our [on-going projects](http://linc.ucy.ac.cy/index.php?id=13).


### <strong>Acknowledgements</strong>
This work is partially supported by the EU Commission through [RAINBOW](https://rainbow-h2020.eu/)  871403 (ICT-15-2019-2020) project 
and by the Cyprus Research and Innovation Foundation through COMPLEMENTARY/0916/0916/0171 project, and from [RAIS](https://rais-itn.eu/) (Real-time analytics for the Internet of Sports), Marie Skłodowska-Curie Innovative Training Networks (ITN), under grant agreement No 813162.

### <strong>License</strong>
The framework is open-sourced under the Apache 2.0 License base. The codebase of the framework is maintained by the authors for academic research and is therefore provided "as is".