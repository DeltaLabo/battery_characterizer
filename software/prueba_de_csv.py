#Probar loop del thread
import pyvisa
import controller2
import time
from time import sleep
import threading
import pandas as pd
rm = pyvisa.ResourceManager()
fuente = rm.open_resource(rm.list_resources()[0])
fuente.write_termination = '\n'
fuente.read_termination = '\n'

Fuente = controller2.Fuente(fuente,"SPD1305" )

volt = 1.0
current = 1.0
power = 1.0
channel = 1

def medicion():
    global volt, current, power
    Fuente.aplicar_voltaje_corriente(1, 3.5, 0.5)
    time.sleep(0.02)
    Fuente.encender_canal(1)
    time.sleep(0.02)
    volt, current, power = Fuente.medir_todo(channel)
    time.sleep(0.02)
    print (volt, current, power)
    #time.sleep(3)

#medicion()
while True:
    medicion()
    time.sleep(2)

    