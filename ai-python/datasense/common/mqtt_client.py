"""
common/mqtt_client.py

Fire-and-forget publish helper, used by the ingestion engine and the DQ
worker for their one-off publishes (ingestion complete / anomaly alert).
This is NOT what the DQ worker or AI layer use for SUBSCRIBING — a
persistent subscriber needs its own long-lived paho.mqtt.client.Client with
a loop, built directly in dq_pipeline.py, not through this helper.
"""

import json
import os

import paho.mqtt.publish as publish


def publish_message(topic: str, payload: dict) -> None:
    host = os.environ.get("MQTT_HOST", "localhost")
    port = int(os.environ.get("MQTT_PORT", 1883))
    publish.single(topic, payload=json.dumps(payload), hostname=host, port=port)