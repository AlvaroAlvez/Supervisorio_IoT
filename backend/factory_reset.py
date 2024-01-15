import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import time 
from datetime import datetime
import sys
sys.path.append('/home/babyiotito/scripts/services')
import LedControl 
import subprocess
import bcrypt

GPIO.setmode(GPIO.BCM) # Use physical pin numbering
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 26 to be an input pin and set initial value to be pulled low (off)
#GPIO.setup(23, GPIO.OUT)

prev_button_state = GPIO.LOW

password = 'admin'

def reset_eth0():
     with open('/etc/network/interfaces', 'r') as interfaces_file_read:
        lines = interfaces_file_read.readlines()
    
     for i in range(len(lines)):
       if lines[i].startswith("iface eth0 inet static"):
           lines[i + 1] = "address 192.168.1.71\n"
           lines[i + 2] = "netmask 255.255.255.0\n"
           lines[i + 3] = "gateway 192.168.1.1\n"
     
     with open('/etc/network/interfaces', 'w') as interfaces_file:
       interfaces_file.writelines(lines)

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode('utf-8')

def reset_credentials():
    hashed_password = hash_password(password)
    with open('/home/babyiotito/scripts/frontend/credentials.txt', 'w') as file:
        file.write(f'username=admin\npassword={hashed_password}\n{password}')


while True: # monitor the button for factoring reset 
    current_button_state = GPIO.input(26) 

    if current_button_state == GPIO.HIGH:
        print("Button was pushed!")
        #GPIO.setup(23, GPIO.OUT)
        
        start_time_timestamp = time.time();
        start_time_formatted = datetime.fromtimestamp(start_time_timestamp)

        print("botão pressionado em:", start_time_formatted)
        prev_button_state = GPIO.HIGH
        print(prev_button_state)

        while GPIO.input(26) == GPIO.HIGH and (time.time() - start_time_timestamp) < 3:
             time.sleep(0.1)
             
        if (time.time() - start_time_timestamp) >= 3:
                 LedControl.LED_ON()
                 reset_eth0()
                 reset_credentials()
                 print("success!")


                 time.sleep(0.2)

                 subprocess.run(['sudo', 'reboot'])

        time.sleep(0.1)

    else:   
        if prev_button_state == GPIO.HIGH:
            print("Button was released")
            prev_button_state = GPIO.LOW
            print(prev_button_state)
        
        #GPIO.output(23, GPIO.LOW)

    time.sleep(0.5) 
    #prev_button_state == current_button_state



