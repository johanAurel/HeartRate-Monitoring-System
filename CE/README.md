
__heart_rate_monitor/asgi.py__ Ensure that Django Channels is set up to handle WebSocket connections.

__myapp/models.py__ includes User, Device, and Heartbeat models. The Heartbeat model sends an MQTT message when the heart rate exceeds a certain threshold.

__myapp/routing.py__ WebSocket routing for Django Channels.

__myapp/management/commands/mqtt_listener.py__ Management command to listen for MQTT messages and update device states and heartbeats.

```bash 
python manage.py mqtt_listener
```

__myapp/views.py__
A view to list devices and their real-time statuses for the logged-in user.

__myapp/templates/device_list.html__
A template to show the real-time device status and heartbeats.

__myapp/static/js/websocket.js__
The JavaScript for handling WebSocket communication to update the front-end in real-time.
