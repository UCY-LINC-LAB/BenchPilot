---
title: "Installation"
weight: 2
# bookFlatSection: false
# bookToc: true
# bookHidden: false
# bookCollapseSection: false
# bookComments: false
# bookSearchExclude: false
---
# <strong style="color: #40897B">GitHub Repository</strong>
Visit our <a href="https://github.com/UCY-LINC-LAB/BenchPilot"> Github Repository </a> to download or fork BenchPilot!


# <strong style="color: #40897B">DockerHub</strong>
All of our Docker images are uploaded on our <a href="https://hub.docker.com/r/benchpilot/benchpilot"> DockerHub Repository</a>!

# <strong style="color: #40897B">BenchPilot Bootstrapping</strong>
Before the experimentation phase starts, a necessary bootstrapping needs to be done. The BenchPilot user only needs to execute a parameterizable installation script of Benchpilot on every cluster node. The script installs all necessary software dependencies across the micro-DC and downloads the required workload docker images.
<!-- For the script to work properly, the user needs to provide a list of essential information about the cluster in the '/conf/bench-cluster-setup.yaml'. Specifically, it's essential to fill each node's <i>hostname</i>, which can be either the machine's IP or hostname that will be reachable from the device BenchPilot is running from, a <i>username</i>, and either an <i>ssh key path</i> or a <i>password</i>. The latter allows BenchPilot to connect and install all necessary software dependencies across the cluster. -->
This step is required only for the first time of the BenchPilot installation or in case of a hardware update, e.g., introducing a new device.
