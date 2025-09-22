import BAC0
import time
import sys
import os
import subprocess
import json
import redis

sys.path.append('/home/babyiotito/scripts/services')
from RaspResources import resources

# Getting IP address
raspi_resources = resources()
raspi_Eth0 = raspi_resources.get_eth0_ip()
raspi_Serial = raspi_resources.get_serial_nmbr()

STATIC_JSON = '/home/babyiotito/scripts/services/static.json'
CURRENT_JSON = '/home/babyiotito/scripts/services/current.json'

status_map = {
    0: "normal",
    1: "normal",
    2: "fogo",
    3: "falha"
}

def save_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return {}

def get_md5(filepath):
    result = subprocess.run(['md5sum', filepath], stdout=subprocess.PIPE)
    return result.stdout.decode().split()[0]

def discover_objects(bacnet, device_addr, start=15000, end=15500):
    found_objects = []
    print(f"\nSearching for multiStateInput objects from {start} to {end}...")

    for obj_instance in range(start, end + 1):
        try:
            value = bacnet.read(f"{device_addr} multiStateInput {obj_instance} presentValue")
            if value is not None:
                print(f"Found multiStateInput {obj_instance} with presentValue: {value}")
                found_objects.append(obj_instance)
        except Exception:
            print(f"multiStateInput {obj_instance} not found or not accessible.")
    return found_objects

def poll_objects(bacnet, device_addr, objects, interval=1):
    print("\nStarting polling...")

    # Connect to Redis
    r = redis.Redis(
        host='iotito.com.br',
        port=6379,
        password='0591aed20b36a22a3d815107f398905b7c137ec90dfaa657ba7a4ea117c555fe',  
        decode_responses=True
    )

    MAX_FAILURES = 5
    failure_count = 0

    initial_objects = {}
    for obj_instance in objects:
        try:
            present_value = bacnet.read(f"{device_addr} multiStateInput {obj_instance} presentValue")
            object_name = bacnet.read(f"{device_addr} multiStateInput {obj_instance} objectName")
            description = bacnet.read(f"{device_addr} multiStateInput {obj_instance} description")

            initial_objects[str(obj_instance)] = {
                "presentValue": present_value,
                "status": status_map.get(present_value, "desconhecido"),
                "objectName": object_name,
                "description": description
            }
        except Exception as e:
            print(f"Error reading multiStateInput {obj_instance}: {e}")

    initial_state = {
        "raspi_serial": raspi_Serial,
        "objects": initial_objects
    }

    save_json(STATIC_JSON, initial_state)
    print(f"Initial state saved to {STATIC_JSON}")

    previous_md5 = get_md5(STATIC_JSON)

    try:
        while True:
            current_objects = {}
            for obj_instance in objects:
                try:
                    present_value = bacnet.read(f"{device_addr} multiStateInput {obj_instance} presentValue")
                    object_name = initial_objects[str(obj_instance)]["objectName"]
                    description = initial_objects[str(obj_instance)]["description"]

                    current_objects[str(obj_instance)] = {
                        "presentValue": present_value,
                        "status": status_map.get(present_value, "desconhecido"),
                        "objectName": object_name,
                        "description": description
                    }

                    print(f"multiStateInput {obj_instance} presentValue: {present_value}")
                    failure_count = 0  # Reset failure counter on success

                except Exception as e:
                    print(f"Error reading multiStateInput {obj_instance}: {e}")
                    failure_count += 1

                    if failure_count >= MAX_FAILURES:
                        print("\n?? Too many consecutive read failures. Assuming network is lost.")
                        return False  # Signal to restart discovery

            current_state = {
                "raspi_serial": raspi_Serial,
                "objects": current_objects
            }

            save_json(CURRENT_JSON, current_state)

            current_md5 = get_md5(CURRENT_JSON)
            if current_md5 != previous_md5:
                print("\n? Detected change in BACnet object values!")

                # Send to Redis
                redis_key = f"raspi:{raspi_Serial}"
                try:
                    r.set(redis_key, json.dumps(current_state))
                    print(f"? Data sent to Redis key: {redis_key}")
                except Exception as e:
                    print(f"? Failed to send data to Redis: {e}")

                if any(entry["presentValue"] == 2 for entry in current_objects.values()):
                    print("\n?? Fire detected in one of the multiStateInput objects!")

                if all(entry["presentValue"] == 1 for entry in current_objects.values()):
                    print("\n? All multiStateInput objects returned to normal.")

                save_json(STATIC_JSON, current_state)
                previous_md5 = current_md5

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nPolling stopped by user.")
        return True  # Exit cleanly if interrupted


def main():
    bacnet = BAC0.connect(ip=f"{raspi_Eth0}/24", port=47808)
    print("BACnet instance running:", bacnet)

    while True:
        device_addr = None

        # Keep scanning until the target BACnet device is found
        while not device_addr:
            print("Starting BACnet discovery...")
            bacnet.discover()
            time.sleep(5)

            if bacnet.discoveredDevices:
                print(f"Discovered BACnet networks: {bacnet.discoveredNetworks}")
                print("Discovered devices:")
                for addr, instance in bacnet.discoveredDevices.items():
                    print(f" - Device instance {instance} at address {addr}")

                    try:
                        # ✅ Address correction
                        if isinstance(addr, tuple):
                            addr_str = addr[0]  # Take the first element
                        else:
                            addr_str = addr

                        # ✅ Filter ONLY by port 47809
                        if addr_str.endswith(":47809"):
                            device_addr = addr_str
                            print(f"✅ Selected device: {device_addr}")
                            break

                    except Exception as e:
                        print(f"Error processing device address: {e}")
                        continue

                if not device_addr:
                    print("Target device not found. Rescanning in 5 seconds...")

                    no_device_state = {
                        "raspi_serial": raspi_Serial,
                        "status": "no device found",
                        "objects": {}
                    }

                    save_json(STATIC_JSON, no_device_state)
                    save_json(CURRENT_JSON, no_device_state)

                    time.sleep(5)
                    continue

            else:
                print("No BACnet devices found. Rescanning in 5 seconds...")

                no_network_state = {
                    "raspi_serial": raspi_Serial,
                    "status": "no network found",
                    "objects": {}
                }

                save_json(STATIC_JSON, no_network_state)
                save_json(CURRENT_JSON, no_network_state)

                time.sleep(5)
                continue

        # Start object discovery
        found_objects = discover_objects(bacnet, device_addr, start=15000, end=15500)

        if not found_objects:
            print("\nNo multiStateInput objects found in this range. Restarting discovery...")

            no_object_state = {
                "raspi_serial": raspi_Serial,
                "status": "no object found",
                "objects": {}
            }

            save_json(STATIC_JSON, no_object_state)
            save_json(CURRENT_JSON, no_object_state)

            time.sleep(5)
            continue  # Restart discovery

        print(f"\nDiscovered multiStateInput objects: {found_objects}")
        
        # Start polling - if it fails, restart discovery
        success = poll_objects(bacnet, device_addr, found_objects, interval=1)
        if not success:
            print("\n🚨 BACnet network lost. Restarting discovery in 5 seconds...")
            time.sleep(5)


if __name__ == "__main__":
    main()
