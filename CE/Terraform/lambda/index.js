const AWS = require('aws-sdk');
const { Client } = require('pg'); // PostgreSQL client

// PostgreSQL configuration
const dbConfig = {
    host: 'my-django-rds.cha88mkoiia7.eu-west-2.rds.amazonaws.com',  // Replace with your RDS endpoint
    port: 5432,
    user: 'monitor',  // Replace with your DB username
    password: 'monitoring',  // Replace with your DB password
    database: 'heartbeat_monitor'  // Replace with your DB name
};

// AWS IoT Data and IoT Events configuration
const iotData = new AWS.IotData({
    endpoint: 'd08281963m7bz3u3le733-ats.iot.eu-west-2.amazonaws.com'  // Replace with your IoT Core endpoint
});

const iotEvents = new AWS.IoTEventsData({
    endpoint: 'data.iotevents.eu-west-2.amazonaws.com'  // Replace with your AWS IoT Events endpoint
});

exports.handler = async (event) => {
    console.log("Received event:", JSON.stringify(event, null, 2));

    // Parse the incoming message from the IoT event
    let parsedBody;
    try {
        parsedBody = typeof event.payload === "string" ? JSON.parse(event.payload) : event.payload;
    } catch (error) {
        console.error("Error parsing message payload:", error);
        return {
            statusCode: 400,
            body: JSON.stringify({ error: 'Invalid JSON format in payload' })
        };
    }

    const { device_id, heartbeat_rate, last_heartbeat } = parsedBody;

    if (!device_id || !heartbeat_rate || !last_heartbeat) {
        return {
            statusCode: 400,
            body: JSON.stringify({ error: 'Missing required fields' })
        };
    }

    // Initialize PostgreSQL client
    const client = new Client(dbConfig);

    try {
        // Connect to PostgreSQL RDS instance
        await client.connect();

        // Insert the heartbeat data into the RDS database
        await client.query(
 //           'INSERT INTO heartbeat (device_id, heartbeat_rate, last_heartbeat) VALUES ($1, $2, $3)',
            [device_id, heartbeat_rate, last_heartbeat]
        );

        // Check for alert conditions (e.g., heartbeat rate exceeds threshold)
        let alertMessage = null;
        if (heartbeat_rate > 100) {
            alertMessage = `High heartbeat rate detected: ${heartbeat_rate} BPM`;
        } else if (heartbeat_rate < 50) {
            alertMessage = `Low heartbeat rate detected: ${heartbeat_rate} BPM`;
        }

        // If an alert condition is met, insert it into the alerts table and publish to IoT
        if (alertMessage) {
            // Insert alert into RDS
            await client.query(
                'INSERT INTO alert (device_id, alert_message) VALUES ($1, $2)',
                [device_id, alertMessage]
            );

            // Publish the alert to the IoT MQTT topic
            const topic = `devices/${device_id}/alerts`;
            const payload = JSON.stringify({ alert: alertMessage, timestamp: new Date().toISOString() });

            await iotData.publish({
                topic,
                qos: 1,
                payload
            }).promise();

            console.log(`Published alert to IoT topic ${topic}: ${alertMessage}`);
        }

        // Update AWS IoT Events detector with the new heartbeat data
        try {
            await iotEvents.batchPutMessage({
                messages: [
                    {
                        messageId: `${device_id}-${Date.now()}`,
                        inputName: "HeartbeatInput", // This should match your IoT Events input name
                        payload: JSON.stringify({
                            device_id: device_id,
                            heartbeat_rate: heartbeat_rate,
                            last_heartbeat: last_heartbeat
                        })
                    }
                ]
            }).promise();

            console.log(`Updated IoT Events for device ${device_id} with heartbeat data.`);
        } catch (iotEventsError) {
            console.error('Error updating IoT Events:', iotEventsError);
        }

        return {
            statusCode: 200,
            body: JSON.stringify({ message: 'Heartbeat data processed successfully' })
        };

    } catch (error) {
        console.error('Error:', error);
        return {
            statusCode: 500,
            body: JSON.stringify({ error: 'Internal server error' })
        };
    } finally {
        await client.end();
    }
};

