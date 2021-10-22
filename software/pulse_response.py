'''
Code to send and measure a pulse response in a discharge process of a 18650 li-ion battery
Diego Fernández Arias
Laboratorio Delta

'''
import controller2 #Ponerlos en las mismas carpetas
import pyvisa
import pandas as pd
from datetime import date, datetime
import threading
import RPi.GPIO as GPIO
import board 
import digitalio
import adafruit_max31855

rm = pyvisa.ResourceManager()

for i in range(3):
    if rm.list_resources()[i].find("DL3A21") > 0:
        carga = rm.open_resource(rm.list_resources()[i]) 
        print("Carga DL3A21 encontrada")
        print(carga.query("*IDN?"))
    elif rm.list_resources()[i].find("SPD13") > 0:
        fuente = rm.open_resource(rm.list_resources()[i])
        print("Fuente SPD1305X encontrada")

#Fuente = controller2.Fuente(fuente, "SPD1305", tipoFuente = True)
Carga = controller2.Carga(carga, "DL3021")

#Ser RPi outputs
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(18,GPIO.OUT) #CH2 para descarga
GPIO.output(18,GPIO.LOW)
GPIO.setup(17,GPIO.OUT) #Cierra CH1 por si estuviera activado
GPIO.output(17,GPIO.LOW)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Shutdown Button

#Definición archivo csv de las mediciones
outputCSV = pd.DataFrame(columns = ["Timestamp", "Time", "Tag", "Voltage", "Current", "Capacity", "Temperature"])

#Global variables definition 
state = "INIT"
init_flag = 1
timer_flag = 0
counter = 0
batt_capacity = 3.5 #Ah
seconds = 0
past_time = 0
volt = 0
current = 0
tempC = 0
end_flag = 0
curr_volt = 0
past_volt = 0
volt_counter = 0
prev_state = 0
tag = 0
capacity = 0
past_curr = 0
past_time = datetime.now()
file_date = datetime.now().strftime("%d_%m_%Y_%H_%M")
spi = board.SPI() #Estas pueden cambiarse para usar
cs = digitalio.DigitalInOut(board.D5) #RPi.GPIO
max31855 = adafruit_max31855.MAX31855(spi,cs)

def statemachine(entry):
    global state
    switch = {"INIT" : INIT,
              "PULSE" : PULSE,
              "REST" : REST,
              "END" : END,    
    }
    func = switch.get(state)
    return func(entry) 


def ISR(): #Interrupt Service Routine
    global timer_flag
    t = threading.Timer(1.00, ISR)
    t.start()
    timer_flag = 1 #timer_flag pasa a 1(flag up)

def poweroff(channel):
    global state
    global end_flag
    GPIO.output(17, GPIO.LOW)
    GPIO.output(18, GPIO.LOW)
    Carga.apagar_carga()
    print("El sistema se ha detenido...")
    state = "END"
    end_flag = 1
GPIO.add_event_detect(22, GPIO.RISING, callback=poweroff, bouncetime=1000)

def measure():
    global past_time
    global past_curr
    global capacity
    global seconds
    global volt
    global current
    global tempC
    global max31855
    global outputCSV
    global file_date
    global past_volt
    global curr_volt
    global counter
    global tag
    
    tiempo_actual = datetime.now()
    deltat = (tiempo_actual - past_time).total_seconds()
    seconds += deltat
    volt,current = Carga.medir_todo()
    tempC = max31855.temperature 

    if tempC >= 60:
        poweroff()
        print("CUIDADO! La celda ha excedido para Tmáx")
        
    capacity +=  deltat * ((current + past_curr) / 7.2) #documentar porque 7.2 sino se te va a olvidar
    past_time = tiempo_actual
    past_curr = current  
    print("s = {:09.2f} tag = {:1d} V = {:06.3f} I = {:06.3f} Q = {:07.2f} T = {:06.3f}".format(seconds, tag, volt, current, capacity, tempC))
    #Añadir valores constantement en el csv
    outputCSV = outputCSV.append({"Timestamp":tiempo_actual,"Time":round(seconds,2), "Tag":tag, "Voltage":volt, "Current":current, "Capacity":capacity, "Temperature":tempC}, ignore_index=True)
    filename = '/home/pi/pulse_discharges/' + 'discharge_pulse' + file_date + '.csv' #For Windows: C:/Repositories/battery_characterizer/coulomb_tests/
    outputCSV.iloc[-1:].to_csv(filename, index=False, mode='a', header=False)

