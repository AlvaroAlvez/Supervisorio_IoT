import BAC0
import time
import sys
import os
import subprocess
import json

sys.path.append('/home/babyiotito/scripts/services')
from RaspResources import resources

# Getting IP address
raspi_resources = resources()
raspi_Eth0 = raspi_resources.get_eth0_ip()

STATIC_JSON = '/home/babyiotito/scripts/services/static.json'
CURRENT_JSON = '/home/babyiotito/scripts/services/current.json'

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

def discover_objects(bacnet, device_addr, start=00000, end=70000):
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

    # Save initial state
    initial_state = {}
    for obj_instance in objects:
        try:
            value = bacnet.read(f"{device_addr} multiStateInput {obj_instance} presentValue")
            initial_state[str(obj_instance)] = value
        except Exception as e:
            print(f"Error reading multiStateInput {obj_instance}: {e}")

    save_json(STATIC_JSON, initial_state)
    print(f"Initial state saved to {STATIC_JSON}")

    previous_md5 = get_md5(STATIC_JSON)

    try:
        while True:
            current_state = {}
            for obj_instance in objects:
                try:
                    value = bacnet.read(f"{device_addr} multiStateInput {obj_instance} presentValue")
                    current_state[str(obj_instance)] = value
                    print(f"multiStateInput {obj_instance} presentValue: {value}")
                except Exception as e:
                    print(f"Error reading multiStateInput {obj_instance}: {e}")

            save_json(CURRENT_JSON, current_state)

            # Compare MD5 hashes
            current_md5 = get_md5(CURRENT_JSON)
            if current_md5 != previous_md5:
                print("\n⚡ Detected change in BACnet object values!")

                # 🔥 Check if any variable changed to 2
                if 2 in current_state.values():
                    print("\n🔥 Fire detected in one of the multiStateInput objects!")

                # ✅ Check if all variables returned to 1
                if all(value == 1 for value in current_state.values()):
                    print("\n✅ All multiStateInput objects returned to normal.")

                # 🔗 Send webhook here (you can use curl or requests)
                # Example (Linux shell): os.system('curl -X POST -H "Content-Type: application/json" -d @/home/babyiotito/scripts/services/current.json http://your_webhook_url')

                # Update static.json to the new state to track next changes
                save_json(STATIC_JSON, current_state)
                previous_md5 = current_md5

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nPolling stopped by user.")


def main():
    bacnet = BAC0.connect(ip=f"{raspi_Eth0}/24", port=47808)
    print("BACnet instance running:", bacnet)

    print("Starting BACnet discovery...")
    bacnet.discover()
    time.sleep(5)

    print(f"Discovered BACnet networks: {bacnet.discoveredNetworks}")
    print("Discovered devices:")
    for addr, instance in bacnet.discoveredDevices.items():
        print(f" - Device instance {instance} at address {addr}")

    device_addr = '1095:192.168.20.10:47809'
    found_objects = discover_objects(bacnet, device_addr, start=00000, end=70000)

    if not found_objects:
        print("\nNo multiStateInput objects found in this range.")
    else:
        print(f"\nDiscovered multiStateInput objects: {found_objects}")
        poll_objects(bacnet, device_addr, found_objects, interval=1)

if __name__ == "__main__":
    main()
