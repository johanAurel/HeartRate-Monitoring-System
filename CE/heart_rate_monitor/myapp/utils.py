import json
import random
from django.utils import timezone
import paho.mqtt.client as mqtt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Device, Alert ,Heartbeat

# MQTT configuration
MQTT_PORT = 1883
MQTT_HEARTBEAT_TOPIC = 'device/heartbeat'
MQTT_TOPIC = 'device/status'
heartbeats = []

# Initialize MQTT client
mqtt_client = mqtt.Client()



@login_required
def toggle_device_status(request):
    if request.method == "POST":
        device_id = request.POST.get("device_id")
        device = get_object_or_404(Device, id=device_id)

        # Toggle the device status
        if device.status == "ON":
            device.status = "OFF"
        else:
            device.status = "ON"
        device.save()

        return JsonResponse({'status': device.status})
    return JsonResponse({'error': 'Invalid request'}, status=400)
    
@login_required
@require_POST
def simulate_heartbeat(request):
    device_id = request.POST.get('device_id')
    device = get_object_or_404(Device, id=device_id)

    # Generate a random heartbeat rate for simulation
    heartbeat_rate = random.randint(60, 115)
    timestamp = timezone.now()

    # Create a new Heartbeat instance
    heartbeat = Heartbeat.objects.create(
        device=device,
        heartbeat_rate=heartbeat_rate,
        last_heartbeat=timestamp
    )

    alert = None
    if heartbeat_rate > 100:
        alert_message = f"High Heartbeat Rate: {heartbeat_rate} BPM!"
        alert = Alert.objects.create(
            device=device,
            heartbeat=heartbeat,
            alert_message=alert_message
        )

    # Fetch recent heartbeats to send to the template
    recent_heartbeats = Heartbeat.objects.filter(device=device).order_by('-last_heartbeat')[:5]
    recent_alerts = Alert.objects.filter(device=device).order_by('-id')[:5]

    # Prepare the response
    return JsonResponse({
        'heartbeat_rate': heartbeat_rate,
        'last_heartbeat': timestamp.isoformat(),
        'alert': alert is not None,
        'recent_heartbeats': [
            {'heartbeat_rate': hb.heartbeat_rate, 'timestamp': hb.last_heartbeat.isoformat()} 
            for hb in recent_heartbeats
        ],
        'recent_alerts': [
            {'message': alert.alert_message, 'timestamp': alert.heartbeat.last_heartbeat.isoformat()} 
            for alert in recent_alerts
        ],
    })


