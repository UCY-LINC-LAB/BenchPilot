#!/bin/bash
# Copyright 2015, Yahoo Inc.
# Licensed under the terms of the Apache License 2.0. Please see LICENSE file in the project root for terms.
set -o pipefail
set -o errtrace
set -o nounset
set -o errexit

LEIN=${LEIN:-lein}
MVN=${MVN:-mvn}
MAKE=${MAKE:-make}

KAFKA_VERSION=${KAFKA_VERSION:-"2.2.1"}
REDIS_VERSION=${REDIS_VERSION:-"6.0.10"}
SCALA_BIN_VERSION=${SCALA_BIN_VERSION:-"2.11"}
SCALA_SUB_VERSION=${SCALA_SUB_VERSION:-"12"}
STORM_VERSION=${STORM_VERSION:-"1.2.3"}
FLINK_VERSION=${FLINK_VERSION:-"1.11.3"}
SPARK_VERSION=${SPARK_VERSION:-"2.4.7"}


STORM_DIR="apache-storm-$STORM_VERSION"
REDIS_DIR="redis-$REDIS_VERSION"
KAFKA_DIR="kafka_$SCALA_BIN_VERSION-$KAFKA_VERSION"
FLINK_DIR="flink-$FLINK_VERSION"
SPARK_DIR="spark-$SPARK_VERSION-bin-hadoop2.7"
spark_executor_memory=$(grep 'spark.executor.memory' ./conf/benchmarkConf.yaml | sed 's/^.*: //');
spark_executor_cores=$(grep 'spark.executor.cores' ./conf/benchmarkConf.yaml | sed 's/^.*: //');


#Get one of the closet apache mirrors
APACHE_MIRROR=$"https://archive.apache.org/dist"

ZK_HOST="zookeeper"
ZK_PORT="2181"
ZK_CONNECTIONS="$ZK_HOST:$ZK_PORT"
TOPIC=${TOPIC:-"ad-events"}
PARTITIONS=${PARTITIONS:-1}
LOAD=${LOAD:-1000}
CONF_FILE=./conf/benchmarkConf.yaml
TEST_TIME=${TEST_TIME:-240}


pid_match() {
   local VAL=`ps -aef | grep "$1" | grep -v grep | awk '{print $2}'`
   echo $VAL
}

start_if_needed() {
  local match="$1"
  shift
  local name="$1"
  shift
  local sleep_time="$1"
  shift
  local PID=`pid_match "$match"`

  if [[ "$PID" -ne "" ]];
  then
    echo "$name is already running..."
  else
    "$@" &
    sleep $sleep_time
  fi
}

stop_if_needed() {
  local match="$1"
  local name="$2"
  local PID=`pid_match "$match"`
  if [[ "$PID" -ne "" ]];
  then
    kill "$PID"
    sleep 1
    local CHECK_AGAIN=`pid_match "$match"`
    if [[ "$CHECK_AGAIN" -ne "" ]];
    then
      kill -9 "$CHECK_AGAIN"
    fi
  else
    echo "No $name instance found to stop"
  fi
}


fetch_untar_file() {
  local FILE="download-cache/$1"
  local URL=$2
  if [[ -e "$FILE" ]];
  then
    echo "Using cached File $FILE"
  else
  mkdir -p download-cache/
    WGET=`whereis wget`
    CURL=`whereis curl`
    if [ -n "$WGET" ];
    then
      wget -O "$FILE" "$URL"
    elif [ -n "$CURL" ];
    then
      curl -o "$FILE" "$URL"
    else
      echo "Please install curl or wget to continue.";
      exit 1
    fi
  fi
  tar -xzvf "$FILE"
}


