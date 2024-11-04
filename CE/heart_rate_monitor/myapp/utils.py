import json
import random
from django.utils import timezone
import paho.mqtt.client as mqtt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Device

# MQTT configuration
MQTT_PORT = 1883
MQTT_HEARTBEAT_TOPIC = 'device/heartbeat'
MQTT_TOPIC = 'device/status'
heartbeats = []

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

def on_message(client, userdata, msg):
    heartbeat = int(msg.payload.decode())
    device_id = msg.topic.split('/')[1]
    heartbeats.append((device_id, heartbeat, 'alert' if heartbeat > 100 else 'normal'))

    # Send alert if heartbeat exceeds threshold
    if heartbeat > 100:
        alert_topic = f"devices/{device_id}/alert"
        client.publish(alert_topic, f"High heartbeat alert: {heartbeat}")
        print(f"Alert sent to {alert_topic} for heartbeat: {heartbeat}")

def get_heartbeat_from_mqtt():
    """Retrieve heartbeat rate from MQTT"""
    # Assume we're simulating the most recent heartbeat data from `heartbeats`
    if heartbeats:
        device_id, heartbeat_rate, status = heartbeats[-1]
        last_heartbeat = timezone.now()
        return heartbeat_rate, last_heartbeat
    else:
        return None, None

def send_mqtt_alert(heartbeat_rate):
    """Send an alert to MQTT if the heartbeat is too high."""
    alert_message = f"Alert: High Heartbeat - {heartbeat_rate} BPM!"
    client.publish(MQTT_TOPIC, alert_message)

# Simulation endpoint

@login_required
@require_POST
def simulate_heartbeat(request):
    device_id = request.POST.get('device_id')
    device = get_object_or_404(Device, id=device_id)

    # Generate a random heartbeat rate for simulation
    heartbeat_rate = random.randint(40, 110)
    timestamp = timezone.now().isoformat()

    return JsonResponse({
        'heartbeat_rate': heartbeat_rate,
        'last_heartbeat': timestamp,
    })
    
# Main MQTT handler
def connect_to_mqtt(request, mqtt_broker='localhost'):
    """
    Connects to the MQTT broker and manages heartbeat data.
    Provides simulated data if MQTT data is unavailable.
    """
    if request.method == 'POST':
        use_mqtt = request.POST.get('use_mqtt', 'true').lower() == 'true'
        
        if use_mqtt:
            client.connect(mqtt_broker, MQTT_PORT, 60)
            client.loop_start()
            client.on_message = on_message
            client.subscribe(MQTT_TOPIC)

            # Get heartbeat data from MQTT
            heartbeat_rate, last_heartbeat = get_heartbeat_from_mqtt()
        else:
            # Use simulation data
            heartbeat_rate, last_heartbeat = simulate_heartbeat(request)

        if heartbeat_rate is not None and heartbeat_rate > 100:
            send_mqtt_alert(heartbeat_rate)

        return JsonResponse({
            'heartbeat_rate': heartbeat_rate,
            'last_heartbeat': last_heartbeat.isoformat() if last_heartbeat else None,
            'alert': heartbeat_rate > 100 if heartbeat_rate else False,
            'source': 'MQTT' if use_mqtt else 'Simulation'
        })

    return JsonResponse({'error': 'Invalid request method'}, status=400)

