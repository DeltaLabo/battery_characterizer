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

GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.OUT) #Pin #17 RPi
GPIO.setup(18,GPIO.OUT) #Pin #18 RPi
##########################Definición 'controller2'##################################
rm = pyvisa.ResourceManager()
print(rm.list_resources())
fuente = rm.open_resource(rm.list_resources()[1])
fuente.write_termination = '\n'
fuente.read_termination = '\n'

#Sección para definir cuáles son los recursos y su orden
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

#Lee valores de entrada como el canal, corriente y voltaje de un archivo csv
df = pd.read_csv("/home/pi/Repositories/battery_characterizer/software/prueba_inputs.csv", header=0)
outputCSV = pd.DataFrame(columns = ["Timestamp", "Voltage", "Current", "Power"])
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

#Primero se definirá la base de la máquina de estados (utilizando diccionapandas append csvrios)
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
    global init_flag
    #df2 = pd.read_csv("C:/Repositories/battery_characterizer/software/prueba_inputs.csv", header=0)
    #tension_fuente = float(input("Digite la tensión a setear en la fuente (V):\n")) #Tensión máxima
    print ("Estado inicial... \n")
    #sleep(2)
    #state = 1
    entry = input("Deberá digitar la letra 'a' para avanzar al siguiente estado: \n")
    #Aquí se definirá la condición para que la máquina pase de una estado a otro
    if entry == "a":
        state = 1
        init_flag = 1
        print("Avanzando al estado de CARGA...")
    else:
        state = 0
        sleep (2)
        print("Se mantiene el estado inicial... Digite la letra correcta")
        sleep(2)

#Interrupt Service Routine
#Executed in response to an event such as a time trigger or a voltage change on a pin
def ISR(): 
    global timer_flag
    t = threading.Timer(1.0, ISR) #ISR se ejecuta cada 1 s mediante threading
    t.start()
    timer_flag = 1 #Al iniciar el hilo, el timer_flag pasa a ser 1

#Thread de medición
def medicion():
    global volt
    global current
    global power
    global outputCSV

    tiempoActual = datetime.now()
    print(tiempoActual,end=',')
    volt,current,power = Fuente.medir_todo(channel) #Sobreescribe valores V,I,P
    print("{:06.3},{:06.3f},{:06.3f}".format(volt, current, power))

    #A continuación, se escriben los valores en un csv
    outputCSV = outputCSV.append({"Timestamp":tiempoActual, "Voltage":volt, "Current":current, "Power":power}, ignore_index=True)
    outputCSV.to_csv("/home/pi/Repositories/battery_characterizer/software/prueba_outputs2.csv")#, columns = ['Voltaje'])#, 'Corriente', 'Potencia'])
#Función para controlar módulo de relés (CH1 y CH2)    
def relay_control(state):
    if state == 1: #Charge - CH1
        GPIO.output(18,GPIO.LOW)
        time.sleep(0.5)
        GPIO.output(17,GPIO.HIGH)
        time.sleep(2)
    elif state == 2: #Discharge - CH2
        GPIO.output(17,GPIO.LOW)
        time.sleep(0.5)
        GPIO.output(18,GPIO.HIGH)
        time.sleep(2)
    elif state == 3: # Wait - Both Low
        GPIO.output(17,GPIO.LOW)
        time.sleep(0.5)
        GPIO.output(18,GPIO.LOW)
        time.sleep(2)

################# Se define la función que hará que la batería se cargue ############################
def CHARGE (entry): 
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
    batt_capacity = df.iloc[0,2] #Eliminarse. Ya está en línea 156

    if init_flag == 1:
        relay_control(1) #CHARGE
        #time.sleep(2)
        set_supply_voltage = df.iloc[0,1] #[fila,columna]
        batt_capacity = df.iloc[0,2] #[fila,columna]
        set_C_rate = batt_capacity * 2 #C rate seteado de 0.5C
        Fuente.aplicar_voltaje_corriente(channel, set_supply_voltage, set_C_rate)
        Fuente.toggle_4w() #Activar sensado
        Fuente.encender_canal(channel) #Solo hay un canal (el #1)
        init_flag = 0 #Cambia el init_flag de 1 a 0
        timer_flag = 0

    if timer_flag == 1:
        timer_flag = 0
        counter +=  1
        if counter >= 1:
            medicion()
            counter = 0
        if current <= (0.45 * batt_capacity) :
            prev_state = 1 #From CHARGE
            state = 3 #To WAIT
            init_flag = 1
            mintowait = 10 #Wait 10 min 
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
    ###################################################################
    if init_flag == 1:
        relay_control(2) #DISCHARGE
        Carga.remote_sense("ON")
        #time.sleep(2)
        #Los siguientes no se definen ya que se continúa con los datos usados para CHARGE
        #set_supply_voltage = df.iloc[0,1] #[fila,columna]
        #batt_capacity = df.iloc[0,2] #[fila,columna]
        init_flag = 0
        
    if timer_flag ==1:
        timer_flag = 0
        counter += 1
        
        
        
    ###################################################################
    
    '''
    print("Se ha llegado al estado de descarga... Se avanzará al estado de espera...")
    prev_state = 2 #From DISCHARGE
    state = 3 #To WAIT
    mintowait = 1 #Wait 1 min
    relay_control(state) #Pasa a State 3. Ambos Low
    
    #Primeras pruebas para descarga mediante la carga electrónica Rigol DL3021
    Carga.encender_carga()
    '''
    

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
    #cycle_counter += 0 #Ciclos aumentan cada vez
    #contador = contador +1 # Necesita múltiplos de 3 por alguna razón1
