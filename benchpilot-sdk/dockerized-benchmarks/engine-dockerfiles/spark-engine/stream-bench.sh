#!/bin/bash
# Copyright 2015, Yahoo Inc.
# Licensed under the terms of the Apache License 2.0. Please see LICENSE file in the project root for terms.
set -o pipefail
set -o errtrace
set -o nounset
set -o errexit

SPARK_VERSION=${SPARK_VERSION:-"2.4.7"}

SPARK_DIR="spark-$SPARK_VERSION-bin-hadoop2.7"

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
  tar -xzvf "$FILE"
  rm "$FILE"
}


run() {
  OPERATION=$1
  if [ "SETUP" = "$OPERATION" ];
  then
    #Fetch Spark
    SPARK_FILE="$SPARK_DIR.tgz"
    fetch_untar_file "$SPARK_FILE" "$APACHE_MIRROR/spark/spark-$SPARK_VERSION/$SPARK_FILE"

  elif [ "START_MANAGER" = "$OPERATION" ];
  then
    start_if_needed org.apache.spark.deploy.master.Master SparkMaster 5 $SPARK_DIR/sbin/start-master.sh -h 0.0.0.0 -p $MANAGER_PORT
  elif [ "STOP_MANAGER" = "$OPERATION" ];
  then
    stop_if_needed org.apache.spark.deploy.master.Master SparkMaster
    sleep 3
  elif [ "START_WORKER" = "$OPERATION" ];
  then
    start_if_needed org.apache.spark.deploy.worker.Worker SparkSlave 5 $SPARK_DIR/sbin/start-slave.sh spark://$MANAGER_HOSTNAME:$MANAGER_PORT
  elif [ "STOP_WORKER" = "$OPERATION" ];
  then
    stop_if_needed org.apache.spark.deploy.worker.Worker SparkSlave
    sleep 3
  else
    if [ "HELP" != "$OPERATION" ];
    then
      echo "UNKOWN OPERATION '$OPERATION'"
      echo
    fi
    echo "Supported Operations:"
    echo "SETUP: download and setup dependencies for spark"
    echo "START_MANAGER: run spark master process"
    echo "STOP_MANAGER: kill spark master process"
    echo "START_WORKER: run spark slave process"
    echo "STOP_WORKER: kill spark slave process"
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
