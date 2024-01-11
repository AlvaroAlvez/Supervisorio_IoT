import BAC0
import sys
sys.path.append('/home/babyiotito/scripts/backend')
from MqttProtocol import Mqtt_class
sys.path.append('/home/babyiotito/scripts/services')
from RaspResources import resources

#Discover Bacnet Devices
eth0_instance = resources()
eth0_ip_BAC = eth0_instance.get_eth0_ip()
print(eth0_ip_BAC)

#serial number
srl_nmbr_instance = resources()
srl_nmbr = srl_nmbr_instance.get_serial_nmbr()

#listen to mqtt topic
broker_address = "mqtt.sobeai.com.br"
mqtt_port = 1883
client_id = "Raspi_server"

Mqtt_lst_instance = Mqtt_class(broker_address, mqtt_port, client_id)
Mqtt_lst_msg = Mqtt_lst_instance.on_subscribe(srl_nmbr, 0)
print(Mqtt_lst_msg)

if Mqtt_lst_msg == 'bacnet':
        bacnet = BAC0.connect(ip=eth0_ip_BAC)
        devices = bacnet.whois()
        print(devices)

try:
        while True:
                pass
except KeyboardInterrupt:
        print('bacnet discover sttoped ')

