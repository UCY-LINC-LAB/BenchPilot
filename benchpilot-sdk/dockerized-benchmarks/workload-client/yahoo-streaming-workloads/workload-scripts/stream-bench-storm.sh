#!/bin/bash

LEIN=${LEIN:-lein}
MVN=${MVN:-mvn}
MAKE=${MAKE:-make}

KAFKA_VERSION=${KAFKA_VERSION:-"2.2.1"}
SCALA_BIN_VERSION=${SCALA_BIN_VERSION:-"2.11"}
SCALA_SUB_VERSION=${SCALA_SUB_VERSION:-"12"}
STORM_VERSION=${STORM_VERSION:-"1.2.3"}

CONF_FILE=./conf/benchmarkConf.yaml

STORM_DIR="apache-storm-$STORM_VERSION"
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
    $MVN clean install -Dkafka.version="$KAFKA_VERSION" -Dstorm.version="$STORM_VERSION"  -Dscala.binary.version="$SCALA_BIN_VERSION" -Dscala.version="$SCALA_BIN_VERSION.$SCALA_SUB_VERSION"
    #Fetch Storm
    STORM_FILE="$STORM_DIR.tar.gz"
    fetch_untar_file "$STORM_FILE" "$APACHE_MIRROR/storm/$STORM_DIR/$STORM_FILE"
    cp ./conf/storm.yaml /$STORM_DIR/conf/storm.yaml

  elif [ "START_REDIS" = "$OPERATION" ];
  then
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
    "/$STORM_DIR/bin/storm" jar /workload-client/src/storm-benchmarks/target/storm-benchmarks-0.1.0.jar storm.benchmark.AdvertisingTopology streaming-topology -conf $CONF_FILE
    sleep 15
  elif [ "STOP_PROCESSING" = "$OPERATION" ];
  then
    "/$STORM_DIR/bin/storm" kill -w 0 streaming-topology || true
    sleep 10
  elif [ "START_TEST" = "$OPERATION" ];
  then
    # START_TIMESTAMP=`date '+%Y-%m-%dT%H:%M:%SZ'`
    run "START_REDIS"
    run "START_PROCESSING"
    run "START_LOAD"
    sleep $TEST_TIME
    #curl "http://storm-ui:8080/api/v1/topology/summary" >> summary.json
    #TOPOLOGY_ID=`cat summary.json | json_pp | grep id | grep -v grep | awk '{print $3}' | sed 's/\"//g' | sed 's/,//g'`
    #curl "http://storm-ui:8080/api/v1/topology/$TOPOLOGY_ID" >> topology.json
    #rm summary.json
    run "STOP_LOAD"
    run "STOP_PROCESSING"
    # END_TIMESTAMP=`date '+%Y-%m-%dT%H:%M:%SZ'`
    rm ./data/seen.txt
    # mv ./data/updated.txt ./data/updated_$START_TIMESTAMP.txt
    # echo "$START_TIMESTAMP,$END_TIMESTAMP," >> workloads.csv
  elif [ "STOP_TEST" = "$OPERATION" ];
  then
    run "STOP_LOAD"
    run "STOP_PROCESSING"
    rm ./data/seen.txt
  else
    if [ "HELP" != "$OPERATION" ];
    then
      echo "UNKOWN OPERATION '$OPERATION'"
      echo
    fi
    echo "Supported Operations:"
    echo "SETUP: download and setup dependencies for storm only"
    echo "START_REDIS: send campaigns to redis"
    echo "START_LOAD: run kafka load generation"
    echo "STOP_LOAD: kill kafka load generation"
    echo
    echo "START_PROCESSING: run the storm topology"
    echo "STOP_PROCESSING: kill the storm topology"
    echo
    echo "START_TEST: run storm (assumes SETUP is done)"
    echo "STOP_TEST: stop loading and processing at once"
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
