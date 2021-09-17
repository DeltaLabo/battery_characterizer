############Código para ciclar baterías en un rango de tensión y corriente definidos############
# Diego Fernández Arias
# Instituto Tecnológico de Costa Rica
import pyvisa
import controller2
import time
from time import sleep
import threading
import pandas as pd
from datetime import datetime
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.OUT)
GPIO.setup(18,GPIO.OUT)
##########################Definición 'controller2'##################################
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

#Variables globales que se utilizará dentro de cada función
state = 0 
channel = df.iloc[0,0] #[Fila,columna] Variable global del canal (Canal 1 por default)
volt = 1.0  
current = 1.0 
power = 1.0 
timer_flag = 0
init_flag = 1
counter = 0
mintowait = 0
prev_state = 0



##########################Se define el diccionario con los estados##################################

#Primero se definirá la base de la máquina de estados (utilizando diccionarios)
def statemachine (entry):
    global state #Se llama a la variable global que se definió 
    #afuera de las funciones 
    switch = {0 : INIT, #Entre carga y descarga debería haber un wait de ciertos minutos (15 min)
              1 : CHARGE,
              2 : DISCHARGE,
              3 : WAIT,
              6 : END,    
    }         #switch será el diccionario donde se guarden los cuatro estados
    func = switch.get(state)
    return func(entry)

#Se define cada uno de los estados (inicial, carga, descarga y espera)

#########################Se define la función del estado inicial#####################################

def INIT(entry):
    global state
    global df
    #df2 = pd.read_csv("C:/Repositories/battery_characterizer/software/prueba_inputs.csv", header=0)
    #tension_fuente = float(input("Digite la tensión a setear en la fuente (V):\n")) #Tensión máxima
    print ("Estado inicial... \n")
    sleep(2)
    #state = 1
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

def ISR():
    global timer_flag
    t = threading.Timer(1.0, ISR)
    t.start()
    timer_flag = 1

#Thread de medición
def medicion():
    global volt
    global current
    global power
    #t = threading.Timer(5.0, medicion)
    #t.start()
    #fuera de esta función? Para que esté correcto el uso en los ifs de "CHARGE".
    #time.sleep(0.02) #Nuevo por falta de query
    #vcp = volt,current,power 
    print(datetime.now(),end=': ')
    volt,current,power = Fuente.medir_todo(channel) #Esto sobreescribe los valores inclusive
    print(f'V = {volt} \t I = {current}\t P = {power}')
    
    df1 = pd.DataFrame(volt)#, columns = ['Voltaje'], 'Corriente', 'Potencia']) 
    print(df1)
    df1.to_csv('C:/Repositories/battery_characterizer/software/prueba_outputs.csv')#, columns = ['Voltaje'])#, 'Corriente', 'Potencia'])
   



    #Esto puede pasar a no imprimir en la terminal los valores, sino guardarlos
    #en un csv para después graficar con los valores de I y V
    #df = pd


def relay_control(state):
    if state == 1:
        GPIO.output(18,GPIO.LOW)
        time.sleep(0.5)
        GPIO.output(17,GPIO.HIGH)
        time.sleep(0.5)
    if state == 2:
        GPIO.output(17,GPIO.LOW)
        time.sleep(0.5)
        GPIO.output(18,GPIO.HIGH)
        time.sleep(0.5)
    if state == 3:
        GPIO.output(17,GPIO.LOW)
        time.sleep(0.5)
        GPIO.output(18,GPIO.LOW)
        time.sleep(0.5)
        


