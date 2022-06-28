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
## Install Docker & Docker Compose
In the 'Getting Started' section we learned how BenchPilot is structured. In order to use the BenchPilot client you need to have installed docker & docker-compose. In our GitHub Repository, under the <em>/utils</em> folder we have prepared for you a script to automatically download it, so all you need to run is "<strong><code style="color: #40897B">sh install-docker.sh</code></strong>".

## Retrieve or Build BenchPilot Client Image
The second step is to either retrieve or build the BenchPilot client image. 

### Pulling Image from DockerHub
For your ease, you can only pull the image from DockerHub just by running "<strong><code style="color: #40897B">docker pull benchpilot/benchpilot:client</code></strong>".

### Building Image Locally
If you want to build the image locally, you firstly need to download or clone our <a href="https://github.com/UCY-LINC-LAB/BenchPilot">GitHub repository</a> and then execute the building image script by running the command "<strong><code style="color: #40897B">sh build-image.sh</code></strong>".

## Start BenchPilot Client and start experimenting!
The final step is to just execute the following docker-compose.yaml by running the simple command "<strong><code style="color: #40897B">docker-compose up</code></strong>". It is not needed from you to be familiarized with docker and docker-compose, but in case you want to learn more, you can always visit their <a href="https://docs.docker.com/">website</a>!

````yaml
version: '3.8' # change it accordingly to your docker-compose version
services:
  benchpilot:
    # if you chose to build it locally replace the it with: bench-pilot
    image: benchpilot/benchpilot:client 
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /usr/bin/docker:/usr/bin/docker
    ports:
      - 8888:8888 # port needed for jupyter
    environment:
    # define http(s)_proxy only if your devide is placed behind a proxy
      - http_proxy=${http_proxy}
      - https_proxy=${https_proxy}
    # jupyter environment variables
      - "JUPYTER_ENABLE_LAB=yes" 
      - "GRANT_SUDO=yes"
      - "CHOWN_HOME=yes"
    # Prometheus environment variables
      - PROMETHEUS_IP=0.0.0.0
      - PROMETHEUS_PREFIX=${your_datacenter_prefix}
    user: root
    # command to start jupyter
    command: ["jupyter", "notebook", "--ip='0.0.0.0'", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
````

After starting the BenchPilot client, you can access jupyter through your browser from this link: "<strong><code style="color: #40897B">http://your_device_ip:8888</code></strong>", and start experimenting!

<a href="https://ucy-linc-lab.github.io/BenchPilot/docs/experiments/"> Learn how to define your experiments here.</a>