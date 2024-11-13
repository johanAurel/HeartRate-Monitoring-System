import json
import random
import boto3
from django.utils import timezone
import paho.mqtt.client as mqtt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Device, Alert ,Heartbeat

iot_client = boto3.client(
    'iot-data',
    region_name='us-east-1',  # Adjust as necessary
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

cloudwatch_client = boto3.client(
    'cloudwatch',
    region_name='eu-west-2',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

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


# Configure the AWS IoT client


def listen_to_heartbeat(request):
    device_id = request.GET.get('id')
    device = get_object_or_404(Device, device_id=device_id)
    
    # Here, we will simulate receiving data from AWS IoT (e.g., using a subscription to a topic)
    response = iot_client.get_topic_attributes(
        topicName=TOPIC
    )
    
    data = json.loads(response['payload'])
    last_heartbeat = data.get('last_heartbeat')
    heartbeat_rate = data.get('heartbeat_rate')
    
    # Create Heartbeat Model
    heartbeat = Heartbeat(device=device, last_heartbeat=last_heartbeat, heartbeat_rate=heartbeat_rate)
    heartbeat.save()
    
    # Check for heartbeat alert (if rate > 100 BPM)
    if heartbeat_rate > 100:
        # Create Alert Model
        alert = Alert(device=device, message=f"High Heartbeat Rate: {heartbeat_rate} BPM")
        alert.save()

        # Send an alert to AWS CloudWatch
        cloudwatch_client.put_metric_data(
            Namespace='HeartbeatMetrics',
            MetricData=[
                {
                    'MetricName': 'HighHeartbeatAlert',
                    'Dimensions': [
                        {
                            'Name': 'DeviceId',
                            'Value': device.device_id
                        },
                    ],
                    'Value': 1,
                    'Unit': 'Count'
                },
            ]
        )

        # Optionally, send an alert to AWS IoT (e.g., publish to a topic)
        iot_client.publish(
            topic=TOPIC,
            qos=1,
            payload=json.dumps({'message': f"High Heartbeat Alert for {device.device_name}"})
        )
        
    return JsonResponse({
        'last_heartbeat': last_heartbeat,
        'heartbeat_rate': heartbeat_rate,
        'alert': 'ALERT: High Heartbeat Rate' if heartbeat_rate > 100 else None
    })
