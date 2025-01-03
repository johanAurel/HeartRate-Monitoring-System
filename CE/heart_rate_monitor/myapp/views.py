from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import get_user_model, authenticate, login
from .forms import  CustomUserCreationForm, DeviceForm # Ensure you import your custom forms
from .models import Device, MyCustomUser
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import AuthenticationForm
from .utils import  *


def conditional_home(request):
    if request.user.is_authenticated:
        return render(request, 'home.html')  # Show home.html if logged in
    else:
        return render(request, 'base.html')  # Show base.html if not logged in

# LOGIN / REGISTER / LOGOUT
def login_view(request):
    if request.method == 'POST':
        # Extract username and password from POST data
        username = request.POST.get('username')  # Use get() to prevent errors if not found
        password = request.POST.get('password')

        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to a different page after successful login
            else:
                return render(request, 'login.html', {'error': 'Invalid username or password'})

        return render(request, 'login.html', {'error': 'Both username and password are required'})

    return render(request, 'login.html')    
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

@login_required  # Ensure the user is logged in before they can delete a device
def delete_device(request, device_id):
    # Get the device by ID, but ensure it belongs to the current user
    device = get_object_or_404(Device, id=device_id, user=request.user)
    
    # Delete the device
    device.delete()
    
    # Redirect the user to the device list or a confirmation page
    return redirect('device_list')  # Adjust the redirect URL as needed

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

        elif action == "listen_to_heartbeat":
            # Connect to MQTT broker
            success = listen_to_heartbeat(request)
            return JsonResponse({'rate': listen_to_heartbeat['rate'],
                'timestamp': listen_to_heartbeat['timestamp']}) if success else JsonResponse({'error': 'Failed to connect'}, status=400)
        elif action == "listen_heartbeat":
            # Connect to AWS iot
            success = listen_to_heartbeat(device)
            return JsonResponse({'message': 'Connected to AWS Iot Server'}) if success else JsonResponse({'error': 'Failed to connect'}, status=400)

        elif action == "simulate_heartbeat":
            # Simulate heartbeat rate
            heartbeat_data = simulate_heartbeat(device)
            return JsonResponse({
                'rate': heartbeat_data['rate'],
                'timestamp': heartbeat_data['timestamp']
            })

    # Render the heartbeat rate template
    return render(request, 'heartbeat_rate.html', {'device': device})

