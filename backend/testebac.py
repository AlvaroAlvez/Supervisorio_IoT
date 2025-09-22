import BAC0
import json

# Caminho do JSON para salvar dispositivos
DEVICES_JSON = "/home/babyiotito/scripts/services/devices.json"

def main():
    # Conecta ao BACnet
    bacnet = BAC0.connect(ip="192.168.20.71/24", port=47808)
    print("BACnet conectado:", bacnet)

    # Descobre dispositivos na rede
    print("Procurando dispositivos BACnet na rede...")
    bacnet.discover()
    # Aguarda discovery
    import time
    time.sleep(2)

    devices_info = {}

    if bacnet.discoveredDevices:
        for addr, instance in bacnet.discoveredDevices.items():
            devices_info[str(instance)] = str(addr)
            print(f"- Device instance {instance} em {addr}")
    else:
        print("Nenhum dispositivo BACnet encontrado.")

    # Salva JSON com IP / endereco dos devices
    with open(DEVICES_JSON, 'w') as f:
        json.dump(devices_info, f, indent=4)

    print(f"\nJSON salvo em {DEVICES_JSON}:\n{json.dumps(devices_info, indent=4)}")

    # 
    # Exemplo de leitura do primeiro device encontrado:
    if devices_info:
        first_instance = list(devices_info.keys())[0]
        addr = devices_info[first_instance]

        # Digite manualmente no prompt para testar
        while True:
            try:
                obj_instance = int(input("\nDigite o numero do multiStateInput para ler: "))
                value = bacnet.read(f"{addr} multiStateInput {obj_instance} presentValue")
                print(f"multiStateInput {obj_instance} presentValue: {value}")
            except KeyboardInterrupt:
                print("\nEncerrando leitura...")
                break
            except Exception as e:
                print(f"Erro: {e}")

if __name__ == "__main__":
    main()
