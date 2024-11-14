# Heartbeat Rate Monitor with AWS IoT Integration

## Overview

This project provides a real-time heartbeat monitoring system using a web interface. It simulates and displays the heartbeat rate of a device and provides real-time alerts if the heartbeat rate is too high or too low. The system also connects to AWS IoT Core, enabling IoT communication between the device and AWS.

### Features:
- Simulate heartbeat data for a device.
- Show real-time heartbeat rate and alert messages.
- Connect and disconnect from AWS IoT Core for device communication.
- Toggle device status (ON/OFF).
- Display recent heartbeats and alerts.
- Receive and display real-time heartbeat data from a WebSocket.

## Prerequisites

Before setting up the project, ensure you have the following prerequisites:

- **Python** 3.x
- **Django** framework
- **PostgreSQL** for database storage
- **AWS IoT Core** for device communication
- **Node.js** and **npm** for front-end dependencies (if needed)

## Project Setup

### Clone the Repository

First, clone this repository to your local machine.

```bash
git clone https://github.com/yourusername/heartbeat-monitor.git
cd heartbeat-monitor
```
Install Required Python Packages
Install the required dependencies by running:

```bash
pip install -r requirements.txt
```
### Configure Database
Set up PostgreSQL for storing device data and alerts:

Create a PostgreSQL Database:

Create a database, e.g., heartbeat_monitor.
Set up the necessary tables, like device, heartbeat, and alert.
Configure Django Database Settings: Edit the DATABASES configuration in settings.py to match your PostgreSQL setup.

```python
Copy code
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'heartbeat_monitor',  # Your database name
        'USER': 'monitor',  # Your PostgreSQL username
        'PASSWORD': 'monitoring',  # Your PostgreSQL password
        'HOST': 'localhost',  # Your database host
        'PORT': '5432',  # Default PostgreSQL port
    }
}
```
### AWS IoT Configuration
Make sure you have AWS IoT Core set up and the following:

Create a Thing in AWS IoT Core.
Get the IoT endpoint to use for the connection.
Configure policies and permissions for your device.
You might want to create all required AWS resources found in the terraform file before(I also wrote an optional Lambda function to connect the IoT thing)
to provision the various terraform resources
```hcl
terraform init
terraform plan
```
```hcl
terraform apply
```
 ### Set Up WebSocket (if using real-time heartbeat data)
This project uses WebSocket for real-time communication. Make sure to install the necessary packages to handle WebSocket connections.

```bash
pip install channels
```
Add WebSocket routing in your urls.py:

```python
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/device/<device_id>/', consumers.DeviceConsumer.as_asgi()),
]
```
### Run Migrations
Apply the database migrations to create the necessary tables:

```bash
Copy code
python manage.py migrate
```
### Run the Development Server
Run the Django development server:

```bash
Copy code
python manage.py runserver
```
### Front-End Setup
If your project includes front-end JavaScript dependencies (such as WebSocket or jQuery), ensure to install them as needed.

```bash
npm install
```

### Test the Application
Once everything is set up:

Go to http://127.0.0.1:8000/ in your browser.
You should see the heartbeat monitor page.
You can simulate heartbeat data, toggle the device status, and connect/disconnect from AWS IoT.
Usage
Toggle Device Status
When the device status is ON, you can simulate heartbeat data.
When the device status is OFF, you cannot simulate heartbeat data.
Simulate Heartbeat
Click Simulate Heartbeat to start generating heartbeat data every second.
The Stop button will stop the simulation.
AWS IoT Connection
Enter the AWS IoT endpoint and click Connect to connect to AWS IoT.
Once connected, the button will change to Disconnect, and you will be able to interact with the device on AWS.
Troubleshooting
If the Connect button doesn't work, ensure your AWS IoT endpoint is correct and accessible.
If real-time heartbeat updates aren't showing, check WebSocket connection in your browser console.
you can also enter the connect file in /CE directory and run the following for a sample Iot core sample/pubsub.py file you can use to see what your thing JSON body will look like
```bash
chmod +x start.sh
```
```bash
./start.sh
```
### Build a Docker image with your docker file
run the following commands:
```bash
docker build -t heartbeat_monitor:1.0.0 .
```
then on your chosen port run the app
```bash
docker run -p 8080:8080 heartbeat_monitor:1.0.0
```
The backend ensures you can create a user to which you manually add device you either set as simulations or connect to your internet of thing and create the different Heartbeats and Alerts, ideally you would want to create an RDS with the terraform code and either use a lambda function(purely backend) or connect it via Endpoint.

When alert is triggered the app does not only create ab Alert model but also is meant to ideally send the error message to Ios event to create an alarm model and send you the alert via the email of your user.
