'''
@file Ciclador de baterías
@author Diego Fernández Arias
@author Juan J. Rojas
@date Sep 28 2021
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
import sec_interp_test

#GPIO.cleanup() pasarlo al final
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.OUT) #Pin #17 RPi
GPIO.setup(18,GPIO.OUT) #Pin #18 RPi
GPIO.output(17, GPIO.LOW)
GPIO.output(18,GPIO.LOW)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Change of State 
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Shutdown Button

############### Communication with Resources ###############
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

Fuente = controller2.Fuente(fuente, "SPD1305", tipoFuente = True)
########################################################################

############### Read needed csv files ###############
df = pd.read_csv("/home/pi/Repositories/battery_characterizer/software/prueba_inputs.csv", header=0)
powd = pd.read_csv("/home/pi/Repositories/battery_characterizer/bat_data/bat40.csv", header=0)
powd.columns = ['time', 'current', 'voltage', 'power']
########################################################################

############### Create csv files ###############
outputCSV = pd.DataFrame(columns = ["Timestamp", "Time", "Voltage", "Current", "Capacity", "Temperature"])
########################################################################

# Global Variables Definition
mode = "discharge" # Se toma que se iniciará en descarga 
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
seconds = 0
end_flag = 0
charge_only  = 0
file_date = datetime.now().strftime("%d_%m_%Y_%H_%M")
spi = board.SPI()
cs = digitalio.DigitalInOut(board.D5)
max31855 = adafruit_max31855.MAX31855(spi, cs)

def poweroff(channel):
    global state 
    global end_flag
    GPIO.output(17, GPIO.LOW)
    GPIO.output(18, GPIO.LOW)
    Fuente.apagar_canal(channel)
    Carga.apagar_carga()
    print("La validación ha finalizado...")
    state = "END"
    end_flag = 1
GPIO.add_event_detect(22, GPIO.RISING, callback=poweroff, bouncetime=1000)


#Interrupt Service Routine
#Executed in response to an event such as a time trigger or a voltage change on a pin
def ISR():
    global timer_flag
    t = threading.Timer(1.0, ISR) #ISR se ejecuta cada 1 s mediante threading
    t.start()
    timer_flag = 1 #Flag se levanta para realizar medición

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
    tiempo_actual = datetime.now()
    deltat = (tiempo_actual - past_time).total_seconds()
    seconds += deltat
    if mode == "charge":
        volt,current = Fuente.medir_todo(channel) #Sobreescribe valores V,I,P
    elif mode == "discharge": 
        volt,current = Carga.medir_todo() #Sobreescribe valores V,I,P
    tempC = max31855.temperature #Measure Temp
    
    if tempC >= 50:
            poweroff(channel)
            print("Cuidado! La celda ha excedido la T máxima de operación")
    
    capacity +=  deltat * ((current + past_curr) / 7.2) #documentar porque 7.2 sino se te va a olvidar. Ya se me olvidó jajaja
    past_time = tiempo_actual
    past_curr = current    
    print("{:09.2f} c = {:02d} V = {:06.3f} I = {:06.3f} Q = {:07.2f} T = {:06.3f}".format(seconds, cycle_counter, volt, current, capacity, tempC))
    base = "/home/pi/cycler_data/"
    
    outputCSV = outputCSV.append({"Timestamp":tiempo_actual,"Time":round(seconds,2), "Voltage":volt, "Current":current, "Capacity":round(capacity,2), "Temperature":tempC}, ignore_index=True)
    filename = base + "validation_data" + file_date + ".csv"
    outputCSV.iloc[-1:].to_csv(filename, index=False, mode='a', header=False) 

    
#Función para controlar módulo de relés (CH1 y CH2)    
def relay_control(mode):
    if mode == "charge": #Charge - CH1
        GPIO.output(18,GPIO.LOW)
        #time.sleep(0.5)
        GPIO.output(17,GPIO.HIGH)
    elif mode == "discharge": #Discharge - CH2
        GPIO.output(17,GPIO.LOW)
        #time.sleep(0.5)
        GPIO.output(18,GPIO.HIGH)


################# Se define la función que hará que la batería se cargue ############################
def set_value (entry): 
    global seconds
    global channel
    global volt
    global current
    global power 
    global capacity
    global df
    global init_flag
    global timer_flag
    global mintowait
    global next_state_flag #FLAG CAMBIO DE ESTADO
    global past_time
    global seconds
    global file_date

    # if init_flag == 1:
        # relay_control(state) #CHARGE
        # set_supply_voltage = df.iloc[0,1] #[fila,columna]
        # batt_capacity = df.iloc[0,2] #[fila,columna]
        # set_C_rate = (0.25) #C rate seteado de C/35
        # Fuente.aplicar_voltaje_corriente(channel, set_supply_voltage, set_C_rate)
        # Fuente.toggle_4w() #Activar sensado
        # Fuente.encender_canal(channel) #Solo hay un canal (el #1)
        # init_flag = 0 #Cambia el init_flag de 1 a 0
        # past_time = datetime.now()
        # file_date = datetime.now().strftime("%d_%m_%Y_%H_%M")
        # timer_flag = 0
        # capacity = 0
        # seconds = 0
        
    if timer_flag == 1:
        timer_flag = 0
        medicion()
        
        if seconds != bat40.time:
            sec_interpolation()
        
        
        
        if current <= (0.098) or next_state_flag == 1: #FLAG CAMBIO DE ESTADO CHARGE:
            Fuente.apagar_canal(channel)
            Fuente.toggle_4w()
            if next_state_flag  == 1:
                next_state_flag = 0
            prev_state = "CHARGE" #From CHARGE
            state = "WAIT" #To WAIT
            init_flag = 1
            mintowait = 4 #Wait 10 min


################# Se define la función que hará que la batería se cargue ############################
def CHARGE (entry): 
    global prev_state
    global state
    global channel
    global volt
    global current
    global power 
    global capacity
    global df
    global init_flag
    global timer_flag
    global mintowait
    global next_state_flag #FLAG CAMBIO DE ESTADO
    global past_time
    global seconds
    global file_date
    batt_capacity = df.iloc[0,2] #Eliminarse. Ya está en línea 156

    if init_flag == 1:
        relay_control(state) #CHARGE
        set_supply_voltage = df.iloc[0,1] #[fila,columna]
        batt_capacity = df.iloc[0,2] #[fila,columna]
        set_C_rate = (0.25) #C rate seteado de C/35
        Fuente.aplicar_voltaje_corriente(channel, set_supply_voltage, set_C_rate)
        Fuente.toggle_4w() #Activar sensado
        Fuente.encender_canal(channel) #Solo hay un canal (el #1)
        init_flag = 0 #Cambia el init_flag de 1 a 0
        past_time = datetime.now()
        file_date = datetime.now().strftime("%d_%m_%Y_%H_%M")
        timer_flag = 0
        capacity = 0
        seconds = 0
        
    if timer_flag == 1:
        timer_flag = 0
        medicion()
        if current <= (0.098) or next_state_flag == 1: #FLAG CAMBIO DE ESTADO CHARGE:
            Fuente.apagar_canal(channel)
            Fuente.toggle_4w()
            if next_state_flag  == 1:
                next_state_flag = 0
            prev_state = "CHARGE" #From CHARGE
            state = "WAIT" #To WAIT
            init_flag = 1
            mintowait = 4 #Wait 10 min
        

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
    global df
    global init_flag  
    global timer_flag
    global mintowait
    global next_state_flag #FLAG CAMBIO DE ESTADO
    global past_time
    global seconds
    global file_date

    ###################################################################
    if init_flag == 1:
        relay_control(state) #DISCHARGE
        Carga.remote_sense(True)
        Carga.fijar_corriente(0.1) #Descargando a C/35
        Carga.encender_carga()
        past_time = datetime.now()
        file_date = datetime.now().strftime("%d_%m_%Y_%H_%M")
        timer_flag = 0 #Revisar
        capacity = 0
        seconds = 0
        init_flag = 0

    if timer_flag == 1:
        timer_flag = 0
        medicion()
        if volt <= (2.5) or next_state_flag == 1: #FLAG CAMBIO DE ESTADO CHARGE:
            Carga.apagar_carga()
            if next_state_flag == 1:
                next_state_flag = 0
            prev_state = "DISCHARGE" #From DISCHARGE
            state = "WAIT" #To WAIT
            init_flag = 1
            mintowait = 4 # Wait 10 min.1 s = 2.5 s
            
    ##################################################################
     
################ Se define la función que esperará y retornará al estado inicial ####################
def WAIT(entry):
    global state
    global mintowait
    global timer_flag
    global init_flag
    global prev_state
    global next_state_flag #FLAG CAMBIO DE ESTADO
    global counter
    global charge_only
    if init_flag == 1:
        relay_control(state)
        counter = 0 
        init_flag = 0
    if timer_flag == 1: #FLAG CAMBIO DE ESTADO
        counter += 1
        timer_flag = 0
        print(counter) #, end='\r')
    if counter >= (mintowait * 60) or next_state_flag == 1:
        if next_state_flag == 1:
            next_state_flag = 0
        if prev_state == "CHARGE": #CHARGE:
            if charge_only == 0:
                state = "DISCHARGE" #DISCHARGE
                print("Estado DISCHARGE") 
            else:
                state = "END" #END
                print("Estado END")  
        elif prev_state == "DISCHARGE": #DISCHARGE:
            state = "END" #END
            print("Estado END")  
        init_flag = 1
    

####Función final. Apagará canal cuando se hayan cumplido ciclos o reiniciará
def END(entry):
    global cycle_counter
    global end_flag
    global state
    print("Terminó el ciclo...")
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
