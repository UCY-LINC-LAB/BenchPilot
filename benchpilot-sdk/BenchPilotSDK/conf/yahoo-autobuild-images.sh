#!/bin/bash

# build benchpilot
# docker build -t registry.gitlab.com/jgeorg02/linc-streaming-benchmarking/bench-pilot:latest -f ~/workspace-linc/linc-streaming-benchmarking/Dockerfile_jupyter .

#build engines
cd ~/workspace-linc/linc-streaming-benchmarking/benchPilot/dockerized-benchmarks/engine-dockerfiles/flink-engine
docker build -t registry.gitlab.com/jgeorg02/linc-streaming-benchmarking/linc-flink-engine-cluster:latest -f Dockerfile_flink_cluster .
cd ~/workspace-linc/linc-streaming-benchmarking/benchPilot/dockerized-benchmarks/engine-dockerfiles/storm-engine
docker build -t registry.gitlab.com/jgeorg02/linc-streaming-benchmarking/linc-storm-engine-cluster:latest -f Dockerfile_storm_cluster .
cd ~/workspace-linc/linc-streaming-benchmarking/benchPilot/dockerized-benchmarks/engine-dockerfiles/spark-engine
docker build -t registry.gitlab.com/jgeorg02/linc-streaming-benchmarking/linc-spark-engine-cluster:latest -f Dockerfile_spark_cluster .

# build clients
cd ~/workspace-linc/linc-streaming-benchmarking/benchPilot/dockerized-benchmarks/workload-client
docker build -t registry.gitlab.com/jgeorg02/linc-streaming-benchmarking/linc-spark-engine-client:latest -f Dockerfile_yahoo_spark_client .
docker build -t registry.gitlab.com/jgeorg02/linc-streaming-benchmarking/linc-storm-engine-client:latest -f Dockerfile_yahoo_storm_client .
docker build -t registry.gitlab.com/jgeorg02/linc-streaming-benchmarking/linc-flink-engine-client:latest -f Dockerfile_yahoo_flink_client .

# docker push registry.gitlab.com/jgeorg02/linc-streaming-benchmarking/bench-pilot:latest
docker push registry.gitlab.com/jgeorg02/linc-streaming-benchmarking/linc-flink-engine-cluster:latest
docker push registry.gitlab.com/jgeorg02/linc-streaming-benchmarking/linc-storm-engine-cluster:latest
docker push registry.gitlab.com/jgeorg02/linc-streaming-benchmarking/linc-spark-engine-cluster:latest
docker push registry.gitlab.com/jgeorg02/linc-streaming-benchmarking/linc-spark-engine-client:latest
docker push registry.gitlab.com/jgeorg02/linc-streaming-benchmarking/linc-storm-engine-client:latest
docker push registry.gitlab.com/jgeorg02/linc-streaming-benchmarking/linc-flink-engine-client:latest
