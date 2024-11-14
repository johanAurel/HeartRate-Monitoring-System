# myapp/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/somepath/$', consumers.MyConsumer.as_asgi()),  # Example WebSocket URL
]
