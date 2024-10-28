#!/bin/bash

start_storm() {
  re='^[0-9]+$'
  if ! [[ $EXECUTORS =~ $re ]] ; then
    EXECUTORS=4
  fi
  for (( i=4; i<$EXECUTORS; i++))
  do
    port=$((6700+$i))
    echo "    - $port" >> /storm/conf/storm.yaml
  done
  
  /storm/bin/storm $1;
  sleep infinity;
}

if [ $# -lt 1 ];
then
  echo "You need to give a storm command"
else
  start_storm "$1"
fi
