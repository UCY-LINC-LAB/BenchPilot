# Commands to build the following benchpilot images:

## WORKLOAD-CLI (base image)
```
docker buildx build --platform linux/amd64,linux/arm64/v8,linux/arm/v7 -t benchpilot/benchpilot:workload-cli --push .
```

## STORM-CLI (based on 2.2.0), same goes for flink and spark
```
docker buildx build --platform linux/amd64,linux/arm64/v8,linux/arm/v7 -t benchpilot/benchpilot:workload-cli-storm-2.2.0 $(for i in `cat build-args-storm.txt`; do out+="--build-arg $i " ; done; echo $out;out="") --file Dockerfile_yahoo_client --push .
```

## STORM ENGINE (based on 2.2.0), same goes for flink and spark
```
docker buildx build --platform linux/amd64,linux/arm64/v8,linux/arm/v7 -t benchpilot/benchpilot:sdpe-storm-2.2.0 --build-arg STORM_VERSION=2.2.0 --push .
```