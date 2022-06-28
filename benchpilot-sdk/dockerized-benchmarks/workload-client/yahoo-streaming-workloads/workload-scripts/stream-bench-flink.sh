#!/bin/bash

LEIN=${LEIN:-lein}
MVN=${MVN:-mvn}
MAKE=${MAKE:-make}

KAFKA_VERSION=${KAFKA_VERSION:-"2.2.1"}
SCALA_BIN_VERSION=${SCALA_BIN_VERSION:-"2.11"}
SCALA_SUB_VERSION=${SCALA_SUB_VERSION:-"12"}
FLINK_VERSION=${FLINK_VERSION:-"1.11.3"}
FLINK_DIR="flink-$FLINK_VERSION"

CONF_FILE=./conf/benchmarkConf.yaml

LOAD=$(grep 'benchmark.tuples.per.second.emition' $CONF_FILE | sed 's/^.*: //');
TEST_TIME=$(grep 'benchmark.duration' $CONF_FILE | sed 's/^.*: //');

#Get one of the closet apache mirrors
APACHE_MIRROR=$"https://archive.apache.org/dist"


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
  tar -xzvf "$FILE" -C /
}


run() {
  OPERATION=$1
  if [ "SETUP" = "$OPERATION" ];
  then
	
    $MVN clean install -Dkafka.version="$KAFKA_VERSION" -Dflink.version="$FLINK_VERSION"  -Dscala.binary.version="$SCALA_BIN_VERSION" -Dscala.version="$SCALA_BIN_VERSION.$SCALA_SUB_VERSION"

    #Fetch Flink
    FLINK_FILE="$FLINK_DIR-bin-scala_${SCALA_BIN_VERSION}.tgz"
    fetch_untar_file "$FLINK_FILE" "$APACHE_MIRROR/flink/flink-$FLINK_VERSION/$FLINK_FILE"
    
    cp ./conf/flink-config.yaml /$FLINK_DIR/conf/flink-conf.yaml
   
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
  elif [ "START_PROCESSING" = "$OPERATION" ];
  then
    "/$FLINK_DIR/bin/flink" run ./flink-benchmarks/target/flink-benchmarks-0.1.0.jar --target remote --confPath $CONF_FILE &
    sleep 3
  elif [ "STOP_PROCESSING" = "$OPERATION" ];
  then
    FLINK_ID=`"$/FLINK_DIR/bin/flink" list | grep 'Flink Streaming Job' | awk '{print $4}'; true`
    if [ "$FLINK_ID" == "" ];
	then
	  echo "Could not find streaming job to kill"
    else
      "/$FLINK_DIR/bin/flink" cancel $FLINK_ID
      sleep 3
    fi
  elif [ "START_TEST" = "$OPERATION" ];
  then
    START_TIMESTAMP=`date '+%Y-%m-%dT%H:%M:%SZ'`
    run "START_REDIS"
    run "START_PROCESSING"
    run "START_LOAD"
    sleep $TEST_TIME
    run "STOP_LOAD"
    run "STOP_PROCESSING"
    END_TIMESTAMP=`date '+%Y-%m-%dT%H:%M:%SZ'`
    rm ./data/seen.txt
    mv ./data/updated.txt ./data/updated_$START_TIMESTAMP.txt
    echo "$START_TIMESTAMP,$END_TIMESTAMP," >> workloads.csv
  else
    if [ "HELP" != "$OPERATION" ];
    then
      echo "UNKOWN OPERATION '$OPERATION'"
      echo
    fi
    echo "Supported Operations:"
    echo "SETUP: download and setup dependencies for flink only"
    echo "START_REDIS: send campaigns to redis"
    echo "START_LOAD: run kafka load generation"
    echo "STOP_LOAD: kill kafka load generation"
    echo "START_PROCESSING: run the flink test processing"
    echo "STOP_PROCESSSING: kill the flink test processing"
    echo
    echo "START_TEST: run flink test (assumes SETUP is done)"
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
