from django.urls import path
from ..myapp.consumer import DeviceConsumer

websocket_urlpatterns = [
    path('ws/devices/', DeviceConsumer.as_asgi()),
]
