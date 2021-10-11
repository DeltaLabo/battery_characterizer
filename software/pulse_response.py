'''
Code to send and measure a pulse response in a discharge process of a 18650 li-ion battery
Diego Fernández Arias
Laboratorio Delta

'''
'''
def counter
when counter = 2 min
Carga.encender_carga(CC@0.25C x 10 min)
Carga.apagar_carga()
Efecto lineal temrinará 1 segundo después de soltar el pulso (apagar canal)
Empezar a medir % de diferencia entre medición y medición
    Cuando haya un % de diferencia entre dos mediciones de voltaje, se comienza el próximo pulso de descarga

Al final, pasar a CV para que la I llega a 100 mA

Agregar las mismas funciones de poweroff, next_state del código original
'''
#import controller2 Ponerlos en las mismas carpetas
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
Carga = controller2.Carga(Carga, "DL3021")

#Ser RPi outputs
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(18,GPIO.OUT) #CH2 para descarga
GPIO.output(18,GPIO.LOW)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Shutdown Button

#Definición archivo csv de las mediciones
outputCSV = pd.DataFrame(columns = ["Timestamp", "Time", "Voltage", "Current", "Temperature"])

#Definición de variables globales
state = "INIT"
init_flag = 0
timer_flag = 0
counter = 0
mintowait = 0
batt_capacity = 3500 #mAh
seconds = 0
past_time = 0
volt = 0
current = 0
tempC = 0
end_flag = 0
past_volt = 0
deltavolt = 0
voltdiff = 0
past_time = datetime.now()
file_date = datetime.now().strftime("%d_%m_%Y_%H_%M")
spi = board.SPI #Estas pueden cambiarse para usar
cs = digitalio.DigitalInOut(board.D5)#RPi.GPIO
max31855 = adafruit_max31855.MAX31855(spi,cs)

def statemachine ():
    global state
    switch = {"INIT" : INIT,
              "PULSE" : PULSE,
              "WAIT" : WAIT,
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

    tiempo_actual = datetime.now()
    deltat = (tiempo_actual - past_time).total_seconds()
    seconds += deltat
    volt,current = Carga.medir_todo()
    tempC = max31855.temperature 

    if tempC >= 60:
        poweroff()
        print("CUIDADO! La celda ha excedido para Tmáx")

    deltavolt = (volt - past_volt)
    voltdiff = (((deltavolt) * 100) / past_volt)
    past_volt = volt

    past_time = tiempo_actual
    print("s = {:09.2f} V = {:06.3f} I = {:06.3f} T = {:06.3f} %V = {:06.3f}".format(seconds, volt, current, tempC, voltdiff))
    #Añadir valores constantement en el csv
    outputCSV = outputCSV.append({"Timestamp":tiempo_actual,"Time":round(seconds,2), "Voltage":volt, "Current":current, "Temperature":tempC, "Voltage difference":voltdiff}, ignore_index=True)
    filename = 'C:/Repositories/battery_characterizer/coulomb_tests' + 'discharge_pulse' + file_date + '.csv'
    outputCSV.iloc[-1:].to_csv(filename, index=False, mode='a', header=False)

def relay_control(state):
    if state == "PULSE":
        GPIO.output(18, GPIO.HIGH)
        #time.sleep(0.5)
    elif state == "WAIT":
        GPIO.output(18, GPIO.LOW)
        #time.sleep(0.5)

def INIT():
    global timer_flag
    global counter
    global state
    global init_flag
    

    if timer_flag == 1:
        timer_flag = 0
        counter += 1
        print(counter)
        if counter >= (2 * 60): #Wait 2 min to start discharge
            state = "PULSE"
            init_flag = 1
            print("Avanzando al pulso de descarga...")
    

def PULSE():
    global state
    global mintowait
    global batt_capacity
    global timer_flag
    global counter
    global volt
    global file_date
    global seconds
    global init_flag
    global past_time
    global timer_flag
    
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
            Carga.apagar_carga()
            state = "WAIT"
            #Esperar 1 s para medir

        if volt <= (2.5):
            Carga.fijar_voltaje(2.5)
#Lo siguiente podría ir en un función aparte
            if current <= (0.1):
                Carga.apagar_carga()
                state = "END"

def WAIT():
    global timer_flag
    global counter
    global seconds
    global voltdiff
    global state
    global init_flag
    
    #seconds = 0
    
    if timer_flag == 1:
        timer_flag = 0
        counter += 1
        print(counter)
        print(voltdiff)
        if voltdiff <= 5:
            print("Iniciando próximo pulso de descarga")
            state = "PULSE"
            init_flag = 1

        # if counter >= (2 * 60):
        #     discharge_pulse


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