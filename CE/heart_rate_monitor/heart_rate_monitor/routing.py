from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/account_changes/', consumers.AccountChangeConsumer.as_asgi()),
]
