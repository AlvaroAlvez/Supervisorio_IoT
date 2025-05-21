from flask import Flask, render_template, request, redirect, url_for, session, flash, abort, jsonify
from flask_login import login_required, logout_user, login_user, current_user, UserMixin, LoginManager
import bcrypt
import subprocess
import re
import os
import time
import RPi.GPIO as GPIO
import sys
sys.path.append('/home/babyiotito/scripts/services')
import LedControl

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    # Aqui vai a lógica de verificação de login...
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/pump_status')
def pump_status():
    try:
        with open('/home/babyiotito/scripts/backend/devices/8940593.json') as f:
            data = json.load(f)
            status = data["acts"].get("Alarm_Inc", 0)
            return jsonify({"status": int(status)})
    except:
        return {"status": 0}


def get_eth0_ip():
    # Read the existing /etc/network/interfaces file
    with open('/etc/network/interfaces', 'r') as interfaces_file:
        lines = interfaces_file.readlines()

    # Initialize variables to store the IP address
    eth0_ip = None

    # Search for the 'address' line in the 'iface eth0 inet static' section
    for line in lines:
        if line.strip() == "iface eth0 inet static":
            for line in lines:
                if re.match(r'\s*address\s+', line):
                    eth0_ip = line.split()[1]
                    break
            break

    return eth0_ip

if __name__ == '__main__':
  eth0_ip = get_eth0_ip()
  if eth0_ip:
      LedControl.LED_Indicator()
      app.run(debug=True, host=eth0_ip, port=8080)
  else:
      print("ERROR") 