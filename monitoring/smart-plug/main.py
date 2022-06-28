import json
import os
from venv import logger

import requests
from prometheus_client.metrics_core import GaugeMetricFamily
from prometheus_client.registry import CollectorRegistry

url = str(os.getenv("SMART_PLUG_URL"))
config_path = str(os.getenv("CONFIG_PATH"))
prefix = str(os.getenv("PREFIX"))
timeout = int(os.getenv("TIMEOUT"))

registry = CollectorRegistry()


class CustomCollector(object):
    def collect(self):
        try:
            payload = json.dumps({
                "header": {
                    "from": "/app/cd33257b7e1c57ab29cbe2c35f53553d95fce690a040001251c8381025e3051e/subscribe",
                    "messageId": "de56fd2fe7b1fa30dc5d6c91b6f088e0",
                    "method": "GET",
                    "namespace": "Appliance.Control.Electricity",
                    "payloadVersion": 1,
                    "sign": "a87581dd22b84cd185702561810c0d16",
                    "timestamp": 1641987971
                },
                "payload": {}
            })
            headers = {
                'Content-Type': 'application/json'
            }
            power_response = requests.request("POST", f"http://{url}/{config_path}",
                                              headers=headers,
                                              data=payload).json()
        except Exception:
            logger.error("Exception during raspberry's data request")
        yield self.create_power_graph(power_response)

    def get_power_and_timestamp(self, power_response):
        power = power_response.get('payload').get('electricity').get('power')
        timestamp = power_response.get('header').get('timestamp')
        return power, timestamp

    def create_power_graph(self, power_response):
        power, timestamp = self.get_power_and_timestamp(power_response)
        power /= 1000.0
        c = GaugeMetricFamily(f'{prefix}power_W', '', labels=['chart', 'family', 'dimension'])
        c.add_metric(value=power, labels=['smart_plug.power', 'smart_plug', 'power'],
                     timestamp=timestamp)
        return c


registry.register(CustomCollector())

from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app

# Create my app
app = Flask(__name__)

# Add prometheus wsgi middleware to route /metrics requests
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/api/v1/allmetrics': make_wsgi_app(registry)
})

app.run(host="0.0.0.0", port=19998)
