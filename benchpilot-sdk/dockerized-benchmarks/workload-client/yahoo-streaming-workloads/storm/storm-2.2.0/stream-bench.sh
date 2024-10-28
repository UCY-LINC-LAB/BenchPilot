#!/bin/bash

STORM_DIR="storm"

. /workload-client/src/marketing-workload.sh

run() {
  manage_workload_processes "$1"
  OPERATION=$1
  if [ "START_PROCESSING" = "$OPERATION" ];
  then
    "/$STORM_DIR/bin/storm" jar /workload-client/src/storm-benchmarks/target/storm-benchmarks-0.1.0.jar storm.benchmark.AdvertisingTopology streaming-topology -conf $CONF_FILE
    sleep 15
  elif [ "STOP_PROCESSING" = "$OPERATION" ];
  then
    "/$STORM_DIR/bin/storm" kill -w 0 streaming-topology || true
    sleep 10
  elif [ "START_TEST" = "$OPERATION" ];
  then
    run "START_REDIS"
    run "START_PROCESSING"
    run "START_LOAD"
  elif [ "STOP_TEST" = "$OPERATION" ];
  then
    run "STOP_LOAD"
    run "STOP_PROCESSING"
  fi
}

while [ $# -gt 0 ];
do
  run "$1"
  shift
done
