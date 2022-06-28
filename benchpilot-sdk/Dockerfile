FROM ubuntu:20.04

# install required libraries
RUN apt-get -y update
RUN apt-get install -y bash vim build-essential
RUN apt-get install -y curl wget
RUN apt-get install -y git ca-certificates
RUN rm -rf /var/lib/apt/lists

# install python 
RUN apt-get -y update
RUN apt-get -y install python3 python3-pip
RUN python3 --version

COPY ./BenchPilotSDK /BenchPilotSDK
COPY ./dockerized-benchmarks /dockerized-benchmarks
COPY benchPilotNote.ipynb /benchPilotNote.ipynb
RUN pip3 install -r /BenchPilotSDK/conf/requirements.txt
RUN pip3 install notebook
