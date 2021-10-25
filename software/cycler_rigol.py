############Código para ciclar baterías en un rango de tensión y corriente definidos############
# Diego Fernández Arias y Juan J. Rojas
# Instituto Tecnológico de Costa Rica
import pyvisa
import controller2
import time
from time import sleep
import threading
import pandas as pd
##########################Actualización del código con 'controller2'##################################
rm = pyvisa.ResourceManager()
fuente = rm.open_resource(rm.list_resources()[0])
fuente.write_termination = '\n'
fuente.read_termination = '\n'

# Alternativa al no tener un comando 'query' para 
fuente.write("*IDN?")
time.sleep(0.1) 
id = fuente.read()
print(id) #Imprime la identificación del recurso
time.sleep(0.2)

Fuente = controller2.Fuente(fuente, "SPD1305") # SPD parámetro para iterar cuando hay más recursos
#############################################################################################
# rm = pyvisa.ResourceManager()
# print(rm.list_resources()) #Retorna los recursos (fuente y carga)
# fuente = rm.open_resource(rm.list_resources()[0])
# #print(fuente.query("*IDN?")) #Verificar orden dela fuente y la carga
# Fuente = controller2.Fuente(fuente, "Diego") #'Diego' parámetro para iterar cuando hay más recursos


df = pd.read_csv("C:/Repositories/battery_characterizer/software/prueba_inputs.csv", header=0)

state = 0 #Variables globales que se utilizará dentro de cada función
channel = df.iloc[0,0] #[Fila,columna] Variable global del canal (Canal 3 por default)
#channel = int(input("Digite el canal a utilizar: \n")) #Variable global para usar el mismo canal
volt = 1.0 #Variable global 
current = 1.0 #Variable global
power = 1.0 #Variable global 

##########################Se define el diccionario con los estados##################################

#Primero se definirá la base de la máquina de estados (utilizando diccionarios)
def statemachine (entry):
    global state #Se llama a la variable global que se definió 
    #afuera de las funciones 
    switch = {0 : INIT, #Entre carga y descarga debería haber un wait de ciertos minutos (15 min)
              1 : CHARGE,
              2 : DISCHARGE,
              3 : WAIT,        
    }         #switch será el diccionario donde se guarden los cuatro estados
    func = switch.get(state)
    return func(entry)

#Se define cada uno de los estados (inicial, carga, descarga y espera)

#########################Se define la función del estado inicial#####################################

def INIT(entry):
    global state
    print ("Estado inicial... \n")
    sleep(2)
    entry = input("Deberá digitar la letra 'a' para avanzar al siguiente estado: \n")
    #Aquí se definirá la condición para que la máquina pase de una estado a otro
    if entry == "a":
        state = 1
        print("Avanzando al estado de CARGA...")
    else:
        state = 0
        sleep (2)
        print("Se mantiene el estado inicial... Digite la letra correcta")
        sleep(2)
    
#Se setea el recurso de la fuente para CARGAR la batería 
#Sección para definir cuáles son los recursos y su orden

################# Se define la función que hará que la batería se cargue ############################

#Condicional dentro del timer para que se quite cuando me avanza de estado
def medicion():
    global volt
    global current
    global power
    volt,current,power = Fuente.medir_todo(channel) #Esto sobreescribe los valores inclusive
    #fuera de esta función? Para que esté correcto el uso en los ifs de "CHARGE".
    time.sleep(0.02) #Nuevo por falta de query
    print(f'La tensión es {volt}, la corriente es de {current} y la potencia de {power}')
    df1 = pd.Dataframe(names=["Canal","Tensión máxima batería","Corriente batería"])
    df1.to_csv('C:/Repositories/battery_characterizer/software/prueba_outputs.csv', index_col="Canal")
    #t = threading.Timer(5, medicion()) # esto creo que no va



    #Esto puede pasar a no imprimir en la terminal los valores, sino guardarlos
    #en un csv para después graficar con los valores de I y V
    #df = pd


def CHARGE (curr): #cambiar este parámetro
    global state
    global channel
    global volt
    global current
    global power 
    sleep(2)
    df2 = pd.read_csv("C:/Repositories/battery_characterizer/software/prueba_inputs.csv", header=0)
    #tension_fuente = float(input("Digite la tensión a setear en la fuente (V):\n")) #Tensión máxima
    tension_fuente = df2.iloc[0,1] #[fila,columna]
    #corriente_fuente = float(input("Digite la corriente máxima (A):\n")) #Corriente de protección
    corriente_fuente = df2.iloc[0,2] #[fila,columna]
    mitad_corriente_fuente = corriente_fuente / 2
    Fuente.aplicar_voltaje_corriente(channel, tension_fuente, mitad_corriente_fuente)
    time.sleep(0.02) #Nuevo por falta de query
    Fuente.encender_canal(channel) #Solo hay un canal (el #1)
    #time.sleep(5)

    #while state == 1:
    t = threading.Timer(5, medicion)
    t.start() #Después de 5 segundos ejecutará lo de medición ()

    while True:
        
        # >=, ==, <=
        #if Fuente.medir_todo(channel)[1] == 1.12: #1.12 A por V/R = I = 4/3.3
        if current == 1.12: #1.12 A por V/R = I = 4/3.3
            state = 2
            #Fuente.apagar_canal(channel)
            #print("Avanzando al estado de DESCARGA...")
            break 
            
        elif current > 1.12: 
        #elif Fuente.medir_todo(channel)[1] > 1.12:
            state = 1
            Fuente.apagar_canal(channel)
            time.sleep(0.02) #Nuevo por falta de query
            #print("CUIDADO! El valor de la corriente es mayor al máximo de 1.12 A...")
            #sleep(2)
    
        elif current < 1.12: 
        #elif Fuente.medir_todo(channel)[1] < 1.12:
            state = 1
            #print ("El valor de la corriente todavía es menor a 1.12 A...")
            #sleep(2) #Este sleep puede ser peligroso por el tiempo que detiene al 'while'

################# Se define la función que hará que la batería se descargue #########################

#Se setea el recurso de la CARGA para descargar la batería       
def DISCHARGE(voltage):
    global state
    sleep(2)
    voltage = float(input("Digite el valor medido de la tensión de la batería (V): \n"))
    #Tres opciones: -=, ==, +=
    if voltage == 2.5:
        state = 3
        print("Avanzando al estado de ESPERA...")
# A partir de aquí, el circuito debe abrirse y no puede seguirse descargando
# Orden al programa de dejar de descargar       
    elif voltage > 2.5:
        state = 2
        print ("El valor de tensión en la batería es mayor al mínimo para avanzar...")
        sleep(2)

    elif voltage < 2.5:
        state = 2
        print("¡ALERTA! El valor de tensión de la batería es menor al mínimo... ")
        sleep(2)
# Este es un estado crítico. La tensión de la celda no puede bajar 
# más allá de su mínimo.

################ Se define la función que esperará y retornará al estado inicial ####################

def WAIT(entry):
    global state
    sleep (10)
    state = 1
    print("Volviendo al estadio inicial...")
        
######################## Programa Principal (loop de la máquina de estado) ########################
cont = int(input("Digite la cantidad de ciclos de carga/descarga de la batería: \n"))
contador = 0
while contador <= cont:
    statemachine(0)
    contador = contador +1 # Necesita múltiplos de 3 por alguna razón
