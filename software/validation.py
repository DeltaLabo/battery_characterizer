'''
@file Ciclador de baterías
@author Diego Fernández Arias
@author Juan J. Rojas
@date Sep 28 2021
Instituto Tecnológico de Costa Rica
Laboratorio Delta
'''
import pyvisa
import numpy as np
import controller2
import time
from time import sleep
import threading
import pandas as pd
from datetime import datetime
import math
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
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Change of State Button
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Shutdown Button

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
# rm = pyvisa.ResourceMana"Power"ger()
# print(rm.list_resources()) #Retorna los recursos (fuente y carga)
# fuente = rm.open_resource(rm.list_resources()[0])
# #print(fuente.query("*IDN?")) #Verificar orden dela fuente y la carga
# Fuente = controller2.Fuente(fuente, "Diego") #'Diego' parámetro para iterar cuando hay más recursos

#definir estructura
outputCSV = pd.DataFrame(columns = ["Timestamp", "Time", "Voltage", "Current", "Capacity", "Temperature"])


############### Read needed csv files ###############
df = pd.read_csv('/home/pi/Repositories/battery_characterizer/software/prueba_inputs.csv', header=0)
powd = pd.read_csv('/home/pi/Repositories/battery_characterizer/bat_data/bat40.csv')
# modeldf = pd.read_csv('home/pi/Repositories/battery_characterizer/validation/parameters.csv')
########################################################################

#Variables globales que se utilizará dentro de cada función
state = "INIT" 
channel = df.iloc[0,0] #[row,column] channel global variable (Channel 1 by default)
volt = 1.0  
current = 1.0 
power = 1.0 
timer_flag = 0
init_flag = 1
mintowait = 0
prev_state = 0
next_state_flag = 0
cycles = 0
counter = 0
cycle_counter = 0
past_time = datetime.now()
past_curr = 0
capacity = 0
tempC = 0
seconds = 0.0
end_flag = 0
charge_only  = 0
######
# Initial values #
i_0 = 0 # El capacitor se comporta como un corto
z_0 = 0.9835 # Cómo escojo el z según la V de la celda?
v_0 = 4.15 # interpolation() ¿Es igual a ocv en el primer momento?
#dt = 1 # 1s de delta time
Q = 3.20347 # Capacidad en Ah
#n = 1 #Eficiencia (debería variar en carga y descarga)
####
file_date = datetime.now().strftime("%d_%m_%Y_%H_%M")
spi = board.SPI()
cs = digitalio.DigitalInOut(board.D5)
max31855 = adafruit_max31855.MAX31855(spi, cs)

# Cambiar por la generic interpolation #
def sec_interpolation(sec_data, pow_data, sec_in):
    for i in range(len(sec_data)-1):
        if sec_in < sec_data[0]:
            pow_out = pow_data[0]
            break
        if sec_in > sec_data[len(sec_data)-1]:
            pow_out = pow_data[len(sec_data)-1]
            break
        if sec_data[i+1] >= sec_in and sec_data[i] <= sec_in:
            pow_out = pow_data[i] + (pow_data[i+1] - pow_data[i]) * ((sec_in - sec_data[i]) / (sec_data[i+1] - sec_data[i]))
            break
    return pow_out

def interpolation(x_data, y_data, x_in): #Usar con R0, R1, C1
        for i in range(len(x_data)-1):
            if x_in < x_data[0]:
                x_out = y_data[0] #Cambiar por extrapolación
                break
            if x_in > x_data[len(x_data)-1]:
                x_out = y_data[len(x_data)-1] #Cambiar por extrapolación
                break
            if x_data[i+1] >= x_in and x_data[i] <= x_in: #Función de interpolación
                x_out = y_data[i] + (y_data[i+1] - y_data[i]) * ((x_in - x_data[i]) / (x_data[i+1] - x_data[i]))
                break
        return x_out

##########################Se define el diccionario con los estados##################################

#Primero se definirá la base de la máquina de estados (utilizando diccionapandas append csvrios)
def statemachine (entry):
    global state 
    switch = {"INIT" : INIT,
              "CHARGE" : CHARGE,
              "DISCHARGE" : DISCHARGE,
              "END" : END,    
    }        
    func = switch.get(state)
    return func(entry)

