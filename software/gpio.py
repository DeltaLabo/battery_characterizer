import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.OUT)
GPIO.setup(18,GPIO.OUT)

while (1):
	GPIO.output(17,GPIO.HIGH)
	time.sleep(0.5)
	GPIO.output(17,GPIO.LOW)
	time.sleep(0.5)
	GPIO.output(18,GPIO.HIGH)
	time.sleep(0.5)
	GPIO.output(18,GPIO.LOW)
	time.sleep(0.5)


