#!/bin/bash
# Copyright 2015, Yahoo Inc.
# Licensed under the terms of the Apache License 2.0. Please see LICENSE file in the project root for terms.
set -o pipefail
set -o errtrace
set -o nounset
set -o errexit

FLINK_VERSION=${FLINK_VERSION:-"1.11.3"}
SCALA_BIN_VERSION=${SCALA_BIN_VERSION:-"2.11"}
FLINK_DIR="flink-$FLINK_VERSION"


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
    #Fetch Flink
    FILE="$FLINK_DIR-bin-scala_${SCALA_BIN_VERSION}.tgz"
    fetch_untar_file "$FILE" "$APACHE_MIRROR/flink/flink-$FLINK_VERSION/$FILE"
    
    cp ./conf/flink-config.yaml ./$FLINK_DIR/conf/flink-conf.yaml

  elif [ "START_MANAGER" = "$OPERATION" ];
  then
    start_if_needed org.apache.flink.runtime.jobmanager.JobManager Flink 1 $FLINK_DIR/bin/start-cluster.sh
    start_if_needed org.apache.flink.runtime.taskmanager.TaskManager Flink 1 $FLINK_DIR/bin/taskmanager.sh stop
  elif [ "START_WORKER" = "$OPERATION" ];
  then
    start_if_needed org.apache.flink.runtime.taskmanager.TaskManager Flink 1 $FLINK_DIR/bin/taskmanager.sh start
  elif [ "STOP_FLINK" = "$OPERATION" ];
  then
    $FLINK_DIR/bin/stop-cluster.sh
  else
    if [ "HELP" != "$OPERATION" ];
    then
      echo "UNKOWN OPERATION '$OPERATION'"
      echo
    fi
    echo "Supported Operations:"
    echo "SETUP: download and setup dependencies for flink only"
    echo "START_MANAGER: run flink job MANAGER processes"
    echo "STOP_MANAGER: kill flink job MANAGER processes"
    echo "START_WORKER: run flink task MANAGER processes"
    echo "STOP_WORKER: kill flink task MANAGER processes"
    echo "STOP_FLINK: to stop the whole cluster"
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
