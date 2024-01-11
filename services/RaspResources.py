from getmac import get_mac_address
import re

class resources():

    def get_mac_addr(self): #devo colocar sempre o "self" para conseguir usar um método de uma função da class em python posso passar um parâmetro tbm dpd do "self"
        rasp_mac = get_mac_address()
        return rasp_mac
    

    def get_serial_nmbr(self): #get serial number from raspi
        raspiSerial = "0000000000000000"
        try:
           with open('/proc/cpuinfo' , 'r') as f:
            for line in f:
              if line.startswith('Serial'): #procura a linha que começa com 'Serial'
               raspiSerial = line[10:26].strip() #10:26 representa a quantidade de caracteres a serem lidos na linha que começa cpom 'Serial'
           f.close()
        except:
           raspiSerial = "ERROR000000000"
        return raspiSerial
    

    def get_eth0_ip(self):
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

     