run() {
  OPERATION=$1
  if [ "SETUP" = "$OPERATION" ];
  then
	
    $MVN clean install -Dspark.version="$SPARK_VERSION" -Dkafka.version="$KAFKA_VERSION" -Dflink.version="$FLINK_VERSION"  -Dstorm.version="$STORM_VERSION"  -Dscala.binary.version="$SCALA_BIN_VERSION" -Dscala.version="$SCALA_BIN_VERSION.$SCALA_SUB_VERSION"  
    
    #Fetch Storm
    STORM_FILE="$STORM_DIR.tar.gz"
    fetch_untar_file "$STORM_FILE" "$APACHE_MIRROR/storm/$STORM_DIR/$STORM_FILE"
    
    cp ./conf/storm.yaml ./$STORM_DIR/conf/storm.yaml

    #Fetch Flink
    FLINK_FILE="$FLINK_DIR-bin-scala_${SCALA_BIN_VERSION}.tgz"
    fetch_untar_file "$FLINK_FILE" "$APACHE_MIRROR/flink/flink-$FLINK_VERSION/$FLINK_FILE"
    
    cp ./conf/flink-config.yaml ./$FLINK_DIR/conf/flink-conf.yaml

    #Fetch Spark
    SPARK_FILE="$SPARK_DIR.tgz"
    fetch_untar_file "$SPARK_FILE" "$APACHE_MIRROR/spark/spark-$SPARK_VERSION/$SPARK_FILE"
  
  elif [ "SETUP_SPARK" = "$OPERATION" ];
  then
	
    $MVN clean install -Dspark.version="$SPARK_VERSION" -Dkafka.version="$KAFKA_VERSION" -Dflink.version="$FLINK_VERSION"  -Dstorm.version="$STORM_VERSION"  -Dscala.binary.version="$SCALA_BIN_VERSION" -Dscala.version="$SCALA_BIN_VERSION.$SCALA_SUB_VERSION"

    #Fetch Spark
    SPARK_FILE="$SPARK_DIR.tgz"
    fetch_untar_file "$SPARK_FILE" "$APACHE_MIRROR/spark/spark-$SPARK_VERSION/$SPARK_FILE"

  elif [ "SETUP_STORM" = "$OPERATION" ];
  then
	
    $MVN clean install -Dspark.version="$SPARK_VERSION" -Dkafka.version="$KAFKA_VERSION" -Dflink.version="$FLINK_VERSION"  -Dstorm.version="$STORM_VERSION"  -Dscala.binary.version="$SCALA_BIN_VERSION" -Dscala.version="$SCALA_BIN_VERSION.$SCALA_SUB_VERSION"  
    
    #Fetch Storm
    STORM_FILE="$STORM_DIR.tar.gz"
    fetch_untar_file "$STORM_FILE" "$APACHE_MIRROR/storm/$STORM_DIR/$STORM_FILE"
    
    cp ./conf/storm.yaml ./$STORM_DIR/conf/storm.yaml
  elif [ "SETUP_FLINK" = "$OPERATION" ];
  then
	
    $MVN clean install -Dspark.version="$SPARK_VERSION" -Dkafka.version="$KAFKA_VERSION" -Dflink.version="$FLINK_VERSION"  -Dstorm.version="$STORM_VERSION"  -Dscala.binary.version="$SCALA_BIN_VERSION" -Dscala.version="$SCALA_BIN_VERSION.$SCALA_SUB_VERSION"  

    #Fetch Flink
    FLINK_FILE="$FLINK_DIR-bin-scala_${SCALA_BIN_VERSION}.tgz"
    fetch_untar_file "$FLINK_FILE" "$APACHE_MIRROR/flink/flink-$FLINK_VERSION/$FLINK_FILE"
    
    cp ./conf/flink-config.yaml ./$FLINK_DIR/conf/flink-conf.yaml
   
  elif [ "START_REDIS" = "$OPERATION" ];
  then
    #start_if_needed redis-server Redis 1 "$REDIS_DIR/BenchPilotSDK/redis-server"
    cd data
    $LEIN run -n --configPath ../conf/benchmarkConf.yaml
    cd ..
  elif [ "STOP_REDIS" = "$OPERATION" ];
  then
    stop_if_needed redis-server Redis
    rm -f dump.rdb
  elif [ "START_STORM_NIMBUS" = "$OPERATION" ];
  then
    start_if_needed daemon.name=nimbus "Storm Nimbus" 3 "$STORM_DIR/bin/storm" nimbus
    start_if_needed daemon.name=logviewer "Storm LogViewer" 3 "$STORM_DIR/bin/storm" logviewer
  elif [ "START_STORM_SUPERVISOR" = "$OPERATION" ];
  then
    start_if_needed daemon.name=supervisor "Storm Supervisor" 3 "$STORM_DIR/bin/storm" supervisor
  elif [ "START_STORM_UI" = "$OPERATION" ];
  then
    start_if_needed daemon.name=ui "Storm UI" 3 "$STORM_DIR/bin/storm" ui
  elif [ "STOP_STORM_UI" = "$OPERATION" ];
  then
    stop_if_needed daemon.name=ui "Storm UI"
  elif [ "STOP_STORM_NIMBUS" = "$OPERATION" ];
  then
    stop_if_needed daemon.name=nimbus "Storm Nimbus"
    stop_if_needed daemon.name=logviewer "Storm LogViewer"
  elif [ "STOP_STORM_SUPERVISOR" = "$OPERATION" ];
  then
    stop_if_needed daemon.name=supervisor "Storm Supervisor"
  elif [ "START_FLINK_MASTER" = "$OPERATION" ];
  then
    start_if_needed org.apache.flink.runtime.jobmanager.JobManager Flink 1 $FLINK_DIR/bin/start-cluster.sh
  elif [ "START_FLINK_WORKER" = "$OPERATION" ];
  then
    start_if_needed org.apache.flink.runtime.taskmanager.TaskManager Flink 1 $FLINK_DIR/bin/taskmanager.sh
  elif [ "STOP_FLINK" = "$OPERATION" ];
  then
    $FLINK_DIR/bin/stop-cluster.sh
  elif [ "START_SPARK_MASTER" = "$OPERATION" ];
  then
    start_if_needed org.apache.spark.deploy.master.Master SparkMaster 5 $SPARK_DIR/sbin/start-master.sh -h 0.0.0.0 -p 7077
  elif [ "STOP_SPARK_MASTER" = "$OPERATION" ];
  then
    stop_if_needed org.apache.spark.deploy.master.Master SparkMaster
    sleep 3
  elif [ "START_SPARK_SLAVE" = "$OPERATION" ];
  then
    start_if_needed org.apache.spark.deploy.worker.Worker SparkSlave 5 $SPARK_DIR/sbin/start-slave.sh spark://spark-master:7077
  elif [ "STOP_SPARK_SLAVE" = "$OPERATION" ];
  then
    stop_if_needed org.apache.spark.deploy.worker.Worker SparkSlave
    sleep 3
  elif [ "START_LOAD" = "$OPERATION" ];
  then
    cd data
    start_if_needed leiningen.core.main "Load Generation" 1 $LEIN run -r -t $LOAD --configPath ../$CONF_FILE
    cd ..
  elif [ "STOP_LOAD" = "$OPERATION" ];
  then
    stop_if_needed leiningen.core.main "Load Generation"
    cd data
    $LEIN run -g --configPath ../$CONF_FILE || true
    cd ..
  elif [ "START_STORM_TOPOLOGY" = "$OPERATION" ];
  then
    "$STORM_DIR/bin/storm" jar ./storm-benchmarks/target/storm-benchmarks-0.1.0.jar storm.benchmark.AdvertisingTopology test-topo -conf $CONF_FILE
    sleep 15
  elif [ "STOP_STORM_TOPOLOGY" = "$OPERATION" ];
  then
    "$STORM_DIR/bin/storm" kill -w 0 test-topo || true
    sleep 10
  elif [ "START_SPARK_PROCESSING" = "$OPERATION" ];
  then
    "$SPARK_DIR/bin/spark-submit" --master spark://spark-master:7077 --conf "spark.executor.memory=$spark_executor_memory" --conf "spark.executor.cores=$spark_executor_cores" --class spark.benchmark.KafkaRedisAdvertisingStream ./spark-benchmarks/target/spark-benchmarks-0.1.0.jar "$CONF_FILE" &
    sleep 5
  elif [ "STOP_SPARK_PROCESSING" = "$OPERATION" ];
  then
    stop_if_needed spark.benchmark.KafkaRedisAdvertisingStream "Spark Client Process"
  elif [ "START_FLINK_PROCESSING" = "$OPERATION" ];
  then
    "$FLINK_DIR/bin/flink" run ./flink-benchmarks/target/flink-benchmarks-0.1.0.jar --target remote --confPath $CONF_FILE &
    sleep 3
  elif [ "STOP_FLINK_PROCESSING" = "$OPERATION" ];
  then
    FLINK_ID=`"$FLINK_DIR/bin/flink" list | grep 'Flink Streaming Job' | awk '{print $4}'; true`
    if [ "$FLINK_ID" == "" ];
	then
	  echo "Could not find streaming job to kill"
    else
      "$FLINK_DIR/bin/flink" cancel $FLINK_ID
      sleep 3
    fi
  elif [ "STORM_TEST" = "$OPERATION" ];
  then
    run "START_REDIS"
    run "START_STORM_TOPOLOGY"
    run "START_LOAD"
    sleep $TEST_TIME
    run "STOP_LOAD"
    run "STOP_STORM_TOPOLOGY"
  elif [ "FLINK_TEST" = "$OPERATION" ];
  then
    run "START_REDIS"
    run "START_FLINK_PROCESSING"
    run "START_LOAD"
    sleep $TEST_TIME
    run "STOP_LOAD"
    run "STOP_FLINK_PROCESSING"
  elif [ "SPARK_TEST" = "$OPERATION" ];
  then
    run "START_REDIS"
    run "START_SPARK_PROCESSING"
    run "START_LOAD"
    sleep $TEST_TIME
    run "STOP_LOAD"
    run "STOP_SPARK_PROCESSING"
  else
    if [ "HELP" != "$OPERATION" ];
    then
      echo "UNKOWN OPERATION '$OPERATION'"
      echo
    fi
    echo "Supported Operations:"
    echo "SETUP: download and setup dependencies for running a single node test"
    echo "SETUP_STORM: download and setup dependencies for storm only"
    echo "SETUP_SPARK: download and setup dependencies for spark only"
    echo "SETUP_FLINK: download and setup dependencies for flink only"
    echo "START_REDIS: send campaigns to redis"
    echo "START_LOAD: run kafka load generation"
    echo "STOP_LOAD: kill kafka load generation"
    echo "START_STORM_NIMBUS: run storm nimbus daemon in the background"
    echo "STOP_STORM_NIMBUS: kill the storm nimbus daemon"
    echo "START_STORM_SUPERVISOR: run storm supervisor daemon in the background"
    echo "STOP_STORM_SUPERVISOR: kill the storm supervisor daemon"
    echo "START_STORM_UI: run storm ui daemon in the background"
    echo "STOP_STORM_UI: kill the storm ui daemon"
    echo "START_FLINK_MASTER: run flink job master processes"
    echo "STOP_FLINK_MASTER: kill flink job master processes"
    echo "START_FLINK_WORKER: run flink task master processes"
    echo "STOP_FLINK_WORKER: kill flink task master processes"
    echo "START_SPARK_MASTER: run spark master process"
    echo "STOP_SPARK_MASTER: kill spark master process"
    echo "START_SPARK_SLAVE: run spark slave process"
    echo "STOP_SPARK_SLAVE: kill spark slave process"
    echo 
    echo "START_STORM_TOPOLOGY: run the storm test topology"
    echo "STOP_STORM_TOPOLOGY: kill the storm test topology"
    echo "START_FLINK_PROCESSING: run the flink test processing"
    echo "STOP_FLINK_PROCESSSING: kill the flink test processing"
    echo "START_SPARK_PROCESSING: run the spark test processing"
    echo "STOP_SPARK_PROCESSSING: kill the spark test processing"
    echo
    echo "STORM_TEST: run storm test (assumes SETUP is done)"
    echo "FLINK_TEST: run flink test (assumes SETUP is done)"
    echo "SPARK_TEST: run spark test (assumes SETUP is done)"
    echo "STOP_ALL: stop everything"
    echo
    echo "HELP: print out this message"
    echo
    exit 1
  fi
}

if [ $# -lt 1 ];
then
  run "HELP"
else
  while [ $# -gt 0 ];
  do
    run "$1"
    shift
  done
fi
