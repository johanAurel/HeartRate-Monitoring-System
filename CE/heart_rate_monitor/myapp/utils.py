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
from .hidden import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

iot_client = boto3.client(
    'iot-data',
    region_name='eu-west-2',  # Adjust as necessary
    aws_access_key_id= AWS_ACCESS_KEY_ID,
    aws_secret_access_key= AWS_SECRET_ACCESS_KEY,
)

cloudwatch_client = boto3.client(
    'cloudwatch',
    region_name='eu-west-2',
    aws_access_key_id= AWS_ACCESS_KEY_ID,# I disabled user  
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)
TOPIC='sdk/test/python'
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
    rate = random.randint(60, 115)
    timestamp = timezone.now()

    # Create a new Heartbeat instance
    heartbeat = Heartbeat.objects.create(
        device=device,
        rate=rate,
        timestamp=timestamp
    )

    alert = None
    if rate > 100:
        alert_message = f"High Heartbeat Rate: {rate} BPM!"
        alert = Alert.objects.create(
            device=device,
            heartbeat=heartbeat,
            alert_message=alert_message
        )

    # Fetch recent heartbeats to send to the template
    recent_heartbeats = Heartbeat.objects.filter(device=device).order_by('-timestamp')[:5]
    recent_alerts = Alert.objects.filter(device=device).order_by('-id')[:5]

    # Prepare the response
    return JsonResponse({
        'rate': rate,
        'timestamp': timestamp.isoformat(),
        'alert': alert is not None,
        'recent_heartbeats': [
            {'rate': hb.rate, 'timestamp': hb.timestamp.isoformat()} 
            for hb in recent_heartbeats
        ],
        'recent_alerts': [
            {'message': alert.alert_message, 'timestamp': alert.heartbeat.timestamp.isoformat()} 
            for alert in recent_alerts
        ],
    })


# Configure the AWS IoT client
@login_required
@require_POST
def listen_to_heartbeat(request):
    device_id = request.GET.get('id')
    device = get_object_or_404(Device, id=device_id)
    endpoint = request.GET.get('endpoint')  
    aws_access_key = AWS_ACCESS_KEY_ID
    aws_secret_key = request.GET.get('aws_secret_key')  
    topic = request.GET.get('topic') 

    if not endpoint or not aws_access_key or not aws_secret_key or not topic:
        return JsonResponse({'error': 'AWS IoT endpoint and credentials are required.'})

    try:
      
        iot_client = boto3.client(
            'iot-data', 
            endpoint_url=endpoint,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name='eu-west-2'  
        )
        
        cloudwatch_client = boto3.client(
            'cloudwatch', 
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name='eu-west-2'  
        )

        # Simulate receiving data from AWS IoT (for now, we'll use get_topic_attributes)
        response = iot_client.get_topic_attributes(
            topicName=TOPIC
        )
        
        # Parse the data from the response (assuming JSON payload)
        data = json.loads(response['payload'])
        timestamp = data.get('timestamp')
        rate = data.get('rate')
        
        if timestamp and rate is not None:
            # Create Heartbeat Model
            heartbeat = Heartbeat(device=device, timestamp=timestamp, rate=rate)
            heartbeat.save()
            
            # Check for heartbeat alert (if rate > 100 BPM)
            if rate > 100:
                # Create Alert Model
                alert = Alert(device=device, message=f"High Heartbeat Rate: {rate} BPM")
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
                'timestamp': timestamp,
                'rate': rate,
                'alert': 'ALERT: High Heartbeat Rate' if rate > 100 else None
            })
        else:
            return JsonResponse({'error': 'Invalid data received from IoT.'})
    
    except Exception as e:
        return JsonResponse({'error': str(e)})