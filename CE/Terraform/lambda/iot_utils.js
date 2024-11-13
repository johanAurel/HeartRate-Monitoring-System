const AWS = require('aws-sdk');
const iotData = new AWS.IotData({ endpoint: 'YOUR_IOT_ENDPOINT' });

/**
 * Publish an alert message to the AWS IoT topic for the device.
 * @param {string} deviceId - The device ID.
 * @param {string} alertMessage - The alert message.
 */
async function publishAlertToIoT(deviceId, alertMessage) {
    const params = {
        topic: `devices/${deviceId}/alerts`,
        payload: JSON.stringify({ alert: alertMessage }),
        qos: 1
    };

    return iotData.publish(params).promise();
}

module.exports = { publishAlertToIoT };

