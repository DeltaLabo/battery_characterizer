'''
Ciclador de baterías############
Diego Fernández Arias
Instituto Tecnológico de Costa Rica
Laboratorio Delta
'''
import pyvisa
import controller2
import time
from time import sleep
import threading
import pandas as pd
from datetime import datetime
import RPi.GPIO as GPIO
import board 
import digitalio
import adafruit_max31855

#GPIO.cleanup() pasarlo al final
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.OUT) #Pin #17 RPi
GPIO.setup(18,GPIO.OUT) #Pin #18 RPi
GPIO.output(17, GPIO.LOW)
GPIO.output(18,GPIO.LOW)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Push Button
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Interruptor

##########################Definición 'controller2'##################################
#rm = pyvisa.ResourceManager()
#print(rm.list_resources())
#fuente = rm.open_resource(rm.list_resources()[1])
#fuente.write_termination = '\n'
#fuente.read_termination = '\n'

rm = pyvisa.ResourceManager()
print(rm.list_resources()[1])

for i in range(3):
    if rm.list_resources()[i].find("DL3A21") > 0:
        carga = rm.open_resource(rm.list_resources()[i]) 
        print("Carga DL3A21 encontrada")
        print(carga.query("*IDN?"))
    elif rm.list_resources()[i].find("SPD13") > 0:
        fuente = rm.open_resource(rm.list_resources()[i])
        print("Fuente SPD1305X encontrada")
        #print("Fuente SPD1305X encontrada")
    #else:
        #print("No se ha detectado la fuente o la carga")

Fuente = controller2.Fuente(fuente, "SPD1305", tipoFuente = True) # SPD parámetro para iterar cuando hay más recursos
Carga = controller2.Carga(carga, "DL3021")
#############################################################################################
# rm = pyvisa.ResourceManager()
# print(rm.list_resources()) #Retorna los recursos (fuente y carga)
# fuente = rm.open_resource(rm.list_resources()[0])
# #print(fuente.query("*IDN?")) #Verificar orden dela fuente y la carga
# Fuente = controller2.Fuente(fuente, "Diego") #'Diego' parámetro para iterar cuando hay más recursos

#Lee valores de entrada como el canal, corriente y voltaje de un archivo csv
df = pd.read_csv("/home/pi/Repositories/battery_characterizer/software/prueba_inputs.csv", header=0)
outputCSV = pd.DataFrame(columns = ["Timestamp", "Voltage", "Current", "Power", "Temperature"])

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
next_state_flag = 0
cycles = 1
cycle_counter = 0
spi = board.SPI()
cs = digitalio.DigitalInOut(board.D5)
max31855 = adafruit_max31855.MAX31855(spi, cs)


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
    global cycles
    
    print ('''
                       '.`                                     `--`                 
                 -``':>rr,                             '<\*!-` `'               
                ^-      -\kx"                       '*yT!       r               
                x:         ~sKr`                  :uMx.         y               
                rY           !Idv'              ^KZv`          _w               
                -O:            :KRu_         `*qd(`            z*               
                 TH`             *MRu-     `*5Eu'             (O`               
                 -dy              `x66L'  =PDK:              !Rx                
                  rEY               _jDdvzEdr`              ,d3`                
                   TDY                rEED3'               ,Zd_                 
                   `hDY              ^ZEw5Ey-             ,ZR~                  
                    .GD}`          -wDZx:ruEd*           :ZE(                   
                   `.^6Eyrvx}uVwXhmdDyL#\gO?MDHIkyu}Lx)*rdDu`                   
           `_~rLymMRDEO6EDqjkycukEDOv3@@\g@#vyDD5VVkjsKREEEDRZ3wY?>:'           
      _^YwXkTxr<!,-``  -PE5,   ,MDI(B@@@\g@@@KrdRi`   iEE( ``-,:>rv}yIk}*,`     
   !r\r!.               'hEd~ ^ORxu@@@@@\g@@@@8*GDI-`yER*              ':^\r~`  
 -!.                     `yDRIEO*Z@@@@@@\g@@@@@#*yDMHEd=                    `!, 
 `                         YEDq^Q@@@@@@@*Z@@@@@@@YvRDd,                       ``
 _!`                      _GEy)#@@@#O33Z#gP3H8@@@@Z^ZEY`                    `:" 
  `~r(~_`                :ZEx}@@RPPMB@@@@@@@@$PPMB@Q^KDV`              `-=)r^'  
     `:(uwzuxr<!_.`     :d6*(P3GB@@@@@@@@@@@@@@@#OPPX:kDw`   `'_:~*v}wkcv=`     
          `,>\}zGOEOMHmjdEzr(zhsmsIIhssmmmmshIXImmssT*\dD5PMdE65Xlv^:'          
                  `.,!}DEu}uyzhKHqZEDD6ddddRDDOHKsjyu}xvmDM!-`                  
                     _ZRr          ^ZEM= `YREw-         `XEc                    
                    `3Rr            'TREyqEM^            `jEv                   
                    uE)               ^REDP'              `hR!                  
                   <Ex               *ZEIMEX,              'P5`                 
                  `Zc              =HDX: `rZEu-             -Z}                 
                  \H`            ,zEh=     `?ZOx`            ~O-                
                  P=           .uRz!         `r5q*`           u\                
                 -I          -idT,             `*3G*`         ,V                
                 -\        =yI*`                  _xKi_        x                
                  !     ,?Yr-                        :xi*-    '"                
                   ``-"=:`                              '!!_.`                  
    ''')
    cycles = int(input("Digite la cantidad de ciclos de carga/descarga de la batería: \n"))
    #entry = input("Deberá digitar la letra 'a' para avanzar al siguiente estado: \n")
    #Aquí se definirá la condición para que la máquina pase de una estado a otro
    if cycles > 0:
        state = 1
        init_flag = 1
        print("Avanzando al estado de CARGA...")
    else:
        state = 0
        time.sleep (2)
        print("Se mantiene el estado inicial... Digite la cantidad de ciclos")

