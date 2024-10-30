from django.urls import path
from myapp.views import *

urlpatterns = [
    path('', conditional_home, name='conditional_home'),
    path('home/', conditional_home, name='home'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('users/', user_list, name='user_list'),  # URL for viewing all users
    path('users/<int:user_id>' , user_list, name='user_list'), # URL for viewing
    path('users/<int:user_id>/devices/', device_list, name='user_devices'),  # URL for viewing a specific user's devices
    path('devices/', device_list, name='device_list'),#URL for viewing list of devices
    path('devices/user/<str:username>/', user_devices, name='user_devices'),
    path('devices/add/', add_device, name='add_device'),  
    path('password_change/', password_management_disabled, name='password_change'),
    path('password_reset/', password_management_disabled, name='password_reset'),    
    path('devices/<int:device_id>/heartbeat/', heartbeat_rate, name='heartbeat'),
    path('logout', logout_view, name='logout'),
    path('devices/change-status/', change_device_status, name='change_device_status'), 
    path('connect-to-mqtt/', connect_to_mqtt, name='connect_to_mqtt'),
    path('simulate-heartbeat/', simulate_heartbeat, name='simulate_heartbeat')
]   
