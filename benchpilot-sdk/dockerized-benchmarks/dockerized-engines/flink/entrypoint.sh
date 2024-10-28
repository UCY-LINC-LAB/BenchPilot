#!/bin/bash

start_flink() {
  
  if [ $1 == "taskmanager" ];
  then
    shift
    bin/bash /flink/bin/taskmanager.sh "$@";
  elif [ $1 == "jobmanager" ];
  then
    shift
    bin/bash /flink/bin/jobmanager.sh "$@";
  else
    echo "You haven't given a valid flink command"
    exit 1
  fi
}

if [ $# -lt 1 ];
then
  echo "You need to give a flink command"
  echo "first specify if you want to start a taskmanager or a jobmanager, and then their parameters"
else
  start_flink "$@"
fi
