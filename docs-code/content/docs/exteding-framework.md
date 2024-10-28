---
title: "Exteding BenchPilot"
weight: 7
# bookFlatSection: false
# bookToc: true
# bookHidden: false
# bookCollapseSection: false
# bookComments: false
# bookSearchExclude: false
---
# <strong style="color: #40897B">Extending BenchPilot</strong>
This section describes all of the steps you need to take in order to extend BenchPilot for supporting more workloads!

## Dockerize Workload
The first step to extend BenchPiot, is to create the necessary docker images. In general BenchPilot utilizes the idea of having a controller node (which BenchPilot's client and other core services will reside on), and the workers, which will be the system under test. Having this scheme in mind, you need to dockerize your workload, and to divide it into images that will reside on your controller node, and another image which will be deployed on the workers. 

## Adding New Services
After creating the latter images, you should add under the /BenchPilotSDK/services the new service. That class should derive its properties from the BenchPilot's abstract service object. Keep in mind that for every docker image you created for your workload, you should declare it as a different service.

For each service it is important to declare the following:
- <i>docker image</i>, either an already existing one, or you have to create it on your own
- <i>hostname</i>, we use the same one as the service name usually
- <i>image tag</i>, in cases of having different images for arm infrastructures you can define it using the "image_arm_tag" attribute.
- <i>ports</i>, needed ports
- <i>environment</i>, needed environment variables / configurations
- <i>service log</i>, the log that the service prints when is up and running
- <i>Depends On</i>, here you should add the service name that it's important to start before the one you just created
- <i>Command</i>, in case if it needs to execute a specific command when the service starts
- <i>Proxy</i>, a simple "True" / "False" definition, whether it will reside on a device that passes through proxy
- <i>needs_placement</i>, again, "True" if it should reside on a worker, "False" if it's a core service and will reside on the manager node

To configure the environment, ports, volumes, and images of the service, you should call the appropriate methods rather than directly assigning them to parameters. This approach simplifies the process by eliminating the need to understand the exact initialization details of these parameters.

Below you can see a service example:
```python
from BenchPilotSDK.services.service import Service


class Redis(Service):
    """
    This class represents the redis docker service
    """
    def __init__(self):
        Service.__init__(self)
        self.hostname = "redis"
        self.assign_image(image_name="bitnami/redis", image_tag="6.0.10")
        self.add_environment("ALLOW_EMPTY_PASSWORD", "yes")
        self.service_started_log = "Ready to accept connections"

```

** Before adding new services, check first if it already exists.

## Adding New Workload
After adding all of your workload's services, you should create a new workload class as well, under the /BenchPilotSDK/workloads. This particular class will inherit its behavior from the "workload" class. In that class you should add in the "services list" all the services you need. 

In the following block you can find a Workload example:
```python
from abc import ABC
import BenchPilotSDK.utils.benchpilotProcessor as bp
from BenchPilotSDK.utils.exceptions import BenchExperimentInvalidException
from BenchPilotSDK.workloads.workload import Workload
from BenchPilotSDK.services.materializedServices.stress import Stress


class Simple(Workload, ABC):
    """
    This class represents the Simple Workload, it just creates a specific simple workload.
    """

    def __init__(self, **workload_definition):
        super().__init__(**workload_definition)
        bp.check_required_parameters('workload > parameters', ["service"], workload_definition["parameters"])
        service = self.parameters["service"]
        options = {} if not "options" in self.parameters else self.parameters["options"]
        service = Stress(options)
        ...

```

### Adding a new SDPE Workload
In case of adding a new Streaming Distributed - based workload you don't need to add the engines, you only need to inherit from the <i>SDPEWorkload</i> class, and add the rest of the services, like the example below: 

```python
import inspect
from abc import ABC
from dataclasses import dataclass, asdict
from BenchPilotSDK.workloads.materializedWorkloads.sdpeWorkload import SDPEWorkload
from BenchPilotSDK.services.materializedServices.kafka import Kafka
from BenchPilotSDK.services.materializedServices.redis import Redis
from BenchPilotSDK.services.materializedServices.zookeeper import Zookeeper


class MarketingCampaign(SDPEWorkload, ABC):
    """
    This class represents Yahoo Streaming Benchmark, it holds all the extra needed services.
    - by extra we mean the services that are not DSPEs
    """

    @dataclass
    class Parameters:
        num_of_campaigns: int = 1000
        ...

        @classmethod
        def from_dict(cls, env):
            return cls(**{
                k: v for k, v in env.items()
                if k in inspect.signature(cls).parameters
            })

        def __post_init__(self):
            ..

    def __init__(self, **workload_definition):
        super().__init__(**workload_definition)
        self.parameters.update(asdict(self.Parameters.from_dict(workload_definition)))
        self.add_service(Zookeeper())
        self.add_service(Kafka(len(self.cluster), self.manager_ip))
        self.add_service(Redis())

```