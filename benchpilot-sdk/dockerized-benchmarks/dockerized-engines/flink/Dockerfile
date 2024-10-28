FROM ubuntu:22.04

# install java (for any architecture) & setup java & other required libraries
USER root
RUN apt-get update \
    && apt-get -y install openjdk-8-jdk tini \
    && rm -rf /var/lib/apt/lists/* && \ 
    export JAVA_HOME=/usr/lib/jvm/`ls -l /usr/lib/jvm | grep '^d' | grep java-8-openjdk | cut -d ' ' -f 9` \
    && apt-get update && apt-get -y install python3 python3-pip python-is-python3 wget
    
# Setup java home and flink version
ENV PATH=$JAVA_HOME/bin:$PATH FLINK_VERSION="1.11.3" SCALA_BIN_VERSION="2.11"

# download flink & tini
COPY flink-conf.yaml masters entrypoint.sh /
RUN export FLINK_FILE="flink-$FLINK_VERSION-bin-scala_${SCALA_BIN_VERSION}.tgz"; \
    wget -O "$FLINK_FILE" "https://archive.apache.org/dist/flink/flink-$FLINK_VERSION/$FLINK_FILE"; \
    tar -xzvf "$FLINK_FILE"; \
    rm "$FLINK_FILE"; \ 
    mv flink-$FLINK_VERSION flink; \
    mv flink-conf.yaml /flink/conf/flink-conf.yaml; \
    mv masters /flink/conf/masters; \
    chmod +x /entrypoint.sh;

ENTRYPOINT ["/usr/bin/tini", "--", "/entrypoint.sh"]
