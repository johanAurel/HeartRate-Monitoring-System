import json
from channels.generic.websocket import WebsocketConsumer
from .models import Device


class DeviceConsumer(WebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        device_id = data.get('deviceId')
        heartbeat_rate = data.get('heartbeat')
        device = Device.objects.get(id=device_id)
        device.heartbeat_rate = heartbeat_rate
        device.save()
        
        # Example response:
         # Send a response back to the frontend
        self.send(text_data=json.dumps({
            'type': 'device_status',
            'deviceId': device_id,
            'heartbeat_rate': heartbeat_rate,
            'status': 'updated',
            'state':'ON'
        }))
