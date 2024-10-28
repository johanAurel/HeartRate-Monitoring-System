import random
import json
import time
import paho.mqtt.client as mqtt
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Device
from .forms import CustomAuthenticationForm, CustomUserCreationForm, DeviceForm # Ensure you import your custom forms
from .utils import  publish_device_status


ABNORMAL_HEARTBEAT_THRESHOLD = 100
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

def password_management_disabled(request):
    return render(request, 'password_disabled.html')

# USERS
def user_list(request):
    if request.user.is_superuser:
        users = User.objects.all()
    else:
        users = [request.user]
    
    return render(request, 'user_list.html', {'users': users})

# DEVICES
def user_devices(request, username):
    user = get_object_or_404(User, username=username)
    devices = Device.objects.filter(user=user)
    return render(request, 'user_devices.html', {'devices': devices, 'user': user})

def device_list(request):
    devices = Device.objects.all()  # Fetch all devices

    # Check for POST request to handle device status change
    if request.method == "POST":
        device_id = request.POST.get("device_id")
        status = request.POST.get("status")
        
        # Update the device status in the database
        device = get_object_or_404(Device, id=device_id)
        device.status = status
        device.save()
        
        # Publish the status change to the MQTT broker
        publish_device_status(device_id, status)
        
        # Redirect back to the device list page
        return redirect('device_list')

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
def heartbeat_rate(request, device_id):
    device = get_object_or_404(Device, id=device_id)

    if request.method == "POST":
        device.status = request.POST.get("status", device.status)
        device.save()
        return JsonResponse({'status': device.status})

    return render(request, 'heartbeat_rate.html', {'device': device})

#MQTT

def mqtt_connect(request):
    client.connect(utils.MQTT_BROKER, utils.MQTT_PORT, 60)

  # Allow POST requests without CSRF validation for this example
def connect_to_mqtt(request):
    if request.method == 'POST':
        device_id = request.POST.get('device_id')
        mqtt_broker = request.POST.get('mqtt_broker')
        
        # Here, add your logic to connect to the MQTT broker
        # For example, you could initialize the MQTT client and connect it
        
        # Return a success response
        return JsonResponse({'message': 'Connected to MQTT Broker', 'broker': mqtt_broker})
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)