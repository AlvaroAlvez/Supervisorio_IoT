import BAC0
import sys
sys.path.append('/home/babyiotito/scripts/services')
from RaspResources import resources
import json

#Getting IP address
raspi_resources = resources()
raspi_Eth0 = raspi_resources.get_eth0_ip()

#connecting to bacnet
bacnet = BAC0.connect(f"{raspi_Eth0}/24")

#connect to bacnet
def bacnet_devices():
    devices = bacnet.whois()
    device_json = json.dumps(devices)
    return device_json





    
