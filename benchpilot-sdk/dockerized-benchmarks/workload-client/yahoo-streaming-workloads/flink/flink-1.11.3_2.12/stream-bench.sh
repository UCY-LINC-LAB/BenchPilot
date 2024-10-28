#!/bin/bash

FLINK_DIR="flink"

. /workload-client/src/marketing-workload.sh

run() {
  manage_workload_processes "$1"
  OPERATION=$1
  if [ "START_PROCESSING" = "$OPERATION" ];
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
