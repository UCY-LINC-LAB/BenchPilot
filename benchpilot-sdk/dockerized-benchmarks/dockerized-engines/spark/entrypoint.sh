#!/bin/bash

start_spark() {
  
  if [ $1 == "master" ];
  then
    shift
    /spark/sbin/start-master.sh "$@";
    tail -f /spark/logs/spark--org.apache.spark.deploy.master.Master*
  elif [ $1 == "worker" ];
  then
    shift
    /spark/sbin/start-slave.sh "$@";
    tail -f /spark/logs/spark--org.apache.spark.deploy.worker.Worker*;
  else
    echo "You haven't given a valid spark command"
    exit 1
  fi
}

if [ $# -lt 1 ];
then
  echo "You need to give a spark command"
  echo "first specify if you want to start a master or a worker, and then their parameters"
else
  start_spark "$@"
fi
