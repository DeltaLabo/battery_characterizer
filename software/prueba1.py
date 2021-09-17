import pyvisa
import controller
import time
import math

#Sección para definir cuáles son los recursos y su orden
rm = pyvisa.ResourceManager()
print(rm.list_resources()) #Retorna los recursos (fuente y carga)
fuente = rm.open_resource(rm.list_resources()[0])
print(fuente.query("*IDN?"))

#Carga de la batería
#Setear el recurso de la fuente
Fuente = controller.Fuente(fuente, "Diego")
channel = int(input("Digite el canal que utilizará (1, 2, 3): \n"))
tension = float(input("Digite la tensión a setear en la fuente:\n"))
corriente = float(input("Digite la capacidad de la batería (Ah):\n"))
#crrnte = corriente / 2
#print(crrnte)
Fuente.aplicar_voltaje_corriente(channel, tension, corriente)
#Carga.fijar_corriente(corriente)
#print(Carga.fijar_corriente)
Fuente.encender_canal(channel)
time.sleep(5)
print(Fuente.medir_todo(channel))
Fuente.apagar_canal(channel)

#Descarga de la batería
#Setear el recurso de la carga
#Carga = controller.Carga(fuente, "Dieguito")