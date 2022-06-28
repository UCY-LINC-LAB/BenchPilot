#!/bin/bash

sudo apt-get -y update && sudo apt-get -y upgrade
sudo apt-get install -y curl
curl -sSL https://get.docker.com | sh
sudo usermod -aG docker ${USER}
groups ${USER}
sudo apt-get -y install libffi-dev libssl-dev python3-dev python3 python3-pip
sudo pip3 install docker-compose
sudo systemctl enable docker
newgrp docker
