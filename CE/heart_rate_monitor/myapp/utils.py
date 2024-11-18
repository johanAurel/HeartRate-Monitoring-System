import json
import random
import boto3
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from .models import Device, Alert ,Heartbeat, MyCustomUser

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

def create_cloudwatch_alarm(device_id, rate_threshold, user_email, access_key , secret_key):
    
    cloudwatch_client = boto3.client('cloudwatch', region_name='eu-west-2', aws_access_key_id = access_key, aws_secret_access_key = secret_key)
    sns_client = boto3.client('sns', region_name='eu-west-2')

    # Define SNS topic for email alerts
    topic_response = sns_client.create_topic(Name=f"heartbeat_alerts_{device_id}")
    topic_arn = topic_response['TopicArn']
    
    # Subscribe the user to the topic to receive email alerts
    sns_client.subscribe(
        TopicArn=topic_arn,
        Protocol='email',
        Endpoint=user_email
    )
    
    # Create a CloudWatch alarm for the 'rate' metric
    alarm_name = f"HeartbeatRateAlarm_{device_id}"
    cloudwatch_client.put_metric_alarm(
        AlarmName=alarm_name,
        MetricName='rate',
        Namespace='HeartbeatMetrics',
        Statistic='Average',
        Period=60,  # Evaluate every 60 seconds
        EvaluationPeriods=1,
        Threshold=rate_threshold,
        ComparisonOperator='GreaterThanThreshold',
        ActionsEnabled=True,
        AlarmActions=[topic_arn],  # Trigger SNS alert
        AlarmDescription=f"Alarm when heartbeat rate exceeds {rate_threshold} BPM for device {device_id}"
    )

    # Send initial confirmation email to the user
    send_mail(
        subject="CloudWatch Alarm Setup for Heartbeat Rate",
        message=f"A CloudWatch alarm has been configured for device {device_id}. "
                f"You will be alerted via email if the heartbeat rate exceeds {rate_threshold} BPM.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )

    return {"message": f"CloudWatch alarm '{alarm_name}' created and email subscription confirmed."}

def trigger_cloudwatch_alarm(device_id, rate, access_key , secret_key):
    cloudwatch_client = boto3.client('cloudwatch', region_name='eu-west-2', aws_access_key_id = access_key, aws_secret_access_key = secret_key)

    # Publish the metric data to CloudWatch
    metric_namespace = "HeartbeatMetrics"
    metric_name = "rate"
    
    cloudwatch_client.put_metric_data(
        Namespace=metric_namespace,
        MetricData=[
            {
                'MetricName': metric_name,
                'Dimensions': [
                    {'Name': 'DeviceID', 'Value': device_id}
                ],
                'Value': rate,
                'Unit': 'Count'  # Assuming rate is a numerical count (beats per minute)
            }
        ]
    )
    
    
    print(f"Triggered alarm: Heartbeat rate {rate} exceeds threshold is abnormal!!!!!!!!")
    return {
            "status": "Triggered",
            "message": f" {rate}BPM is awy too high!!!!",
        }

# Configure the AW  S IoT client
@login_required
@csrf_protect
@require_POST
def listen_to_heartbeat(request):
    # Retrieve device and AWS parameters
    device_id = request.POST.get('device_id')
    device = get_object_or_404(Device, id=device_id)
    user_id = request.POST.get('user_id')
    user_email = get_object_or_404(MyCustomUser, id=user_id).email

    endpoint = request.POST.get('aws-endpoint')
    aws_access_key = request.POST.get('aws-access-key')
    aws_secret_key = request.POST.get('aws-secret-key')
    topic = request.POST.get('topic')

    # Check for required parameters
    if not endpoint or not aws_access_key or not aws_secret_key or not topic:
        return JsonResponse({'error': 'AWS IoT endpoint and credentials are required.'})

    try:
        # Initialize IoT client
        iot_client = boto3.client('iot-data', endpoint_url=endpoint,
                                  aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key,
                                  region_name='eu-west-2')

        cloudwatch_client = boto3.client('cloudwatch', region_name='eu-west-2',
                                         aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)

        # Ensure the CloudWatch alarm exists
        alarm_name = f"HeartbeatRateAlarm_{device_id}"
        alarms = cloudwatch_client.describe_alarms(AlarmNames=[alarm_name])

        if not alarms['HeartbeatMetrics']:  # Create alarm if it doesn't exist
            create_cloudwatch_alarm(device_id, 100, user_email, aws_access_key, aws_secret_key)

        # Retrieve real-time IoT message payload
        response = iot_client.get_thing_shadow(thingName=device_id)
        payload = json.loads(response['payload'].read().decode('utf-8'))

        desired_state = payload["state"].get("desired", {})

        # Extract desired values
        rate = desired_state.get("rate")
        timestamp = desired_state.get("timestamp")

        if timestamp and rate is not None:
            # Save the heartbeat
            Heartbeat.objects.create(device=device, rate=rate, timestamp=timestamp)

            # Add alert if the rate exceeds the threshold
            alert = None
            if rate > 100:  # Threshold
                alert = Alert.objects.create(device=device, alert_message=f"High Heartbeat Rate: {rate} BPM")
                
                # Publish metric to CloudWatch
                trigger_cloudwatch_alarm(device_id, rate, aws_access_key, aws_secret_key)

            # Return recent data for the UI
            recent_heartbeats = Heartbeat.objects.filter(device=device).order_by('-timestamp')[:5]
            recent_alerts = Alert.objects.filter(device=device).order_by('-id')[:5]

            return JsonResponse({
                'rate': rate,
                'timestamp': timestamp,
                'alert': alert is not None,
                'recent_heartbeats': [{'rate': hb.rate, 'timestamp': hb.timestamp.isoformat()} for hb in recent_heartbeats],
                'recent_alerts': [{'message': al.alert_message, 'timestamp': al.heartbeat.timestamp.isoformat()} for al in recent_alerts],
            })
        else:
            return JsonResponse({'error': 'Invalid data received from AWS IoT.'})

    except Exception as e:
        return JsonResponse({'error': str(e)})
