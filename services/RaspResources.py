from getmac import get_mac_address

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



