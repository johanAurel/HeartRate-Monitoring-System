from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from .forms import CustomAuthenticationForm, CustomUserCreationForm, DeviceForm # Ensure you import your custom forms
from .models import Device
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .utils import  *


def conditional_home(request):
    if request.user.is_authenticated:
        return render(request, 'home.html')  # Show home.html if logged in
    else:
        return render(request, 'base.html')  # Show base.html if not logged in

# LOGIN / REGISTER / LOGOUT
def login_view(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, "You have successfully logged in.")
                return redirect('conditional_home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid credentials. Please try again.")
    
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'login.html', {'form': form})

def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Account created for {username}!")
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'register.html', {'form': form})

def logout_view(request):
    logout(request)  # Logout the user
    return redirect('conditional_home')  # Redirect to conditional home after logout

@login_required
def update_account(request):
    # Make changes to the user account here

    # Once changes are made, trigger a WebSocket message
    channel_layer = get_channel_layer()
    group_name = f"account_changes_{request.user.id}"

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "account_update",
            "message": "Your account details have been updated!",
        }
    )
    
def password_management_disabled(request):
    return render(request, 'password_disabled.html')

# USERS
@login_required
def user_list(request):
    if request.user.is_superuser:
        User = get_user_model()
        users = User.objects.all()
    else:
        users = [request.user]
    
    return render(request, 'user_list.html', {'users': users})

# DEVICES
@login_required
def device_list(request):
    # Check if the user is a superuser or not
    if request.user.is_superuser:
        # Superuser sees all devices
        devices = Device.objects.all()
    else:
        # Regular user sees only their devices
        devices = Device.objects.filter(user=request.user)

    # Check for POST request to handle device status change
    if request.method == "POST":
        device_id = request.POST.get("device_id")
        status = request.POST.get("status")
        
        # Fetch the device based on the logged-in user and device_id
        device = get_object_or_404(Device, id=device_id)
        
        # Ensure the device belongs to the logged-in user or is a superuser
        if device.user != request.user and not request.user.is_superuser:
            # Return an error or show a message
            return redirect('device_list')  # Redirect to the device list page if not authorized
        
        # Update the device status in the database
        device.status = status
        device.save()
        
        # Publish the status change to the MQTT broker
        publish_device_status(device_id, status)
        
        # Redirect back to the device list page
        return redirect('device_list')
    for device in devices:
       print(type(device.user.username))  
       
    return render(request, 'device_list.html', {'devices': devices})

def add_device(request):
    if request.method == 'POST':
        form = DeviceForm(request.POST)
        if form.is_valid():
            form.save()  # This saves the device to the database
            return redirect('device_list')  # Redirect to the device list view
    else:
        form = DeviceForm()
    return render(request, 'add_device.html', {'form': form})

def change_device_status(request):

    if request.method == "POST":
        device_id = request.POST.get("device_id")
        new_status = request.POST.get("status")
        
        # Update the device status in the database
        device = Device.objects.get(id=device_id)
        device.status = new_status
        device.save()
        
        # Redirect to the device list or send a success response
        return JsonResponse({'status': device.status})
    
    # If GET request, render the change status template
    device = Device.objects.get(id=request.GET.get("device_id"))
    return render(request, 'change_device_status.html', {'device': device})

# HEARTBEAT
@login_required
def heartbeat_rate(request):
    
    device_id = request.GET.get('id')
    device = get_object_or_404(Device, id = device_id)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "update_status":
            # Update the device status
            device.status = request.POST.get("status", device.status)
            device.save()
            return JsonResponse({'status': device.status})

        elif action == "connect_mqtt":
            # Connect to MQTT broker
            mqtt_broker = request.POST.get("mqtt_broker")
            success = connect_to_mqtt(mqtt_broker)
            return JsonResponse({'message': 'Connected to MQTT Broker', 'broker': mqtt_broker}) if success else JsonResponse({'error': 'Failed to connect'}, status=400)

        elif action == "simulate_heartbeat":
            # Simulate heartbeat rate
            heartbeat_data = simulate_heartbeat(device)
            return JsonResponse({
                'heartbeat_rate': heartbeat_data['heartbeat_rate'],
                'last_heartbeat': heartbeat_data['last_heartbeat']
            })

    # Render the heartbeat rate template
    return render(request, 'heartbeat_rate.html', {'device': device})

#MQTT
@csrf_exempt
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    # Subscribe to the heartbeat topic (e.g., "device/{device_id}/heartbeat")
    device_id = userdata['device_id']
    mqtt_client.subscribe(f"device/{device_id}/heartbeat")

def on_message(client, userdata, msg):
    # Parse the message payload (assuming it's in JSON format)
    message = json.loads(msg.payload)
    device_id = userdata['device_id']
    heartbeat_rate = message.get('heartbeat_rate')
    last_heartbeat = message.get('last_heartbeat')

    # Process the received heartbeat data
    device = Device.objects.get(id=device_id)
    heartbeat = Heartbeat.objects.create(device=device, heartbeat_rate=heartbeat_rate, last_heartbeat=last_heartbeat)

    # Check if the heartbeat rate triggers an alert
    alert = Heartbeat.check_and_create_alert(device)

    # If an alert was created, send it via WebSocket
    if alert:
        send_alert_to_websocket(device, alert.alert_message)

def publish_device_status(device_id, status):
    """Publish the device status to the MQTT broker."""
    try:
        # Ensure we're connected to the broker
        if not mqtt_client.is_connected():
            connect_to_mqtt()

        # Define the topic for this device
        topic = f"{MQTT_TOPIC}/?id={device_id}"
        
        # Publish the status message
        payload = f"{status}"  # The status (ON or OFF)
        mqtt_client.publish(topic, payload, qos=1)
        
        print(f"Published status: {status} for device: {device_id} on topic: {topic}")

    except Exception as e:
        print(f"Error publishing device status: {e}")

def connect_to_mqtt(device_id, mqtt_broker):
    """
    Connects to the MQTT broker and starts subscribing to the device's heartbeat topic.
    """
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    # Set up user data for the device
    userdata = {'device_id': device_id}

    # Connect to the MQTT broker
    mqtt_client.user_data_set(userdata)
    mqtt_client.connect(mqtt_broker)

    # Start the MQTT client loop
    mqtt_client.loop_start()

# Example WebSocket alert notification
def send_alert_to_websocket(device, alert_message):
    channel_layer = get_channel_layer()
    # Send alert message to WebSocket group corresponding to the device
    channel_layer.group_send(
        f"device_{device.id}",
        {
            "type": "device_alert",
            "message": alert_message
        }
    )
    # Here it would send an alert via WebSocket to the device
    # For example, using Django Channels or other real-time technologies
    # For demonstration, I simulate this as a function:
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.send)(
        f"device_{device.id}", {
            "type": "device.alert",
            "message": alert_message
        }
    )