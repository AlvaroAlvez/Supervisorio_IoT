import paho.mqtt.client as Mqtt
import sys
sys.path.append('/home/babyiotito/scripts/services')
from RaspResources import resources
#import threading #cria threads, que são fluxos separados de controle dentro do código, permitindo uma correta execução do programa 
import time

payload = None
last_payload = None

#class Mqtt:
#class Mqtt_class():
    #class Mqtt_class(broker, port, client_id)
    #o python entende os valores pela ordem colocada em __init__, logo broker entende
    #que seu valor é broker_address, por causa da sua posição na hora  do constructor se trocassemos por port, (port, Broker_adress, ...) ele colocaria o valor de port em broker
    #isso por conta da localização no código, o mesmo serve para parâmetros de função 

#    def __init__(self, broker, port, client_id): #Encapsula as funcionalidades Mqtt server, o __init__ é o construtor da class e inicia vários atributos no "self"
#        self.client = Mqtt.Client(client_id) #o atributo self é indispensável para apontar para o atributo dentro da class
#        self.client.on_message = self.on_message
#        self.client.on_publish = self.on_publish
#        self.broker = broker
#        self.port = port
#        self.payload = None #inicia o payload com um valor nulo
#        self.payload_lock = threading.Lock() #evita condições de corrida, onde duas ou mais threads tentam acessar a mesma variável
                                             #cria um objeto Lock associado a classe, objetivo: garantir que uma thread por vez tente acessar a sessão crítica

#def Mqtt_connect(broker, port, client):
#    client = Mqtt.Client(client_id=client)
#    client.connect(broker, port, client)
#    client.loop_start()

#def on_publish(client,userdata,result): # função de callback, quando o paho publicar recebemos uma função de callback
    #dizendo que a mensagem foi publicada
#    print("data published \n")
#    pass

#def on_subscribe(client, topic, qos):
#    client.subscribe(topic, qos) 

def on_message(client, userdata, msg): #eu não preciso chamar essa função, no paho lib, essa função é chamada automaticamente se chegar uma msg no tópico subscrito
                                       #somente preciso subscrever o tópico e deixar a função declarada
#    with payload_lock:#garante que apenas uma thread por vez tente acessar o que está no bloco, no caso self.payload
#       payload = msg.payload.decode()
        global payload
        global last_payload

        message_received = f"{msg.topic}: {msg.payload.decode()}"
        payload = msg.payload.decode()
        print(message_received)
        print(payload)

        with open('/home/babyiotito/scripts/backend/payload.txt', 'r') as file:
                 last_payload=file.read()

        if payload != last_payload:
           with open('/home/babyiotito/scripts/backend/payload.txt', 'w') as file:
                 file.write(payload)
           export_Mqtt_payload()
        
        
def publish_message(client, topic, message):
    client.publish(topic, message)

def on_publish(client, userdata, result):
     print("data published \n")
     pass
    
#def get_Mqtt_payload():
    #with self.payload_lock:#mesma situação que on_message, porém para acessar o return 
#    return payload
        


def export_Mqtt_payload():
      with open('/home/babyiotito/scripts/backend/payload.txt', 'r') as file:
           exported_payload=file.read()
      print(exported_payload)
      return exported_payload
   
    
if __name__ == "__main__":#padrão da linguagem, quando informo isso, quer dizer que o código abaixo só rodará se esse script estiver rodando
     #se chamarmos para um código externo, não rodará ai teríamos que por um else posterior
     
     #GET MAC ADRESS FROM RASPI - sempre criar uma instancia antes de solicitar a function 
     raspi_instance = resources()
     raspi_serial_nmbr = raspi_instance.get_serial_nmbr()

     #connect to mqqt

     broker = "mqtt.sobeai.com.br"
     port = 1883
     client = Mqtt.Client("raspi server")
     client.connect(broker, port)
     
     client.on_message=on_message
     client.on_publish=on_publish
     client.subscribe(raspi_serial_nmbr, qos=0)
     client.publish(raspi_serial_nmbr, "raspi connected")

     client.loop_start()

     try:
         while True:
             time.sleep(0.5)
             #pass #loop infinito
     except KeyboardInterrupt:
         print("Mqtt code server stopped")
