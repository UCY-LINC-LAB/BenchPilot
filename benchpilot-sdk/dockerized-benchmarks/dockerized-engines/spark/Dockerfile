FROM ubuntu:22.04

# install java (for any architecture) & setup java & other required libraries
USER root
RUN apt-get update \
    && apt-get -y install openjdk-8-jdk tini \
    && rm -rf /var/lib/apt/lists/* && \ 
    export JAVA_HOME=/usr/lib/jvm/`ls -l /usr/lib/jvm | grep '^d' | grep java-8-openjdk | cut -d ' ' -f 9` \
    && apt-get update && apt-get -y install python3 python3-pip python-is-python3 wget
    
# Setup java home and storm version
ENV PATH=$JAVA_HOME/bin:$PATH SPARK_VERSION="3.0.0" HADOOP_VERSION="2.7" MANAGER_PORT="7077"

# download spark & tini
COPY entrypoint.sh /
RUN export SPARK_FILE="spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION.tgz"; \
    wget -O "$SPARK_FILE" "https://archive.apache.org/dist/spark/spark-$SPARK_VERSION/$SPARK_FILE"; \
    tar -xzvf "$SPARK_FILE"; \
    rm "$SPARK_FILE"; \ 
    mv spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION spark; \
    chmod +x /entrypoint.sh; 

ENTRYPOINT ["/usr/bin/tini", "--", "/entrypoint.sh"]
