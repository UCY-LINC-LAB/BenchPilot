#!/bin/bash

mongod --logpath /var/log/mongodb/mongod.log &
sleep 2
# Check if the DURATION environment variable is set, default to 1 if not set.
DURATION=${DURATION:-1}
THREADS=${THREADS:-1}
RECORDCOUNT=${RECORDCOUNT:-2500000}
OPERATIONCOUNT=${OPERATIONCOUNT:-2500000}

# Create the experiment.txt file
cat > /db-benchmark/workloads/workloada <<EOF
recordcount=$RECORDCOUNT
operationcount=$OPERATIONCOUNT
workload=site.ycsb.workloads.CoreWorkload

readproportion=0.5
updateproportion=0.5
scanproportion=0
insertproportion=0

requestdistribution=zipfian
EOF
mkdir /output

# Until the workload's time is over, keep benchmarking
start_time=$(date +%s)  # Get the current timestamp in seconds

while true; do
    current_time=$(date +%s)  # Get the current timestamp in seconds
    elapsed_time=$((current_time - start_time))

    if [ $elapsed_time -lt $DURATION ]; then
        ./bin/ycsb load mongodb-async -threads $THREADS -s -P workloads/workloada > /output/outputLoad.txt && ./bin/ycsb run mongodb-async -threads $THREADS -s -P workloads/workloada > /output/outputRun.txt
        mongo ycsb --eval "db.dropDatabase()"
    else
        break  # Exit the loop once the duration has passed
    fi
done