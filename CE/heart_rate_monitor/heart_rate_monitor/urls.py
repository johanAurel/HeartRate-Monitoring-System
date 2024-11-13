from django.urls import path
from myapp.views import *
from myapp.utils import *

urlpatterns = [
    path('', conditional_home, name='conditional_home'),
    path('home/', conditional_home, name='home'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('users/', user_list, name='user_list'),  
    path('users/<int:user_id>' , user_list, name='user_list'), 
    path('users/<int:user_id>/devices/', device_list, name='user_devices'),  
    path('devices/', device_list, name='device_list'),
    path('devices/add/', add_device, name='add_device'),
    path('device/<int:device_id>/delete/', delete_device, name='delete_device'),  
    path('password_change/', password_management_disabled, name='password_change'),
    path('password_reset/', password_management_disabled, name='password_reset'),    
    path('devices/heartbeat/', heartbeat_rate, name='heartbeat'),
    path('logout', logout_view, name='logout'),
    path('devices/change-status/', change_device_status, name='change_device_status'), 
    path('listen_to_heartbeat/', listen_to_heartbeat, name='listen_to_heartbeat'),
    path('simulate-heartbeat/', simulate_heartbeat, name='simulate_heartbeat'),
    path('toggle-status/', toggle_device_status, name='toggle_device_status'),
]   
