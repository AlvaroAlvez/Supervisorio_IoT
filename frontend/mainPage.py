from flask import Flask, render_template, request, redirect, url_for, session, flash, abort, jsonify
from flask_login import login_required, logout_user, login_user, current_user, UserMixin, LoginManager
import bcrypt
import subprocess
import re
import os
import datetime
import RPi.GPIO as GPIO
import sys
sys.path.append('/home/babyiotito/scripts/services')
import LedControl
from functools import wraps
from flask import make_response
import json
from RaspResources import resources
#GPIO.setmode(GPIO.BCM)
#GPIO.setup(23, GPIO.OUT)
     
app = Flask(__name__, template_folder='/home/babyiotito/scripts/frontend' )

chave_Flask_random = os.urandom(24)
chave_Flask_random_hex = chave_Flask_random.hex()

app.secret_key = chave_Flask_random_hex

login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_id, username, password):
        self.id = user_id
        self.username = username
        self.password = password

def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return no_cache

def disconnect_wifi(connection_name):
    disconnect_cmd = f"sudo nmcli connection down '{connection_name}'"
    subprocess.run(disconnect_cmd, shell=True)

def connection_wifi(WiFi_SSID, WiFi_password):
    check_cmd = f"sudo nmcli device wifi connect '{WiFi_SSID}' password '{WiFi_password}'"
    return subprocess.run(check_cmd, shell=True).returncode == 0


def is_wifi_connected():
    try:
        result = subprocess.run(['nmcli', 'connection', 'show', '--active'], capture_output=True, text=True, check=True)
        return 'wifi' in result.stdout.lower()
        print(result.stdout.lower)
    except subprocess.CalledProcessError:
        return False


def get_available_wifi_networks():
    cmd = "nmcli device wifi list"
    result = subprocess.check_output(cmd, shell=True, text=True)
    wifi_list = result.splitlines()
    #print (wifi_list)

    ssids = [re.search(r'\s+(.+?)\s+Infra', line).group(1) for line in wifi_list[1:]]
    #print(ssids)
    return ssids


def check_credentials(user_id):
    
    file_path = '/home/babyiotito/scripts/frontend/credentials.txt'
   
    try: 
        with open (file_path, 'r') as file:
            lines = file.readlines()

        if len(lines) >= 2:
           stored_username = lines[0].strip().split('=')[1]
           stored_password = lines[1].strip().split('=')[1]
           
           return User(user_id=1, username=stored_username, password=stored_password)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    return None

def get_timezone():
    cmd_time = "timedatectl list-timezones"
    timezone = subprocess.check_output(cmd_time, shell=True, text=True)
    timezone_list=timezone.splitlines()
    return timezone_list

def set_timezone(timezone_selected):
    set_timezone_cmd = f"sudo timedatectl set-timezone {timezone_selected}"
    return subprocess.run(set_timezone_cmd, shell = True)


@login_manager.user_loader
def load_user(user_id):
      return check_credentials(user_id)


@app.route('/configuration')
@login_required
@nocache
def config_form():
     wifi_networks = get_available_wifi_networks()
     wifi_connected = is_wifi_connected()
     timezone_html_list = get_timezone()
     login_session = login()
     return render_template('mainPage.html', wifi_networks=wifi_networks, wifi_connected=wifi_connected, login_session=login_session, timezone_html_list=timezone_html_list)

@app.route('/status')
@login_required
def status():
    return render_template('status.html')  # Or whatever logic you want

@app.route('/')
@login_required
@nocache
def dashboard():
    login_session = login()
    return render_template('dashboard.html', login_session=login_session)


@app.route('/disconnect-wifi', methods=['POST'])
def disconnect_wifi_route():
      if is_wifi_connected():
        connection_name = subprocess.run("nmcli -t -f NAME,DEVICE,TYPE con show --active | awk -F: '$3==\"802-11-wireless\" {print $1}'", shell=True, text=True, capture_output=True).stdout.strip()
        disconnect_wifi(connection_name)
      return redirect(url_for('config_form'))


