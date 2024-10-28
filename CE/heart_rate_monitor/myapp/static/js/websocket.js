// Establish a WebSocket connection
const socket = new WebSocket('ws://localhost:8000/ws/devices/');

// Function to update device status in the User Interface
function updateDeviceStatus(deviceId, state) {
    const deviceElement = document.getElementById(`device-${deviceId}`);
    if (deviceElement) {
        deviceElement.textContent = `Status: ${state}`;
    }
}

// Function to update heartbeat in the User Interface
function updateHeartbeat(deviceId, heartRate) {
    const heartbeatElement = document.getElementById(`heartbeat-${deviceId}`);
    if (heartbeatElement) {
        heartbeatElement.textContent = `Heart Rate: ${heartRate} bpm`;
    }
}

// Connection opened
socket.addEventListener('open', function (event) {
    console.log('WebSocket connection established');
});

// Listen for messages from the server
socket.addEventListener('message', function (event) {
    const data = JSON.parse(event.data);
    console.log('Message from server:', data);
    
    // Update the User Interface based on received data
    if (data.type === 'device_status') {
        updateDeviceStatus(data.deviceId, data.state);
    } else if (data.type === 'heartbeat') {
        updateHeartbeat(data.deviceId, data.heartRate);
    }
});

// Connection closed
socket.addEventListener('close', function (event) {
    console.log('WebSocket connection closed');
});

// Handle errors
socket.addEventListener('error', function (error) {
    console.error('WebSocket error:', error);
});
