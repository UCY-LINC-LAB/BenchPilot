#!/bin/bash

CONSUL_IP="x.x.x.x"
# current device's ip
DEVICE_IP="x.x.x.x"

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
  "Port": 19999,
  "EnableTagOverride": false,
  "Check": {
    "DeregisterCriticalServiceAfter": "90m",
    "HTTP": "http://$DEVICE_IP:19999/api/v1/allmetrics?format=prometheus&help=no",
    "Interval": "600s"
  }
}

EOF
) >> payload.json

curl \
    --request PUT \
    --data @payload.json \
    http://$CONSUL_IP:8500/v1/agent/service/register?replace-existing-checks=1

