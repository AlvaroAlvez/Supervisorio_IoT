import BAC0
import time

# Inicializa BAC0 na sua interface de rede
bacnet = BAC0.lite(ip='192.168.20.71', port=47808)
print(f"BACnet instance running: {bacnet}")


time.sleep(2)

# Envia Who-Is para todos os dispositivos (0-4194303)
print("Enviando Who-Is...")
devices = bacnet.discover()
time.sleep(2)

# Mostra dispositivos encontrados
if devices:
    print("Dispositivos encontrados:")
    for device in devices:
        print(device)
else:
    print("Nenhum dispositivo BACnet respondeu.")

# Encerra BAC0
bacnet.disconnect()
