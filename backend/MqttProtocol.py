import paho.mqtt.client as Mqtt
import sys
sys.path.append('/home/babyiotito/scripts/services')
from RaspResources import resources


#class Mqtt:
class Mqtt_class():

    def __init__(self, broker, port, client_id): #Encapsula as funcionalidades Mqtt server, o __init__ é o construtor da class e inicia vários atributos no "self"
        self.client = Mqtt.Client(client_id) #o atributo self é indispensável para apontar para o atributo dentro da class
        self.client.on_message = self.on_message
        self.client.on_publish = self.on_publish
        self.broker = broker
        self.port = port

    def Mqtt_connect(self):
        self.client.connect(self.broker, self.port)
        self.client.loop_start()

    def on_publish(self, client,userdata,result):
        print("data published \n")
        pass

    def on_subscribe(self, topic, qos):
        self.client.subscribe(topic, qos)

    def on_message(self, client, userdata, msg): #eu não preciso chamar essa função, no paho lib, essa função é chamada automaticamente se chegar uma msg no tópico subscrito
        #somente preciso subscrever o tópico e deixar a função declarada
        message_received = (f"{msg.topic}: {msg.payload.decode()}")
        print (message_received)

        
    def publish_message(self, topic, message):
        self.client.publish(topic, message)

if __name__ == "__main__":#padrão da linguagem, quando informo isso, quer dizer que o código abaixo só rodará se esse script estiver rodando
     #se chamarmos para um código externo, não rodará ai teríamos que por um else posterior
     
     broker_address = "mqtt.sobeai.com.br"
     mqtt_port = 1883
     client_id = "Raspi_server"

     #GET MAC ADRESS FROM RASPI - sempre criar uma instancia antes de solicitar a function 
     raspi_instance = resources()
     raspi_serial_nmbr = raspi_instance.get_serial_nmbr()

     mqtt_server = Mqtt_class(broker_address, mqtt_port, client_id) #o python entende os valores pela ordem colocada em __init__, logo broker entende
     #que seu valor é broker_address, por causa da sua posição na hora  do constructor se trocassemos por port, (port, Broker_adress, ...) ele colocaria o valor de port em broker
     #isso por conta da localização no código, o mesmo serve para parâmetros de função 
     mqtt_server.Mqtt_connect()
     mqtt_server.publish_message(raspi_serial_nmbr, "raspi connected")

     mqtt_server.on_subscribe(raspi_serial_nmbr, 0)


     try:
         while True:
             
             pass #loop infinito
     except KeyboardInterrupt:
         print("Mqtt code server stopped")
