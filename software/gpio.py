import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.OUT)
GPIO.setup(18,GPIO.OUT)

while (1):
	GPIO.output(17,GPIO.LOW)
	time.sleep(60)
	GPIO.output(17,GPIO.LOW)
	
