import BAC0
import sys
sys.path.append('/home/babyiotito/scripts/backend')
from MqttProtocol import export_Mqtt_payload
sys.path.append('/home/babyiotito/scripts/services')
from RaspResources import resources

#Discover Bacnet Devices
eth0_instance = resources()
eth0_ip_BAC = eth0_instance.get_eth0_ip()
print(eth0_ip_BAC)

#serial number
srl_nmbr_instance = resources()
srl_nmbr = srl_nmbr_instance.get_serial_nmbr()

print(export_Mqtt_payload)

try:
        while True:
                pass


except KeyboardInterrupt:
        print('bacnet discover sttoped ')

