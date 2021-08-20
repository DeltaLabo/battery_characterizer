#Código para ciclar baterías en un rango de tensión y corriente definidos previamente
import pyvisa
import controller
import time
from time import sleep
#Se define una variable global que se utilizará dentro de cada función
#Se define para no tener que estar definiéndolo de nuevo en cada estado
state = 'i'
#Definir el orden de la fuente y de la carga
rm = pyvisa.ResourceManager()
print(rm.list_resources()) #Retorna los recursos (fuente y carga)
fuente = rm.open_resource(rm.list_resources()[0])
print(fuente.query("*IDN?"))
Fuente = controller.Fuente(fuente, "Diego") #Parámetro para iterar cuando hay más recursos
#################################################################################################
#Primero se definirá la base de la máquina de estados (utilizando diccionarios)
def statemachine (entry):
    global state #Se llama a la variable global que se definió 
    #afuera de las funciones 
    switch = {'i': INIT,
              0 : CHARGE,
              1: DISCHARGE,
              2: WAIT,        
    }         #switch será el diccionario donde se guarden los cuatro estados
    func = switch.get(state)
    return func(entry)

#Se define cada uno de los estados (inicial, carga, descarga y espera)

def INIT(entry):
    global state
    print ("Estado inicial... \n")
    sleep(2)
    entry = input("Deberá digitar la letra 'a' para avanzar al siguiente estado: \n")
    #Aquí se definirá la condición para que la máquina pase de una estado a otro
    if entry == "a":
        state = 0
        print("Avanzando al estado de CARGA...")
    else:
        state = 'i'
        sleep (2)
        print("Se mantiene el estado inicial... Digite la letra correcta")
        sleep(2)
    
#Se setea el recurso de la fuente para CARGAR la batería 
#Sección para definir cuáles son los recursos y su orden

def CHARGE (curr):
    global state
    sleep(2)
    channel = int(input("Digite el canal que utilizará (1, 2, 3): \n")) #Canal a utilizar
    tension = float(input("Digite la tensión a setear en la fuente:\n")) #Tensión máxima
    corriente = float(input("Digite la capacidad de la batería en Ah:\n"))
    curr = corriente / 2
    Fuente.aplicar_voltaje_corriente(channel, tension, curr)
    Fuente.encender_canal(channel)
    time.sleep(10)
    print(Fuente.medir_todo(channel))
    #Fuente.apagar_canal(channel)

    #Tres opciones: >=, ==, <=
    if curr == 1.5:
        state = 1
        Fuente.apagar_canal(channel)
        print("Avanzando al estado de DESCARGA...")
        
    elif curr > 1.5:
        state = 0
        print("El valor de la corriente es mayor a 100 mA...")
        sleep(2)
# Aquí podría definirse qué es la acción que se llevará a cabo si la corriente
# es MAYOR a la que se defina (100 mA, en este caso) 
       
    elif curr < 1.5:
        state = 0
        print ("El valor de la corriente todavía es menor a 100 mA...")
        sleep(2)
# Aquí podría definirse qué es la acción que se llevará a cabo si la corriente
# es MENOR a la que se defina (100 mA, en este caso)   

#Se setea el recurso de la CARGA para descargar la batería       
def DISCHARGE(voltage):
    global state
    sleep(2)
    voltage = float(input("Digite el valor medido de la tensión de la batería (V): \n"))
    #Tres opciones: -=, ==, +=
    if voltage == 2.5:
        state = 2
        print("Avanzando al estado de ESPERA...")
# A partir de aquí, el circuito debe abrirse y no puede seguirse descargando
# Orden al programa de dejar de descargar       
    elif voltage > 2.5:
        state = 1
        print ("El valor de tensión en la batería es mayor al mínimo para avanzar...")
        sleep(2)

    elif voltage < 2.5:
        state = 1
        print("¡ALERTA! El valor de tensión de la batería es menor al mínimo... ")
        sleep(2)
# Este es un estado crítico. La tensión de la celda no puede bajar 
# más allá de su mínimo.
def WAIT(entry):
    global state
    sleep (10)
    state = 0
    print("Volviendo al estadio inicial...")
        
# Programa Principal (loop de la máquina de estado)
cont = int(input("Digite la cantidad de ciclos de carga/descarga de la batería: \n"))
contador = 0
while contador <= cont:
    statemachine('i')
    contador = contador +1
##########################
#while True:
#    statemachine('i')
##########################    
###################################################################################################
#cont = int(input("Digite la cantidad de ciclos de carga/descarga de la batería:\n"))
#contador = 0
#while contador <= cont:
#    statemachine('i')
#    contador = contador + 1
###################################################################################################