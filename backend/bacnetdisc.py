import BAC0
import sys
sys.path.append('/home/babyiotito/scripts/services')
from RaspResources import resources
import time

#Discover Bacnet Devices
eth0_instance = resources()
eth0_ip_BAC = eth0_instance.get_eth0_ip()
print(eth0_ip_BAC)

#serial number
srl_nmbr_instance = resources()
srl_nmbr = srl_nmbr_instance.get_serial_nmbr()

#mqtt payload
def get_Mqtt_payload():
        with open('/home/babyiotito/scripts/backend/payload.txt', 'r') as file:
                 Mqtt_message = file.readline()
        print(Mqtt_message) 
        
try:
        while True:
                time.sleep(0.5)
                pass


except KeyboardInterrupt:
        print('bacnet discover sttoped ')

