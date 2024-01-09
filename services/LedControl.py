import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)

def LED_Indicator():
    GPIO.setup(23, GPIO.OUT)
    GPIO.output(23, GPIO.HIGH)
    time.sleep(3)
    GPIO.output(23, GPIO.LOW)
    time.sleep(0.1)
    #GPIO.cleanup()

def LED_ON():
    GPIO.setup(23, GPIO.OUT)
    GPIO.output(23, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(23, GPIO.LOW)
    #GPIO.cleanup()

try:
    #GPIO.cleanup()
    LED_Indicator()
except:
    pass