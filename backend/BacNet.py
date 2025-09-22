#!/usr/bin/env python3
import BAC0
import time
import json
import os
import redis
import sys
import threading
from flask import Flask, jsonify

# Import RaspResources to get dynamic IP and serial
sys.path.append('/home/babyiotito/scripts/services')
from RaspResources import resources

# ---------------- CONFIG ----------------
LOCAL_PORT = 47808
DISCOVER_WAIT = 2
POLL_INTERVAL = 10

STATIC_JSON = "/home/babyiotito/scripts/services/static_NET.json"
CURRENT_JSON = "/home/babyiotito/scripts/services/current_NET.json"

REDIS_HOST = "iotito.com.br"
REDIS_PORT = 6379
REDIS_PASS = "0591aed20b36a22a3d815107f398905b7c137ec90dfaa657ba7a4ea117c555fe"
REDIS_KEY = "raspi:discovery_alert"

# Flask app
app = Flask(__name__)

# Globals
bacnet = None
raspi_Serial = None
r = None
static_devices = []
last_status_map = {}
rescan_requested = False  # flag to trigger rescan


# ---------------- HELPERS ----------------
def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=4, sort_keys=True)


def load_json(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}


def discover_devices(bacnet):
    """Send Who-Is and return a list of dicts: {'ip':..., 'instance':..., 'status':'online'}"""
    devices_raw = bacnet.discover()
    time.sleep(DISCOVER_WAIT)
    devices_list = []
    if devices_raw:
        for ip, instance in devices_raw:
            devices_list.append({
                "ip": ip,
                "instance": instance,
                "status": "online"
            })
    return devices_list


def notify_redis(r, raspi_serial, changed_devices):
    payload = {
        "raspi_serial": raspi_serial,
        "changed_devices": changed_devices,
        "timestamp": int(time.time())
    }
    try:
        r.set(REDIS_KEY, json.dumps(payload))
        print(f"[Redis] Sent device status change: {payload}")
    except Exception as e:
        print(f"[Redis] Failed to send notification: {e}")


# ---------------- POLLING LOOP ----------------
def polling_loop():
    global static_devices, last_status_map, rescan_requested

    while True:
        print("\n=== Running discovery round ===")
        current_devices = discover_devices(bacnet)

        # If a rescan was requested, reset static_devices
        if rescan_requested:
            static_devices = current_devices
            save_json(STATIC_JSON, {
                "raspi_serial": raspi_Serial,
                "devices": static_devices,
                "created_at": int(time.time())
            })
            last_status_map = {f"{d['ip']}_{d['instance']}": d["status"] for d in static_devices}
            rescan_requested = False
            print("⚡ Rescan completed and static.json updated.")

        # Build map of currently online devices
        online_map = {f"{d['ip']}_{d['instance']}": "online" for d in current_devices}

        # Detect status changes
        changed_devices = []
        for dev in static_devices:
            key = f"{dev['ip']}_{dev['instance']}"
            new_status = "online" if key in online_map else "offline"

            if last_status_map.get(key, "unknown") != new_status:
                dev["status"] = new_status
                changed_devices.append(dev)

            last_status_map[key] = new_status

        # Save current snapshot
        current_payload = {
            "raspi_serial": raspi_Serial,
            "devices": static_devices,
            "checked_at": int(time.time())
        }
        save_json(CURRENT_JSON, current_payload)
        print(f"Discovered devices: {current_devices}")

        if changed_devices:
            print(f"⚡ Status changed: {changed_devices}")
            notify_redis(r, raspi_Serial, changed_devices)
        else:
            print("No status changes detected.")

        time.sleep(POLL_INTERVAL)


# ---------------- FLASK ROUTES ----------------
@app.route("/rescan", methods=["POST"])
def rescan():
    global rescan_requested
    rescan_requested = True
    return jsonify({"status": "ok", "message": "Rescan requested"})


@app.route("/get_ips", methods=["GET"])
def get_ips():
    """Retorna IPs e status do current_NET.json e static_NET.json"""
    current_data = load_json(CURRENT_JSON)
    static_data = load_json(STATIC_JSON)

    current_ip, current_status = "192.168.20.145", "offline"
    static_ip, static_status = "192.168.20.145", "offline"

    if "devices" in current_data and current_data["devices"]:
        dev = current_data["devices"][0]
        current_ip = dev.get("ip", "192.168.20.145")
        current_status = dev.get("status", "offline")

    if "devices" in static_data and static_data["devices"]:
        dev = static_data["devices"][0]
        static_ip = dev.get("ip", "192.168.20.145")
        static_status = dev.get("status", "offline")

    return jsonify({
        "current_ip": current_ip,
        "current_status": current_status,
        "static_ip": static_ip,
        "static_status": static_status
    })


# ---------------- MAIN ----------------
def main():
    global bacnet, raspi_Serial, r, static_devices, last_status_map

    raspi_resources = resources()
    raspi_Eth0 = raspi_resources.get_eth0_ip()
    raspi_Serial = raspi_resources.get_serial_nmbr()

    bacnet = BAC0.lite(ip=f"{raspi_Eth0}/24", port=LOCAL_PORT)
    print(f"BACnet instance running: {bacnet}")

    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASS, decode_responses=True)

    # Initial discovery for static.json
    print("Updating static.json with current BACnet devices...")
    devices = discover_devices(bacnet)
    static_devices = devices
    save_json(STATIC_JSON, {
        "raspi_serial": raspi_Serial,
        "devices": static_devices,
        "created_at": int(time.time())
    })
    last_status_map = {f"{d['ip']}_{d['instance']}": d["status"] for d in static_devices}
    print(f"Static JSON updated with {len(static_devices)} device(s).")

    # Start polling loop in background
    t = threading.Thread(target=polling_loop, daemon=True)
    t.start()

    # Start Flask server
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
