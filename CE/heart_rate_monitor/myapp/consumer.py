import json
from channels.generic.websocket import AsyncWebsocketConsumer

class DeviceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.device_id = self.scope['url_route']['kwargs']['device_id']
        self.room_group_name = f"device_{self.device_id}"

        # Join device group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Leave device group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive alert from the server and send it to the WebSocket client
    async def device_alert(self, event):
        alert_message = event['message']

        # Send alert message to WebSocket
        await self.send(text_data=json.dumps({
            'message': alert_message
        }))
