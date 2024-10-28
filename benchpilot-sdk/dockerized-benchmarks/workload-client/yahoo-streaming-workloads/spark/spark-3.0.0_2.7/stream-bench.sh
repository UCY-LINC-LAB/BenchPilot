#!/bin/bash

SPARK_DIR="spark"

. /workload-client/src/marketing-workload.sh

run() {
  manage_workload_processes "$1"
  OPERATION=$1
if [ "START_PROCESSING" = "$OPERATION" ];
  then
    "/$SPARK_DIR/bin/spark-submit" --master spark://10.16.3.91:7077 --conf "spark.executor.memory=1G" --conf "spark.executor.cores=4" --class spark.benchmark.KafkaRedisAdvertisingStream /workload-client/src/spark-benchmarks/target/spark-benchmarks-0.1.0.jar "$CONF_FILE" &
    sleep 5
  elif [ "STOP_PROCESSING" = "$OPERATION" ];
  then
    stop_if_needed spark.benchmark.KafkaRedisAdvertisingStream "Spark Client Process"
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
