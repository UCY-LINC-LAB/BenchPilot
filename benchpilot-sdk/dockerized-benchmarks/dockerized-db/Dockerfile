#FROM mongo:4-focal
FROM mongo:4.4.8-focal

COPY . /db-benchmark
WORKDIR /db-benchmark

# Install prequisites
USER root
RUN apt-get update && \
#&& apt-get -y upgrade && \
    apt-get -y install openjdk-8-jdk \ 
    wget \
    tar \
    tini \
    python-is-python3; \
    export JAVA_HOME=/usr/lib/jvm/`ls -l /usr/lib/jvm | grep '^d' | grep java-8-openjdk | cut -d ' ' -f 9` \
    export MAVEN_V="3" MAVEN_VERSION="3.9.4"; \
    wget -O /home/apache-maven-$MAVEN_VERSION-bin.tar.gz http://apache.mirror.iphh.net/maven/maven-$MAVEN_V/$MAVEN_VERSION/binaries/apache-maven-$MAVEN_VERSION-bin.tar.gz; \
    tar -xvf /home/apache-maven-$MAVEN_VERSION-bin.tar.gz -C /opt/; \
    rm /home/apache-maven-$MAVEN_VERSION-bin.tar.gz; \
    mv /opt/apache-maven-$MAVEN_VERSION /opt/maven; \
    chmod +x /db-benchmark/start_experiment.sh; \
    mv /db-benchmark/maven_settings.xml /opt/maven/conf/settings.xml && \
    mv /db-benchmark/.m2 /root/.m2; 

ENV PATH "/opt/maven/bin:$PATH"
ENV PATH "$JAVA_HOME/bin:$PATH"

#RUN mvn -pl site.ycsb:mongodb-binding -am package -DskipTests dependency:build-classpath -DincludeScope=compile -Dmdep.outputFilterFile=true;   

ENTRYPOINT ["/usr/bin/tini", "--", "./start_experiment.sh"]
