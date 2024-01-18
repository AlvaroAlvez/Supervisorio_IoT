import BAC0
import sys
sys.path.append('/home/babyiotito/scripts/services')
from RaspResources import resources

#Getting IP address

raspi_resources = resources()
raspi_Eth0 = raspi_resources.get_eth0_ip()

#connect to bacnet
def bacnet_devices():
    bacnet = BAC0.connect(f"{raspi_Eth0}/24")
    devices = bacnet.whois()
    return devices








    
