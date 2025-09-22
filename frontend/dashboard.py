from flask import Flask, render_template, request, redirect, url_for, session, flash, abort, jsonify
from flask_login import login_required, logout_user, login_user, current_user, UserMixin, LoginManager
import datetime
import bcrypt
import json
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
    return redirect(url_for('dashboard2'))

@app.route('/dashboard2')
def dashboard():
    return render_template('dashboard2.html')

@app.route('/pump_status')
def pump_status():
    try:
        with open('/home/babyiotito/scripts/backend/devices/8940593.json') as f:
            data = json.load(f)
            status = data["acts"].get("Alarm_Inc", 0)
            return jsonify({"status": int(status)})
    except:
        return {"status": 0}

@app.route('/bomba_action', methods=['POST'])
def bomba_action():
    data = request.get_json()
    serial = data.get('serial')
    action = data.get('action')
    value = data.get('value')

    # Dados com timestamp
    record = {
        "serial": serial,
        "action": action,
        "value": value,
        "timestamp": datetime.now().isoformat()
    }

    # Caminho do arquivo onde os dados serão salvos
    log_path = os.path.join("frontend", f"bomba_log_{serial}.json")

    # Criar diretório logs se não existir
    os.makedirs("frontend", exist_ok=True)

    # Salvar ou adicionar ao arquivo JSON
    if os.path.exists(log_path):
        with open(log_path, "r+") as file:
            try:
                content = json.load(file)
            except json.JSONDecodeError:
                content = []
            content.append(record)
            file.seek(0)
            json.dump(content, file, indent=4)
    else:
        with open(log_path, "w") as file:
            json.dump([record], file, indent=4)

    print(f"LOG salvo: {record}")
    return jsonify({"status": "ok", "message": "Comando registrado com sucesso"})

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