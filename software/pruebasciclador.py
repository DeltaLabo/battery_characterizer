import pyvisa
import controller
import time
from time import sleep

#Se debe lograr poner la fuente primero en CC para la primera parte de la carga
#Para la segunda parte, sin apagar el canal, debe pasarse a CV
def CHARGE(charge_voltage, charge_current):
    global state 
    channel = int(input("Digite el canal de la fuente en el que se cargará (1, 2, 3): \n"))
    iprotection = float(input("Digite el valor máximo de corriente:\n"))
    #Al llegar a este valor, el canal se apagará. Se dispara. Sirve como "fusible"
    vprotection = float(input("Digite el valor máximo de tensión:\n"))
    #Al llegar a este valor, el canal se apagará.
    #Estos valores pueden ser entrada o pueden quedarse como fijos
    #Dependerá del tipo y características de la batería 
    charge_current = float(input("Digite la capacidad de la batería en Ah:\n"))# Se fijará
    charge_voltage = float(input("Digite la tensión máxima de operación:\n"))#Setea tensión en el canal
    Fuente.aplicar_voltaje_corriente(channel, charge_voltage, charge_current)
    Fuente.encender_canal(channel) #¿Cómo hago para que me mida solo tensión?
    #Ya para este momento, el canal debe estar en CC *tensión empezará a aumentar
    
    while True:
        return Fuente.medir_todo(channel(voltaje))

    Fuente.medir_todo(channel) = voltaje, corriente, potencia
    
    #Tres casos: 1) cuando llega a la vprotection
    if Fuente.medir_todo[0] >= vprotection:
        Fuente.apagar_canal(channel)
        print("Se dispara la protección...\n Se volverá a iniciar el programa")
        sleep(3)
        state = 'i'

    #2)  Cuando llega al voltaje seteado (cut-off voltage)
    elif Fuente.medir_todo[0] == charge_voltage: #Pasa al estado de descarga
        print("Se ha llegado al cutt-off voltage. Se pasa al estado de descarga...\n")
        state = 1

    # 3) Si es menor al voltaje máximo de operación, seguirá cargando

def DISCHARGE(discharge_current):
    global state
    #Se pasará a CV. La tensión se fijará y la corriente empezará a disminuir
    discharge_current = float(input("Digite la corriente mínima a la que puede llegar la batería:\n"))
    discharge_current_prot = discharge_current * 0.9

    if Fuente.medir_todo[1] == discharge_current: #Pasa al estado de WAITING 
        print("Se ha terminado el primer ciclo de carga/descarga...")
        sleep(5)
        state = 2

    elif Fuente.medir_todo[1] <= discharge_current_prot:
        print("Se dispara la protección...\n Se volverá a iniciar el programa")
        sleep(3)
        state = 'i'

    # 3) Si es mayor a la corriente mínima, seguirá descargando


##########Para que me mida constantemente la tensión, corriente y potencia########## 
#while True:
#    return Fuente.medir_todo(channel)
#    sleep(5)


    