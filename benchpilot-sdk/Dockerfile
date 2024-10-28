FROM ubuntu:latest


# Copy benchpilot files
COPY BenchPilotSDK /BenchPilotSDK
# install required libraries
RUN apt-get -y update && apt-get install -y bash vim build-essential curl wget git ca-certificates python3 python3-pip && \
    pip3 install -r /BenchPilotSDK/conf/benchPilotExtraConf/requirements.txt && pip3 install notebook && \
    export TINI_VERSION=v0.19.0; \
    wget https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini; \
    chmod +x /tini;

ENTRYPOINT ["/tini", "--", "jupyter", "notebook", "--ip='0.0.0.0'", "--port=8888", "--no-browser", "--allow-root"]
