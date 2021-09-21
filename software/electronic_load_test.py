''' 
Carga electrónica Rigol DL3021
'''
import pyvisa
import controller2
import time

rm = pyvisa.ResourceManager()
print(rm.list_resources()[1])
carga = rm.open_resource(rm.list_resources()[1]) 
#El orden va a cambiar en la progra. La fuente va a ser [1] y la carga [2]. O viceversa.
#carga.write_termination = '\n'
#carga.read_termination = '\n'

Carga = controller2.Carga(carga, "DL3021")


Carga.encender_carga()
print("Se encendió la carga...") 
time.sleep(3)
Carga.fijar_voltaje(5.0)
print("Se fijó el voltaje...") 
time.sleep(3)
Carga.fijar_corriente(0.002)
print("Se fijó la corriente") 
time.sleep(3)
Carga.fijar_resistencia(5.0)
print("Se fijó la resistencia...") 
time.sleep(3)
Carga.apagar_carga()
print("Se apagó la carga...") 

