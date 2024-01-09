import paho.mqtt.client as Mqtt
import sys
sys.path.append('/home/babyiotito/scripts/services')
from RaspResources import resources

#GET MAC ADRESS FROM RASPI - sempre criar uma instancia antes de solicitar a function
raspi_instance = resources() #instancia chamand a class resources
raspi_serial_nmbr = raspi_instance.get_serial_nmbr() #chama a função da instancia(class)
print(raspi_serial_nmbr)

#CONNECT TO MQTT Broker
broker = "192.168.1.237"
port = 1883

def on_publish(client,userdata,result):
    print("data published \n")
    pass

client1 = Mqtt.Client("client1")
client1.on_publish = on_publish
client1.connect(broker, port)
ret=client1.publish(raspi_serial_nmbr, "teste ok")


