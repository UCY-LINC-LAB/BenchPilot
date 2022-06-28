#!/bin/bash
# Copyright 2015, Yahoo Inc.
# Licensed under the terms of the Apache License 2.0. Please see LICENSE file in the project root for terms.
set -o pipefail
set -o errtrace
set -o nounset
set -o errexit

STORM_VERSION=${STORM_VERSION:-"1.2.3"}

STORM_DIR="apache-storm-$STORM_VERSION"

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
    #Fetch Storm
    STORM_FILE="$STORM_DIR.tar.gz"
    fetch_untar_file "$STORM_FILE" "$APACHE_MIRROR/storm/$STORM_DIR/$STORM_FILE"

    cp ./conf/storm.yaml ./$STORM_DIR/conf/storm.yaml
  elif [ "START_MANAGER" = "$OPERATION" ];
  then
    start_if_needed daemon.name=nimbus "Storm Nimbus" 3 "$STORM_DIR/bin/storm" nimbus
    start_if_needed daemon.name=logviewer "Storm LogViewer" 3 "$STORM_DIR/bin/storm" logviewer
  elif [ "START_WORKER" = "$OPERATION" ];
  then
    start_if_needed daemon.name=supervisor "Storm Supervisor" 3 "$STORM_DIR/bin/storm" supervisor
  elif [ "START_UI" = "$OPERATION" ];
  then
    start_if_needed daemon.name=ui "Storm UI" 3 "$STORM_DIR/bin/storm" ui
  elif [ "STOP_UI" = "$OPERATION" ];
  then
    stop_if_needed daemon.name=ui "Storm UI"
  elif [ "STOP_MANAGER" = "$OPERATION" ];
  then
    stop_if_needed daemon.name=nimbus "Storm Nimbus"
    stop_if_needed daemon.name=logviewer "Storm LogViewer"
  elif [ "STOP_WORKER" = "$OPERATION" ];
  then
    stop_if_needed daemon.name=supervisor "Storm Supervisor"
  else
    if [ "HELP" != "$OPERATION" ];
    then
      echo "UNKOWN OPERATION '$OPERATION'"
      echo
    fi
    echo "Supported Operations:"
    echo "SETUP: download and setup dependencies for storm only"
    echo "START_MANAGER: run storm nimbus daemon in the background"
    echo "STOP_MANAGER: kill the storm nimbus daemon"
    echo "START_WORKER: run storm supervisor daemon in the background"
    echo "STOP_WORKER: kill the storm supervisor daemon"
    echo "START_UI: run storm ui daemon in the background"
    echo "START_UI: kill the storm ui daemon"
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
