import paho.mqtt.client as Mqtt
import sys
sys.path.append('/home/babyiotito/scripts/services')
from RaspResources import resources
#import threading #cria threads, que são fluxos separados de controle dentro do código, permitindo uma correta execução do programa 
import time
sys.path.append('/home/babyiotito/scripts/backend')
import json

payload = None
last_payload = None
Mqtt_message_received = False

def on_message(client, userdata, msg):
    global payload

    payload = msg.payload.decode()
    print(f"Received message on topic '{msg.topic}': {payload}")

    try:
        data = json.loads(payload)
        device_id = data.get("id")
        act = data.get("act")
        val = data.get("val")

        if not device_id or not act:
            print("Missing 'id' or 'act' in the message")
            return

        # Path to file per device
        file_path = f"/home/babyiotito/scripts/backend/devices/{device_id}.json"

        # Load existing data if available
        try:
            with open(file_path, "r") as f:
                device_data = json.load(f)
        except FileNotFoundError:
            device_data = {"id": device_id, "acts": {}}

        # Update the specific "act" with new value
        device_data["acts"][act] = val

        # Save back the updated JSON
        with open(file_path, "w") as f:
            json.dump(device_data, f, indent=2)

        print(f"Updated device {device_id} - act '{act}': {val}")

    except json.JSONDecodeError:
        print("Invalid JSON received")

def on_publish(client, userdata, result):
    print("Data published successfully")

def publish_message(client, topic, message):
    client.publish(topic, message)

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(topic)
    print(f"Subscribed to topic inside on_connect: {topic}")

if __name__ == "__main__":

    # MQTT broker info
    broker = "mqtt.sobeai.com.br"
    port = 1883
    topic = "store/kit/mqtt"

    # Get Raspberry Pi serial number (used as topic)
    raspi_instance = resources()
    raspi_serial_nmbr = raspi_instance.get_serial_nmbr()
    print(f"Using MQTT topic:{topic}")

    # Create MQTT client and connect
    client = Mqtt.Client("raspi_server")
    client.connect(broker, port)

    # Attach callbacks
    client.on_message = on_message
    client.on_publish = on_publish
    client.on_connect = on_connect

    # Subscribe to the topic
    client.subscribe(topic, qos=0)
    print(f"Subscribed to topic: {topic}")

    # Publish initial message
    client.publish(raspi_serial_nmbr, "raspi connected")
    print("Published connection message")

    # Start MQTT client network loop
    client.loop_start()

    try:
        while True:
            time.sleep(0.5)  # main loop keeps script alive
    except KeyboardInterrupt:
        print("MQTT client stopped by user")
        client.loop_stop()
        client.disconnect()
