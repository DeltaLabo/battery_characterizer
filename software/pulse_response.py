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

Fuente = controller2.Fuente(fuente, "SPD1305", tipoFuente = True)
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
outputCSV = pd.DataFrame(columns = ["Timestamp", "Time", "Voltage", "Current", "Temperature"])

#Global variables definition 
state = "INIT"
init_flag = 1
timer_flag = 0
counter = 0
batt_capacity = 3500 #mAh
seconds = 0
past_time = 0
volt = 0
current = 0
tempC = 0
end_flag = 0
curr_volt = 0
past_volt = 0
deltavolt = 0
volt_counter = 0
prev_state = 0
past_time = datetime.now()
file_date = datetime.now().strftime("%d_%m_%Y_%H_%M")
spi = board.SPI #Estas pueden cambiarse para usar
cs = digitalio.DigitalInOut(board.D5) #RPi.GPIO
max31855 = adafruit_max31855.MAX31855(spi,cs)

def statemachine ():
    global state
    switch = {"INIT" : INIT,
              "PULSE" : PULSE,
              "REST" : REST,
              "END" : END,    
    }
    func = switch.get(state)
    return func() 


def ISR(): #Interrupt Service Routine
    global timer_flag
    t = threading.Timer(1.00, ISR)
    t.start()
    timer_flag = 1 #timer_flag pasa a 1(flag up)

def poweroff():
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
    global seconds
    global volt
    global current
    global tempC
    global max31855
    global outputCSV
    global file_date
    global past_volt
    global deltavolt
    global curr_volt
    global volt_counter

    tiempo_actual = datetime.now()
    deltat = (tiempo_actual - past_time).total_seconds()
    seconds += deltat
    volt,current = Carga.medir_todo()
    tempC = max31855.temperature 

    if tempC >= 60:
        poweroff()
        print("CUIDADO! La celda ha excedido para Tmáx")

    ####################################################
    if state == "REST":
        curr_volt += volt #Current value of the voltage 
        volt_counter += 1 #Este counter puede ser diferente al ya definido?
    #past_volt también se está acumulando?
        if volt_counter == 60:
            deltavolt = (curr_volt - past_volt) * 100 / past_volt
            volt_counter = 0
            past_volt = curr_volt
            curr_volt = 0

    ####################################################
    past_time = tiempo_actual
    print("s = {:09.2f} V = {:06.3f} I = {:06.3f} T = {:06.3f}".format(seconds, volt, current, tempC))
    #Añadir valores constantement en el csv
    outputCSV = outputCSV.append({"Timestamp":tiempo_actual,"Time":round(seconds,2), "Voltage":volt, "Current":current, "Temperature":tempC}, ignore_index=True)
    filename = 'C:/Repositories/battery_characterizer/coulomb_tests' + 'discharge_pulse' + file_date + '.csv'
    outputCSV.iloc[-1:].to_csv(filename, index=False, mode='a', header=False)

def relay_control(state):
    if state == "PULSE":
        GPIO.output(18, GPIO.HIGH)
        #time.sleep(0.5)
    elif state == "REST":
        GPIO.output(18, GPIO.LOW)
        #time.sleep(0.5)

def INIT():
    global timer_flag
    global counter
    global state
    global init_flag
    
    print("Pronto empezará el pulso de descarga...")
    if timer_flag == 1:
        timer_flag = 0
        counter += 1
        print(counter)
        if counter >= (2 * 60): #Wait approx 2 min to start discharge
            state = "PULSE"
            init_flag = 1
            print("Avanzando al pulso de descarga...")
    

def PULSE():
    global state
    global batt_capacity
    global timer_flag
    global counter
    global volt
    global file_date
    global seconds
    global init_flag
    global past_time
    global timer_flag
    global prev_state
    
    if init_flag == 1:
        relay_control(state)
        Carga.remote_sense("ON")
        Carga.fijar_corriente(batt_capacity * 0.25) #0.25C
        Carga.encender_carga()
        init_flag = 0
        past_time = datetime.now()
        file_date = datetime.now().strftime("%d_%m_%Y_%H_%M")
        timer_flag = 0
        seconds = 0
       
    if timer_flag == 1:
        timer_flag = 0
        counter += 1
        if counter >= 1:
            measure()
            counter = 0
        if counter <= (10 * 60): #Discharge pulse of 10 min
            print("Vmin = {:06.3f} t = {:09.2f}".format(volt, seconds))
            Carga.apagar_carga()
            prev_state = "PULSE"
            state = "REST"
            #Esperar 1 s para medir

        if volt <= (2.5):
            Carga.fijar_voltaje(2.5)
#Lo siguiente debería ir en un función aparte?
            if current <= (0.1):
                Carga.apagar_carga()
                state = "END"

def REST():
    global timer_flag
    global counter
    global seconds
    global state
    global init_flag
    global past_volt
    global deltavolt
    global curr_volt
    global volt_counter

    #seconds = 0
    curr_volt += volt #Current value of the voltage 
    volt_counter += 1 #Este counter puede ser diferente al ya definido?
    #past_volt también se está acumulando?
    
    if timer_flag == 1:
        timer_flag = 0
        counter += 1
        print(counter)
        if counter >=1: # Empieza a medir 1s después de entrar a REST
            measure()
            counter = 0
            ###############################
            # if volt_counter == 60:
            #     deltavolt = (curr_volt - past_volt) * 100 / past_volt
            #     volt_counter = 0
            #     past_volt = curr_volt
            #     curr_volt = 0
            ###############################
            if deltavolt <= 1:
                print("Iniciando próximo pulso de descarga")
                state = "PULSE"
                init_flag = 1

def END():
    global end_flag
    print("Se ha descarga la batería por completo...")
    end_flag = 1

#################### MAIN PROGRAM ####################
t = threading.Timer(1.0, ISR)
t.start()
while end_flag == 0:
    statemachine("INIT")
print("Terminó el programa...")