def next_state(channel):
    global next_state_flag
    next_state_flag = 1 
GPIO.add_event_detect(24, GPIO.RISING, callback=next_state, bouncetime=1000) 

def reiniciar(channel):
    global state 
    GPIO.output(17, GPIO.LOW)
    GPIO.output(18, GPIO.LOW)
    Fuente.apagar_canal(channel)
    Carga.apagar_canal()
    print("Se reinicia el sistema")
    time.sleep(10)
    #state = 0
GPIO.add_event_detect(23, GPIO.RISING, callback=reiniciar, bouncetime=1000)


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
    global state
    global outputCSV
    global max31855

    tiempoActual = datetime.now()
    print(tiempoActual,end=',')
    if state == 1:
        volt,current = Fuente.medir_todo(channel) #Sobreescribe valores V,I,P
        tempC = max31855.temperature
    elif state == 2: 
        volt,current = Carga.medir_todo() #Sobreescribe valores V,I,P
        tempC = max31855.temperature
    print("{:06.3f},{:06.3f},{:06.3f}".format(volt, current,tempC))
    

    #Valores escritos en un csv
    outputCSV = outputCSV.append({"Timestamp":tiempoActual, "Voltage":volt, "Current":current, "Power":power, "Temperature":tempC}, ignore_index=True)
    outputCSV.to_csv("/home/pi/Repositories/battery_characterizer/software/prueba_outputs2.csv")
    
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
    global next_state_flag #FLAG CAMBIO DE ESTADO
    batt_capacity = df.iloc[0,2] #Eliminarse. Ya está en línea 156

    if init_flag == 1:
        relay_control(1) #CHARGE
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
        if current <= (0.45 * batt_capacity) or next_state_flag == 1: #FLAG CAMBIO DE ESTADO CHARGE:
            Fuente.apagar_canal(channel)
            if next_state_flag  == 1:
                next_state_flag = 0
            prev_state = 1 #From CHARGE
            state = 3 #To WAIT
            init_flag = 1
            mintowait = 0.1 #Wait 10 min 

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
    global next_state_flag #FLAG CAMBIO DE ESTADO
    ###################################################################
    if init_flag == 1:
        relay_control(2) #DISCHARGE
        Carga.remote_sense("ON")
        Carga.fijar_corriente(3.5) #Descargando a 1C
        Carga.encender_carga()
        init_flag = 0
        timer_flag = 0 #Revisar
        
    if timer_flag == 1:
        timer_flag = 0
        counter += 1
        if counter >= 1:
            medicion()
            counter = 0
        if volt <= (2.55) or next_state_flag == 1: #FLAG CAMBIO DE ESTADO CHARGE:
            Carga.apagar_carga()
            if next_state_flag == 1:
                next_state_flag = 0
            prev_state = 2 #From DISCHARGE
            state = 3 #To WAIT
            init_flag = 1
            mintowait = 10 # Wait 10 min    
    ##################################################################
     
################ Se define la función que esperará y retornará al estado inicial ####################

def WAIT(entry):
    global state
    global mintowait
    global timer_flag
    global init_flag
    global counter
    global prev_state
    global next_state_flag #FLAG CAMBIO DE ESTADO
    
    relay_control(state)
    
    if timer_flag == 1: #FLAG CAMBIO DE ESTADO
        timer_flag = 0
        counter += 1
        print(counter) #, end='\r')
        if counter >= (mintowait * 60) or next_state_flag == 1:
            if next_state_flag == 1:
                next_state_flag = 0
            if prev_state == 1: #CHARGE:
                state = 2 #DISCHARGE
                print("Estado DISCHARGE") 
            elif prev_state == 2: #DISCHARGE:
                state = 6 #END
                print("Estado END")    
    

####Función final. Apagará canal cuando se hayan cumplido ciclos o reiniciará
def END(entry):
    global cycle_counter
    print("Terminó el ciclo...")
    state = 0 
    cycle_counter += 1

######################## Programa Principal (loop de la máquina de estado) ########################
t = threading.Timer(1.0, ISR)
t.start() #Después de 5 segundos ejecutará lo de medición ()
while cycles > cycle_counter:
    statemachine(0)
    #cycle_counter += 0 #Ciclos aumentan cada vez
    #contador = contador +1 # Necesita múltiplos de 3 por alguna razón1
print("Terminó el programa")
