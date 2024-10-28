# Heart Rate Monitoring System

## Overview

The Heart Rate Monitoring System is a Django web application that allows users to monitor heart rate data from various devices. The application provides an interface for managing devices, connecting to MQTT brokers, and visualizing heart rate data. This project also incorporates real-time updates through MQTT.

## Features

- Device Management: Add, update, and monitor devices.
- MQTT Integration: Connect to MQTT brokers for real-time data streaming.
- Heart Rate Monitoring: Visualize and manage heart rate data.
- User Authentication: Secure access with user roles (superusers and regular users).

## Major Files and Functionalities

### 1. **`myapp/models.py`**

This file defines the `Device` model, which represents a heart rate monitoring device. Each device has attributes such as `name`, `status`, and `machine_state`.

### 2. **`myapp/views.py`**

This file contains the view functions for handling requests:

- **`change_device_status(request)`**: Updates the status of a device based on user input.
- **`connect_to_mqtt(request)`**: Connects to the specified MQTT broker and subscribes to relevant topics.
- **`publish_message(request)`**: Publishes messages to a specified topic on the MQTT broker.
- **`heartbeat_rate(request, device_id)`**: Renders the heart rate monitoring page for a specific device.

### 3. **`myapp/templates/heartbeat_rate.html`**

This template displays the heart rate monitoring interface. It allows users to connect to an MQTT broker, view heart rate data, and change device statuses.

### 4. **`myapp/templates/device_list.html`**

This template lists all devices, showing their current statuses. Users can change the status of devices directly from this list.

### 5. **`myapp/urls.py`**

This file defines the URL patterns for the application. It maps URLs to their corresponding view functions.

### 6. **`requirements.txt`**

Lists all the required Python packages for the project, including Django and Paho-MQTT.

## Installation

### Prerequisites

- Python 3.10 or later
- Django 5.1.2
- Paho-MQTT

### Local Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd heart_rate_monitor
