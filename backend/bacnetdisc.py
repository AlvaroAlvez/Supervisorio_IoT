import BAC0

bacnet = BAC0.connect(ip='192.168.1.60')

devices = bacnet.whois()

print(devices)


