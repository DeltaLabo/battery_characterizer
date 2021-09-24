''' 
Carga electrónica Rigol DL3021
'''
import pyvisa
import controller2
import time
import equipment as eq 
import string

#eload = Eload_DL3000.DL3000()
#eloads = eq.Carga()
#eload = eloads.choose_eload()
#print (eload)

rm = pyvisa.ResourceManager()
print(rm.list_resources()[1])
for i in range(2):
	if rm.list_resources()[i].find("DL3A21") > 0:
		carga = rm.open_resource(rm.list_resources()[i]) 
		print("Carga DL3A21 encontrada")
	elif rm.list_resources()[i].find("SPD13") > 0:
		fuente = rm.open_resource(rm.list_resources()[i]) 
		print("Fuente SPD1305X encontrada")
	
#El orden va a cambiar en la progra. La fuente va a ser [1] y la carga [2]. O viceversa.
#carga.write_termination = '\n'
#carga.read_termination = '\n'


Carga = controller2.Carga(carga, "DL3021")

#Carga.encender_carga()
#print("Se encendió la carga...") 
#time.sleep(3)
#Carga.fijar_voltaje(5.0)
#print("Se fijó el voltaje...") 
#time.sleep(3)
#Carga.fijar_resistencia(5.0)
#print("Se fijó la resistencia...") 
#time.sleep(3)
#Carga.apagar_carga()
#print("Se apagó la carga...") 
Carga.remote_sense("ON")
print("Se encendió el canal de sensado...") 
time.sleep(3)
Carga.fijar_corriente(0.8)
print("Se fijó la corriente") 
time.sleep(3)
Carga.encender_carga()
Carga.medir_corriente()
current = Carga.medir_corriente()
print(current)
time.sleep(3)
Carga.medir_voltaje()
voltage = Carga.medir_voltaje()
print(voltage)
time.sleep(3)
#Carga.remote_sense("OFF")
#time.sleep(3)
Carga.apagar_carga()
print("Fin de la prueba")



