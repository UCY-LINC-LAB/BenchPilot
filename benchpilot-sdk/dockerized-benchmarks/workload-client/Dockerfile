FROM ubuntu:22.04

# copy client files 
COPY src /workload-client/src
WORKDIR /workload-client/src

# install java (for any architecture) & setup java & other required libraries
USER root
RUN apt-get update && apt-get -y install openjdk-8-jdk \
    && rm -rf /var/lib/apt/lists/*; \ 
    apt-get update && apt-get -y install python3 python3-pip python-is-python3 git wget tini; \
    export JAVA_HOME=/usr/lib/jvm/`ls -l /usr/lib/jvm | grep '^d' | grep java-8-openjdk | cut -d ' ' -f 9` \
    export MAVEN_V="3" MAVEN_VERSION="3.9.6"; \
    wget -O /home/apache-maven-$MAVEN_VERSION-bin.tar.gz http://apache.mirror.iphh.net/maven/maven-$MAVEN_V/$MAVEN_VERSION/binaries/apache-maven-$MAVEN_VERSION-bin.tar.gz; \
    tar -xvf /home/apache-maven-$MAVEN_VERSION-bin.tar.gz -C /opt/; \
    rm /home/apache-maven-$MAVEN_VERSION-bin.tar.gz; \
    mv /opt/apache-maven-$MAVEN_VERSION /opt/maven; \
    wget -O /home/lein https://raw.githubusercontent.com/technomancy/leiningen/stable/bin/lein; \
    mv /home/lein /usr/local/bin/lein; \
    chmod a+x /usr/local/bin/lein; \
    wget -O /home/linux-install-1.10.2.774.sh https://download.clojure.org/install/linux-install-1.10.2.774.sh; \
    chmod +x /home/linux-install-1.10.2.774.sh; \
    /home/linux-install-1.10.2.774.sh; \
    pip3 install -r ./requirements.txt;

ENV PATH "/opt/maven/bin:$PATH"
ENV PATH "$JAVA_HOME/bin:$PATH"

ENTRYPOINT ["/usr/bin/tini", "--", "python3", "main.py"]
