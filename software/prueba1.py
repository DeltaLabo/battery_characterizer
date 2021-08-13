import pyvisa
import controller
import time

#Sección para definir cuáles son los recursos y su orden
rm = pyvisa.ResourceManager()
print(rm.list_resources()) #Retorna los recursos (fuente y carga)
fuente = rm.open_resource(rm.list_resources()[0])
print(fuente.query("*IDN?"))

#Setear el recurso de la fuente
Fuente = controller.Fuente(fuente, "Diego")
Fuente.aplicar_voltaje_corriente(1, 5, 0.5)
Fuente.encender_canal(1)
time.sleep(5)
print(Fuente.medir_todo(1))
Fuente.apagar_canal(1)