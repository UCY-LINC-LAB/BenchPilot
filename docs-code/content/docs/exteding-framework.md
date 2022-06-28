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
- <i>image tag</i>
- <i>image arm tag</i>, if one exists
- <i>ports</i>, needed ports
- <i>environment</i>, needed environment variables / configurations
- <i>service log</i>, the log that the service prints when is up and running
- <i>Depends On</i>, here you should add the service name that it's important to start before the one you just created
- <i>Command</i>, in case if it needs to execute a specific command when the service starts
- <i>Proxy</i>, a simple "True" / "False" definition, whether it will reside on a device that passes through proxy
- <i>needs_placement</i>, again, "True" if it should reside on a worker, "False" if it's a core service and will reside on the manager node

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
        self.image = "bitnami/redis"
        self.image_tag = "6.0.10"
        self.image_arm_tag = "not supported" # in case of not supporting arm images
        self.ports = ["6379:6379"]
        self.environment = ["ALLOW_EMPTY_PASSWORD=yes"]
        self.service_log = "Ready to accept connections"

```

** Before adding new services, check first if it already exists.

## Adding New Workload
After adding all of your workload's services, you should create a new workload class as well, under the /BenchPilotSDK/workloads. This particular class will inherit its behavior from the "workload" class. In that class you should add in the "services list" all the services you need. 

In the following block you can find a Workload example:
```python
from abc import ABC

from BenchPilotSDK.services.sdpe.engines import *
from BenchPilotSDK.services.sdpe.engine import Engine
from BenchPilotSDK.workloads.workload import Workload


class SDPEWorkload(Workload, ABC):
    """
    This class extends workload and adds the assign engine method in order to be able to assign
    a specific streaming distributed processing engine
    """
    engine: Engine

    def __init__(self, workload_yaml, workload_name: str):
        super().__init__(workload_yaml)
        self.workload_setup.check_required_parameters('workload', ["engine"], workload_yaml)
        self.workload_setup.check_required_parameters('engine', ["name"], workload_yaml["engine"])
        self.assign_engine(workload_yaml["engine"]["name"], workload_name)
        self.services.append(self.engine)

    # this method is for generalizing the term "Engine", hence the Engine is a generalized service that can be either Storm, Flink or Spark
    def assign_engine(self, engine: str, workload_name: str):
        if not engine is None:
            if "spark" in engine.lower():
                self.engine = Spark(len(self.nodes), self.manager_ip, workload_name)
            elif "storm" in engine.lower():
                self.engine = Storm(len(self.nodes), self.manager_ip, workload_name)
            elif "flink" in engine.lower():
                self.engine = Flink(len(self.nodes), self.manager_ip, workload_name)

```

### Adding a new SDPE Workload
In case of adding a new Streaming Distributed - based workload you don't need to add the engines, you only need to inherit from the <i>SDPEWorkload</i> class, and add the rest of the services, like the example below: 

```python
from abc import ABC

from BenchPilotSDK.workloads.sdpeWorkload import SDPEWorkload
from BenchPilotSDK.services.kafka import Kafka
from BenchPilotSDK.services.redis import Redis
from BenchPilotSDK.services.zookeeper import Zookeeper
from BenchPilotSDK.workloads.setup.yahooWorkloadSetup import YahooWorkloadSetup

# Inherits from the SDPEWorkload class that already exists
class Yahoo(SDPEWorkload, ABC):
    """
    This class represents Yahoo Streaming Benchmark, it holds all of the extra needed services.
    - by extra we mean the services that are not DSPEs
    """

    def __init__(self, workload_yaml):
        super().__init__(workload_yaml, "marketing-campaign")
        self.services.append(Zookeeper())
        kafka = Kafka(len(self.nodes), self.manager_ip)
        self.services.append(kafka)
        # defines which services would need to restart when a trials is over
        self.restarting_services.append(kafka)
        redis = Redis()
        self.services.append(redis)
        self.restarting_services.append(redis)
        # Assigns a workload setup
        self.workload_setup = YahooWorkloadSetup(workload_yaml)

```

### Creating a workload Setup
Under the /workloads we also included a setup package. In the setup package, you can add a new setup class thay you **may** need for configuring your workload. Your class should inherit and override the following class:
```python
import os
from abc import abstractmethod

from BenchPilotSDK.utils.exceptions import MissingBenchExperimentAttributeException


class WorkloadSetup(object):
    """
    The workloadSetup is responsible to set up the needed configuration files of a workload
    """
    cluster_dockerfile_path: str = os.environ["BENCHPILOT_PATH"]
    workload_client_path: str = os.environ["BENCHPILOT_PATH"] + "dockerized-benchmarks/workload-client/"

    def __init__(self, workload_yaml = None):
        self.workload_yaml = workload_yaml

    @abstractmethod
    def setup(self, parameters = None):
        self.update_workload_configuration(parameters)

    @abstractmethod
    def update_workload_configuration(self, parameters):
        # TODO override depending on the workload when rebuilding image
        pass

    @staticmethod
    def check_required_parameters(main_attribute, required_attributes, yaml):
        for att in required_attributes:
            if not att in yaml:
                raise MissingBenchExperimentAttributeException(main_attribute + "> " + att)
```

In case of not needing a setup, you can just ignore this step.

### Adding the workload into the workload factory
After adding the new workload, you should add a new "if" statement in the workload factory. This factory is applying the factory design pattern, and was added in order to generalize the "workload" object without needing to know with which object we are dealing with. 

Below you can find the code from the <i>/BenchPilotSDK/workloads/WorkloadFactory.py</i>, where you need to replace in the last lines your new workload's name:

```python
from BenchPilotSDK.workloads import *
from BenchPilotSDK.workloads.setup.workloadSetup import WorkloadSetup

class WorkloadFactory:
    """
    This class works as a workload factory.
    """
    workload: Workload
    workloadSetup: WorkloadSetup

    def __init__(self, workload_yaml):
        workloadSetup = WorkloadSetup()
        workloadSetup.check_required_parameters('workload', ["name"], workload_yaml)
        workload_name = workload_yaml["name"].lower()
        if "yahoo" in workload_name or "marketing-campaign" in workload_name:
            self.workload = Yahoo(workload_yaml)
        # replace the following lines with your new workload name
        elif "your-new-workload-name" in workload_name: 
            self.workload = YourNewWorkloadName(workload_yaml)
```


## Creating a new agent for submitting the job 
This part may be the trickiest one. You need to create a new agent. For the record, the agent is basically a Flask REST API which will get every now and again requests from BenchPilot to (i) <strong>start a new benchmark</strong>, (ii) <strong>check the benchmarking status</strong> (if it began, if it's running or if it has finished), and (iii) <strong>to force stop a running benchmark</strong>. So you need to implement these three functionalities in order for BenchPilot to work as expected.

This class exists under the following path: <i>dockerized-benchmarks/workload-client/src</i>.