@app.route('/configure', methods=['POST'])
def configure():
   # session['logged_in']=True
    username = request.form['username']
    raw_password = request.form['password']
    WiFi_SSID_raw = request.form['ssid']
    WiFi_password = request.form['wifi_password']
    eth0_ip = request.form['eth0_ip']
    eth0_net = request.form['eth0_netmask']
    eth0_gtw = request.form['eth0_gateway']    
    connection_name = subprocess.run("nmcli -t -f NAME,DEVICE,TYPE con show --active | awk -F: '$3==\"802-11-wireless\" {print $1}'", shell=True, text=True, capture_output=True).stdout.strip()
    timezone_selected = request.form['timezone']
    print('connection_name')
    print(timezone_selected)

    with open('/etc/network/interfaces', 'r') as interfaces_file:
        lines = interfaces_file.readlines()

    hashed_password = hash_password(raw_password)

    with open('/home/babyiotito/scripts/frontend/credentials.txt', 'w') as file:
        file.write(f'username={username}\npassword={hashed_password}\n{raw_password}')

    WiFi_SSID_parts = WiFi_SSID_raw.split(None, 1)
    WiFi_SSID = WiFi_SSID_parts[1]

    print(WiFi_SSID)

    print(timezone_selected)

    set_timezone(timezone_selected)

    disconnect_wifi(connection_name)

    connection_wifi(WiFi_SSID, WiFi_password)


    for i in range(len(lines)):
       if lines[i].startswith("iface eth0 inet static"):
           lines[i + 1] = f"address {eth0_ip}\n"
           lines[i + 2] = f"netmask {eth0_net}\n"
           lines[i + 3] = f"gateway {eth0_gtw}\n"


    with open('/etc/network/interfaces', 'w') as interfaces_file:
       interfaces_file.writelines(lines)

    subprocess.run(['sudo', 'reboot']) 
    
    return "restarting device"


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        entered_username = request.form['username']
        entered_password = request.form['password']

        user = check_credentials(user_id=1)

        if user and entered_username == user.username and bcrypt.checkpw(entered_password.encode(), user.password.encode()):
           print (user.username)
           print (bcrypt.checkpw(entered_password.encode(), user.password.encode()))
           print ('login sucess')
           session['Logged_in'] = True
           flash('Login Successful!', 'success')
           login_user(user)
           return redirect(url_for('dashboard'))
          # return redirect(url_for('config_form'))
          
        else:
           print (user.username)
           print (user.password.encode())
           print (bcrypt.checkpw(entered_password.encode(), user.password.encode())) 
           flash ('invalid username or password','error')
           print('sucks motherfucker')

    return render_template('loginPage.html')

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    return redirect(url_for('login'), code=302)

@app.route('/connecteduser')
@login_required
def some_route():
     print(current_user)
     return "Check your code"

@app.route('/pump_status')
@login_required
def pump_status():
    try:
        with open('/home/babyiotito/scripts/backend/devices/8940601.json') as f:
            data = json.load(f)
            status = data["acts"].get("Alarm_Inc", "0")
            return jsonify({"status": int(status)})
    except Exception as e:
        print(f"Erro ao ler status da bomba: {e}")
        return jsonify({"status": 0})

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode('utf-8')

@app.route('/bomba_action', methods=['POST'])
def bomba_action():
    data = request.get_json()
    action = data.get('action')  # será o "act"
    value = data.get('value')    # será o "val"

    raspi_instance = resources()
    serial = raspi_instance.get_serial_nmbr()

    if not serial or not action:
        return jsonify({"status": "error", "message": "Dados incompletos"}), 400

    # Caminho para o arquivo JSON na pasta frontend
    file_path = f"/home/babyiotito/scripts/frontend/{serial}.json"

    try:
        # Carregar dados existentes, se houver
        try:
            with open(file_path, "r") as f:
                device_data = json.load(f)
        except FileNotFoundError:
            device_data = {"id": serial, "acts": {}}

        # Atualizar valor da ação
        device_data["acts"][action] = value

        # Salvar o arquivo JSON atualizado
        with open(file_path, "w") as f:
            json.dump(device_data, f, indent=2)

        print(f"Atualizado: {serial} - {action}: {value}")
        return jsonify({"status": "ok", "message": "Comando registrado com sucesso"})

    except Exception as e:
        print(f"Erro ao atualizar JSON: {e}")
        return jsonify({"status": "error", "message": "Falha ao atualizar JSON"}), 500


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
      app.run(debug=True, host='0.0.0.0', port=8080)
  else:
      print("ERROR")