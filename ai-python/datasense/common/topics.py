"""
common/topics.py

Single source of truth for MQTT topic names. Import these constants rather
than typing topic strings inline anywhere — a typo in a topic string fails
silently (nobody's subscribed to the misspelled topic, no error is raised),
so centralizing it here removes an entire class of bug.
"""

INGESTION_COMPLETE = "pipeline/ingestion/complete"
ANOMALY_ALERT = "pipeline/anomaly/alert"

# Retained from the original CloudWatch-simulator design for possible future
# use — dataset/severity-scoped topics allow selective subscription.
def dq_alert_topic(dataset: str, severity: str) -> str:
    return f"datasense/alerts/dq/{dataset}/{severity}"