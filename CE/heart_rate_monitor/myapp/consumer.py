import json
from channels.generic.websocket import AsyncWebsocketConsumer

class AccountChangeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Use a group name based on the user's ID or account ID for personalization
        self.user_id = str(self.scope["user"].id)
        self.group_name = f"account_changes_{self.user_id}"

        # Join the user-specific group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group on disconnect
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        # Optionally handle incoming messages if needed
        pass

    async def account_update(self, event):
        # Send the update event data to the WebSocket
        await self.send(text_data=json.dumps({
            "message": event["message"]
        }))
