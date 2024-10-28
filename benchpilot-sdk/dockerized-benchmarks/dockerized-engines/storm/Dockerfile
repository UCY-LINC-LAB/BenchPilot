FROM ubuntu:22.04

# to build, please don't forget to set the build-arg, for e.g. --build-arg STORM_VERSION=2.2.0
# install java (for any architecture) & setup java & other required libraries
USER root
RUN apt-get update \
    && apt-get -y install openjdk-8-jdk tini \
    && rm -rf /var/lib/apt/lists/* && \ 
    export JAVA_HOME=/usr/lib/jvm/`ls -l /usr/lib/jvm | grep '^d' | grep java-8-openjdk | cut -d ' ' -f 9` \
    && apt-get update && apt-get -y install python3 python3-pip python-is-python3 wget
    
# Setup java home and storm version
ARG STORM_VERSION
ENV PATH=$JAVA_HOME/bin:$PATH PATH="$PATH:/entrypoint.sh"

# download storm & tini
COPY storm.yaml entrypoint.sh /
RUN export STORM_FILE="apache-storm-$STORM_VERSION.tar.gz"; \
    wget -O "$STORM_FILE" "https://archive.apache.org/dist/storm/apache-storm-$STORM_VERSION/$STORM_FILE"; \
    tar -xzvf "$STORM_FILE"; \
    rm "$STORM_FILE"; \ 
    mv apache-storm-$STORM_VERSION /storm; \
    mv /storm.yaml /storm/conf/storm.yaml; \
    chmod +x /entrypoint.sh;

ENTRYPOINT ["/usr/bin/tini", "--", "/entrypoint.sh"]
