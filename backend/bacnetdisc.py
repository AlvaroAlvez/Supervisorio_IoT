import BAC0
import sys
sys.path.append('/home/babyiotito/scripts/backend')
from MqttProtocol import export_Mqtt_payload
import time


#mqtt payload
teste1 = export_Mqtt_payload()

if teste1 == 'bacnet':
  print("works")
else:
  print("not worked")

        
try:
   while True:

        teste1 = export_Mqtt_payload()

        if teste1 == 'bacnet':
            print("works")
        else:
            print("not worked")
                
        time.sleep(0.5)
                


except KeyboardInterrupt:
        print('bacnet discover sttoped ')