def CHARGE (entry): #cambiar este parámetro
    global state
    global channel
    global volt
    global current
    global power 
    global df
    global init_flag
    global timer_flag
    global counter
    global prev_state
    global mintowait
    set_supply_current = df.iloc[0,2]

    if init_flag == 1:
        set_supply_voltage = df.iloc[0,1] #[fila,columna]
        set_supply_current = df.iloc[0,2] #[fila,columna]
        half_supply_current = set_supply_current / 2
        Fuente.aplicar_voltaje_corriente(channel, set_supply_voltage, half_supply_current)
        Fuente.toggle_4w()
        Fuente.encender_canal(channel) #Solo hay un canal (el #1)
        init_flag = 0
        relay_control(state)

    if timer_flag == 1:
        timer_flag = 0
        counter +=  1
        if counter >= 5:
            medicion()
            counter = 0
    

    #while state == 1:
    #medicion() #OPCION A
    #volt2 = copy.deepcopy(volt) #OPCION A

    #print(f"Volt 1 es {volt}")
    #print(volt2)

    # if volt2 != volt: #OPCION A
    #     #t = threading.Timer(5, medicion) #OPCION A
    #     t.start() #OPCION A
    #     volt2 = copy.deepcopy(volt) #OPCION A
    #     print(volt)
    #     print(volt2)1

    # >=, ==, <=
    #if Fuente.medir_todo(channel)[1] == 1.12: #1.12 A por V/R = I = 4/3.3
    if current <= (0.25 * set_supply_current) : #1.12 A por V/R = I = 4/3.3
        prev_state = 1 #CHARGE
        state = 3 #WAIT
        init_flag = 1
        mintowait = 10
        #Fuente.apagar_canal(channel)
        #print("Avanzando al estado de DESCARGA...")
        
    #elif current > 1.12: 
    #elif Fuente.medir_todo(channel)[1] > 1.12:
        #state = 1
        #Fuente.apagar_canal(channel)
        #print("CUIDADO! El valor de la corriente es mayor al máximo de 1.12 A...")
        #sleep(2)

################# Se define la función que hará que la batería se descargue #########################

#Se setea el recurso de la CARGA para descargar la batería       
def DISCHARGE(entry):
    global prev_state
    global state
    global mintowait
    global channel
    global volt
    global current
    global power 
    global df
    global timer_flag
    global init_flag
    global counter
    
    #voltage = float(input("Digite el valor medido de la tensión de la batería (V): \n"))
    prev_state = 2 #DISCHARGE
    state = 3 #WAIT
    mintowait = 1
    relay_control(state)
    print("Se ha llegado al estado de descarga... Se avanzará al estado de espera...")

#     #Tres opciones: -=, ==, +=
#     if voltage == 2.5:
#         state = 3
#         print("Avanzando al estado de ESPERA...")
# # A partir de aquí, el circuito debe abrirse y no puede seguirse descargando
# # Orden al programa de dejar de descargar       
#     elif voltage > 2.5:
#         state = 2
#         print ("El valor de tensión en la batería es mayor al mínimo para avanzar...")
#         sleep(2)

#     elif voltage < 2.5:
#         state = 2
#         print("¡ALERTA! El valor de tensión de la batería es menor al mínimo... ")
#         sleep(2)
# Este es un estado crítico. La tensión de la celda no puede bajar 
# más allá de su mínimo.

################ Se define la función que esperará y retornará al estado inicial ####################

def WAIT(entry):
    global state
    global mintowait
    global timer_flag
    global init_flag
    global counter
    global prev_state

    relay_control(state)
    if timer_flag == 1:
        timer_flag = 0
        counter += 1
        if counter >= (mintowait * 60):
            if prev_state == 1: #CHARGE:
                state = 2 #DISCHARGE
            elif prev_state == 2: #DISCHARGE:
                state = 6 #END
    
    print("Volviendo al estadio inicial...")

####Función final. Apagará canal cuando se hayan cumplido ciclos o reiniciará
def END(entry):
    print("Terminó el ciclo...")
    Fuente.apagar_canal(channel)
    Fuente.aplicar_voltaje_corriente(channel,0,0)

######################## Programa Principal (loop de la máquina de estado) ########################
t = threading.Timer(1.0, ISR)
t.start() #Después de 5 segundos ejecutará lo de medición ()
cycles = int(input("Digite la cantidad de ciclos de carga/descarga de la batería: \n"))
cycle_counter = 0
while cycle_counter <= cycles:
    statemachine(0)
    #contador = contador +1 # Necesita múltiplos de 3 por alguna razón1