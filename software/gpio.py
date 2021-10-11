import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.OUT)
GPIO.setup(18,GPIO.OUT)
#GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  
#GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 

#def my_callback(channel):  

#GPIO.add_event_detect(24, GPIO.RISING, callback=my_callback, bouncetime=1000) 

while True:
	GPIO.output(18,GPIO.LOW)
	time.sleep(0.5)
	GPIO.output(17,GPIO.HIGH)
	time.sleep(60)

	
