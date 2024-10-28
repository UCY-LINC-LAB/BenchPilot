#!/bin/bash

CONSUL_IP="x.x.x.x"
CONSUL_PORT="8500"
# current device's ip
DEVICE_IP="x.x.x.x"
NETDATA_PORT="19999"

rm -f ./payload.json

echo $(cat <<EOF
{
  "ID": "$(hostname)",
  "Name": "$(hostname)",
  "Tags": [
    "uCatascopia",
    "$(hostname)"
  ],
  "Address": "$DEVICE_IP",
  "Port": $NETDATA_PORT,
  "EnableTagOverride": false,
  "Check": {
    "DeregisterCriticalServiceAfter": "90m",
    "HTTP": "http://$DEVICE_IP:$NETDATA_PORT/api/v1/allmetrics?format=prometheus&help=no",
    "Interval": "600s"
  }
}

EOF
) >> payload.json

curl \
    --request PUT \
    --data @payload.json \
    http://$CONSUL_IP:$CONSUL_PORT/v1/agent/service/register?replace-existing-checks=1