def relay_control(state):
    if state == "PULSE":
        GPIO.output(18, GPIO.HIGH)
        #time.sleep(0.5)
    elif state == "REST":
        GPIO.output(18, GPIO.LOW)
        #time.sleep(0.5)

def INIT(entry):
    global timer_flag
    global counter
    global state
    global init_flag
    global past_time
    global volt
    global past_volt
    
    d = str(input("¿Desea iniciar el proceso de pulsos de descarga a la batería? (y/n): \n"))
    if d == "y":
        print("Inicio...")
        state = "REST"
        init_flag = 1
        past_time = datetime.now()
        measure()
        past_volt = volt
    else:
        print("El proceso no comenzará. Si desea iniciar, digite 'y'.")
        state = "INIT"

def PULSE(entry):
    global state
    global batt_capacity
    global timer_flag
    global counter
    global volt
    global past_volt
    global current
    global file_date
    global seconds
    global init_flag
    global past_time
    global timer_flag
    global prev_state
    global seconds
    global tag
    dt = 120 #Discharge time (in seconds)
    
    if init_flag == 1:
        relay_control(state)
        Carga.remote_sense("ON")
        Carga.fijar_corriente(batt_capacity * 0.5) #DISCHARGE @0.5C
        Carga.encender_carga()
        #past_time = datetime.now()
        #file_date = datetime.now().strftime("%d_%m_%Y_%H_%M")
        init_flag = 0
        #timer_flag = 0
        counter = 0
        timer_flag = 0
        tag = 1
        #seconds = 0 Interesa ver la gráfica desde que se empieza en el INIT
       
    if timer_flag == 1:
        timer_flag = 0
        counter += 1 
        measure()
        if volt > 2.5:
            if counter >= dt:
                Carga.apagar_carga()
                prev_state = "PULSE"
                state = "REST"
                init_flag = 1
                past_volt = volt #Para la primera medición, past_volt = último valor medido de volt
                counter = 0
                tag = 0
        else:
            #Carga.fijar_voltaje(2.5)
#Lo siguiente debería ir en un función aparte?
            #if current <= (0.1):
            Carga.apagar_carga()
            state = "END"

def REST(entry):
    global timer_flag
    global counter
    global seconds
    global state
    global init_flag
    global past_volt
    global curr_volt
    global volt
    global tag

    if timer_flag == 1:
        timer_flag = 0
        counter += 1
        measure()
        curr_volt += volt # current_voltage is accumulating in the REST state
        #print("Debería acumularse:", curr_volt)
        if counter == 60: #Compare last 60 values 
            curr_volt = curr_volt / 60 
            print("curr_volt:", curr_volt)
            print("past_volt:", past_volt)
            deltavolt = abs(((curr_volt - past_volt) * 100) / past_volt)
            print("DeltaVolt:", deltavolt)
            counter = 0
            past_volt = curr_volt
            curr_volt = 0
            if deltavolt <= 0.01:
                print("Iniciando próximo pulso de descarga")
                state = "PULSE"
                init_flag = 1

def END(entry):
    global end_flag
    print("Se ha descarga la batería por completo...")
    end_flag = 1

#################### MAIN LOOP ####################
t = threading.Timer(1.0, ISR)
t.start()
while end_flag == 0:
    statemachine("INIT")
print("Terminó el programa...")
