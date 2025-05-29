import paho.mqtt.client as Mqtt
import sys
sys.path.append('/home/babyiotito/scripts/services')
from RaspResources import resources
#import threading #cria threads, que são fluxos separados de controle dentro do código, permitindo uma correta execução do programa 
import time
sys.path.append('/home/babyiotito/scripts/backend')
import json
import threading  


payload = None
last_payload = None
Mqtt_message_received = False
frontend_last_state = {}


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


def monitor_frontend_changes(client, device_id):
    global frontend_last_state
    frontend_path = f"/home/babyiotito/scripts/frontend/{device_id}.json"

    while True:
        try:
            with open(frontend_path, "r") as f:
                frontend_data = json.load(f)
        except FileNotFoundError:
            frontend_data = {"id": device_id, "acts": {}}

        for act, val in frontend_data["acts"].items():
            last_val = frontend_last_state.get(act)

            if str(last_val) != str(val):
                # Publish the command
                publish_topic = f"store/kit/mqtt/{device_id}"
                payload = json.dumps({
                    "id": device_id,
                    "act": act,
                    "val": val
                })

                publish_message(client, publish_topic, payload)
                print(f"[Frontend Monitor] Published change: {act} = {val}")
                frontend_last_state[act] = val

        time.sleep(0.5)  # Poll interval


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

    monitor_thread = threading.Thread(
    target=monitor_frontend_changes, args=(client, raspi_serial_nmbr), daemon=True
    )
    monitor_thread.start()
#testando
    try:
        while True:
            time.sleep(0.5)  # main loop keeps script alive
    except KeyboardInterrupt:
        print("MQTT client stopped by user")
        client.loop_stop()
        client.disconnect()