#########################Se define la función del estado inicial#####################################

def INIT(entry):
    global state
    global init_flag
    global cycles
    global cycle_counter
    global charge_only
    global seconds
    global int_pow
    global past_time
    
    if cycles == 0:
        print ('''
                '.`                                           `--`                 
                 -``':>rr,                              '<\*!-` `'               
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
   !r\k!.               'hEd~ ^ORxu@@@@@\g@@@@8*GDI-`yER*              ':^\k~`  
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
        
    seconds = float(input("Segundos iniciales: \n"))
    int_pow = sec_interpolation(powd.time, powd.power, seconds)
    
    
    if input("Desea iniciar?: \n") == 'y':
        if int_pow > 0:
            state = "DISCHARGE"
        else:
            state = "CHARGE"
    init_flag = 1
    cycle_counter += 1 
    past_time = datetime.now()
    print("Iniciando...")

def poweroff(channel):
    global state 
    global end_flag
    GPIO.output(17, GPIO.LOW)
    GPIO.output(18, GPIO.LOW)
    Fuente.apagar_canal(channel)
    Carga.apagar_carga()
    print("El sistema se ha apagado")
    state = "END"
    end_flag = 1
GPIO.add_event_detect(22, GPIO.RISING, callback=poweroff, bouncetime=1000)


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
    global past_time
    global past_curr
    global capacity
    global file_date
    global seconds
    global tempC
    global channel
    global cycle_counter
    ######
    global z_0
    global i_0
    global v_0
    global Q
    tiempo_actual = datetime.now()
    deltat = (tiempo_actual - past_time).total_seconds()
    seconds += deltat
    if state == "CHARGE":
        volt,current = Fuente.medir_todo(channel) #Sobreescribe valores V,I,P
        current = -current
        n = 0.932333
    elif state == "DISCHARGE": 
        volt,current = Carga.medir_todo() #Sobreescribe valores V,I,P
        n = 1
    tempC = max31855.temperature #Measure Temp
    
    if tempC >= 60:
            poweroff(channel)
            print("Cuidado! La celda ha excedido la T máxima de operación")
    
    capacity +=  deltat * ((current + past_curr) / 7.2) #documentar porque 7.2 sino se te va a olvidar
    past_time = tiempo_actual
    past_curr = current    
    print("{:09.2f} c = {:02d} V = {:06.3f} I = {:06.3f} Q = {:07.2f} T = {:06.3f}".format(seconds, cycle_counter, volt, current, capacity, tempC))
    
    ##### INICIO DEL MODELO #####
    # Define values for interpolartion #
    # z_data = modeldf.soc.values
    # r0_data = modeldf.r0.values
    # r1_data = modeldf.r1.values
    # c1_data = modeldf.c1.values
    
    # # Definir arrays donde se escribirán las interpolaciones
    # z_r = np.array([z_0])
    # z_p = np.array([0])
    # i_R1 = np.array([0])
    # v = np.array([v_0])
    # # t = np.array([0])
    
    # # Ecuaciones discretizadas #
    # z_r = np.append(z_r, z_0 - ( (deltat*n*current)/Q ) )
    
    # #Modelo
    # ocv_p = volt +  interpolation(z_data, r1_data, z_0)*i_R1 + interpolation(z_data, r0_data, z_0)*current
    # z_p = interpolation(ocv_data, z_data, ocv_p)
    
    # i_R1 = np.append(i_1, math.exp(-deltat / interpolation(z_data, r1_data, z_0) * interpolation(z_data, c1_data, z_0)) * (i_0) + (1 - math.exp(-deltat / (interpolation(z_data, r1_data, z_0) * interpolation(z_data, c1_data, z_0) ) ) ) * current)
    # v = np.append(v, (interpolation(z_data, ocv_data, z_0)) - (interpolation(z_data, r1_data, z_0) * (i_0)) - (interpolation(z_data, r0_data, z_0) * current))
     
    
    
    # z_0 = z_r[-1]
    # i_0 = i_R1[-1]

    ##### FINAL DEL MODELO #####

    # Create csv to write the measurements
    base = "/home/pi/cycler_data/"        
    outputCSV = outputCSV.append({"Timestamp":tiempo_actual,"Time":round(seconds,2), "Voltage":volt, "Current":current, "Capacity":round(capacity,2), "Temperature":tempC}, ignore_index=True)
    filename = base + "validation" + file_date + ".csv"
    outputCSV.iloc[-1:].to_csv(filename, index=False, mode='a', header=False) #Create csv for CHARGE
    
    # # Create csv of the model predicted values
    # model_validation = pd.DataFrame(data={"soc_predicted":z_1, "i_r1":i_1,"v":v})
    # model_validation.to_csv('home/pi/Repositories/battery_characterizer/validation/validation.csv', index=False, mode='a', header=["soc_predicted","i_r1", "v"])
    
#Función para controlar módulo de relés (CH1 y CH2)    
def relay_control(state):
    if state == "CHARGE": #Charge - CH1
        GPIO.output(18,GPIO.LOW)
        time.sleep(0.05)
        GPIO.output(17,GPIO.HIGH)
        time.sleep(0.05)
    elif state == "DISCHARGE": #Discharge - CH2
        GPIO.output(17,GPIO.LOW)
        time.sleep(0.05)
        GPIO.output(18,GPIO.HIGH)
        time.sleep(0.05)
        
################# Se define la función que hará que la batería se cargue ############################
def CHARGE (entry): 
    global powd
    ##
    global prev_state
    global state
    global channel
    global volt
    global current
    global power 
    global capacity
    global init_flag
    global timer_flag
    global next_state_flag #FLAG CAMBIO DE ESTADO
    global past_time
    global seconds

    if init_flag == 1:
        init_flag = 0
        relay_control(state) #CHARGE
        Fuente.toggle_4w() #Activar sensado
        Fuente.aplicar_voltaje_corriente(channel, 4.2, 0)
        Fuente.encender_canal(channel) 
        time.sleep(0.1)
        timer_flag = 1
        
    if timer_flag == 1:
        timer_flag = 0
        medicion()
        int_pow = sec_interpolation(powd.time, powd.power, seconds)
        if int_pow > 0:
            state = "DISCHARGE" 
            Fuente.apagar_canal(channel)
            Fuente.toggle_4w()
            init_flag = 1
        else:          
            int_curr = -int_pow / volt
            Fuente.aplicar_voltaje_corriente(channel, 4.2, int_curr)
    
    if seconds > powd.time[len(powd)-1]:
        state = "END"
        

################# Se define la función que hará que la batería se descargue #########################

#Se setea el recurso de la CARGA para descargar la batería       
def DISCHARGE(entry):
    global prev_state
    global state
    global channel
    global volt
    global current
    global power
    global capacity #Faltó ponerlo para reiniciar la C en descarga
    global init_flag  
    global timer_flag
    global next_state_flag #FLAG CAMBIO DE ESTADO
    global past_time
    global seconds
    global file_date

    ###################################################################
    if init_flag == 1:
        init_flag = 0
        relay_control(state) #CHARGE
        Carga.remote_sense(True) #Activar sensado
        Carga.fijar_corriente(0)
        Carga.encender_carga() #Solo hay un canal (el #1)
        time.sleep(0.1)
        #past_time = datetime.now()
        timer_flag = 1
        
    if timer_flag == 1:
        timer_flag = 0
        medicion()
        int_pow = sec_interpolation(powd.time, powd.power, seconds)
        if int_pow  < 0:
            state = "CHARGE" 
            Carga.apagar_carga()
            init_flag = 1
        else:            
            int_curr = int_pow / volt
            Carga.fijar_corriente(int_curr)
    
    if seconds > powd.time[len(powd)-1]:
        state = "END"
    
            
    ##################################################################
     
################ Se define la función que esperará y retornará al estado inicial ####################
    

####Función final. Apagará canal cuando se hayan cumplido ciclos o reiniciará
def END(entry):
    global cycle_counter
    global end_flag
    global state
    print("Terminó el ciclo...")
    poweroff(channel)
    if cycle_counter >= cycles:
        end_flag = 1
    else:
        state = "INIT" 
    

######################## Programa Principal (loop de la máquina de estado) ########################
t = threading.Timer(1.0, ISR)
t.start() #Después de 5 segundos ejecutará lo de medición ()
while end_flag == 0:
    statemachine("INIT")
print("Terminó el programa")
