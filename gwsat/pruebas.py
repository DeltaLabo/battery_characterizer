import pyvisa
import controller2 #Solo se va a usar la Electronic Load
import RPi.GPIO as GPIO
import threading
import time

### Resetear los GPIOs ###

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.OUT) #Pin #17 RPi
GPIO.setup(18,GPIO.OUT) #Pin #18 RPi
GPIO.output(17, GPIO.LOW)
GPIO.output(18, GPIO.LOW)
##########################

### Resource-set-up communication ###

rm = pyvisa.ResourceManager()
print("Este es el número 1:\n", rm.list_resources()[1])
carga = rm.list_resources()[1]
print("La carga está dada por el recurso", carga)


for i in range(2):
    if rm.list_resources()[i].find("DL3A21") > 0:
        carga = rm.open_resource(rm.list_resources()[i]) 
        print("Carga DL3A21 encontrada")
        print(carga.query("*IDN?"))
    #else:
    #    print("Electronic load not found!")

Carga = controller2.Carga(carga, "DL3A21")

Carga.remote_sense(True)
Carga.set_mode("VOLT") #CV ON
time.sleep(5)
Carga.set_volt_range(15) 
