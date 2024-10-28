import json
import paho.mqtt.client as mqtt
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# MQTT configuration
MQTT_BROKER = 'mqtt-broker-address'
MQTT_PORT = 1883
MQTT_HEARTBEAT_TOPIC = 'device/heartbeat'
MQTT_STATUS_TOPIC = 'device/status'

# Dictionary to store device statuses
device_statuses = {}

# Initialize MQTT client
client = mqtt.Client()

def publish_device_status(device_id, status):
    topic = f"device/{device_id}/status"
    payload = json.dumps({
        "device_id": device_id,
        "status": status
    })
    client.publish(topic, payload)
    print(f"Published {status} status to device {device_id}")

def publish_warning(device_id, message):
    # Function to publish a warning message to MQTT
    topic = f"device/{device_id}/warning"
    payload = json.dumps({
        "device_id": device_id,
        "warning": message
    })
    client.publish(topic, payload)
    print(f"Published warning to {topic}: {message}")

