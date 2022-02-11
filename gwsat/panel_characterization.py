'''
Programa para 
caracterización de panel solar a utilizar en el GWSat
'''
import pyvisa
import controller2 #Solo se va a usar la Electronic Load
import RPi.GPIO as GPIO
import threading
import time

### Resetear los GPIOs ###

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.OUT) #Pin #17 RPi
GPIO.setup(18,GPIO.OUT) #Pin #18 RPi
GPIO.output(17, GPIO.LOW)
GPIO.output(18, GPIO.LOW)
##########################

### Resource-set-up communication ###

rm = pyvisa.ResourceManager()
print("Este es el número 1:\n", rm.list_resources()[1])
carga = rm.list_resources()[1]
print("La carga está dada por el recurso", carga)


# for i in range(6):
    # if rm.list_resources()[i].find("DL3A21") > 0:
        # carga = rm.open_resource(rm.list_resources()[i]) 
        # print("Carga DL3A21 encontrada")
        # print(carga.query("*IDN?"))
    # #else:
    # #    print("Electronic load not found!")

Carga = controller2.Carga(carga, "DL3A21")

# Carga.remote_sense(True)
#####################################

### Condiciones iniciales ###
GPIO.output(18, GPIO.HIGH)
Carga.remote_sense(False)
Carga.set_mode("VOLT") #CV ON
Carga.set_volt_range(15) #Range @ 15 V
Carga.encender_carga()

#############################

### Global Variables ###
timer_flag = 0
init_flag = 1
volt = 0
current = 0
set_volt = 0

########################

### Interrupt Service Routine ###
# def isr():
    # global timer_flag
    # t = threading.Timer(1.0, isr)
    # t.start()
    # timer_flag = 1 #Do the measurement every second
#################################

### Measure the I&V variables every given time ###
def measure():
    global volt
    global current
    
    volt, current = Carga.medir_todo()
    print("V = {:06.3f} I = {:06.3f}".format(volt, current))
##############################################

### Solar panel discharge to load ###
def pan_disch():
    global timer_flag
    global init_flag
    global volt
    global set_volt #Empieza en cero
    #global new_volt # Tiene que ser global?
    
    volt, current = Carga.medir_todo()
    while volt <= 22:
        Carga.fijar_voltaje(set_volt)
        measure()
        new_volt = (set_volt + (0.5))
        set_volt = new_volt

    # if init_flag == 1:
        # init_flag = 0
        # time.sleep(2)
        # GPIO.output(18, GPIO.HIGH)
        # Carga.remote_sense(True)
        # Carga.set_mode("VOLT") #CV ON
        # Carga.set_volt_range(15) #Range @ 15 V
        # Carga.encender_carga()
        # timer_flag = 1

    # if timer_flag == 1:
        # timer_flag = 0
        # Carga.fijar_voltaje(set_volt)
        # #time.sleep(1)
        # if volt <= 22: #Solar panel parameter
            # measure()
            # new_volt = (set_volt + (0.5)) # 0.5V increments
            # set_volt = new_volt
            
        # else:
            # # t.cancel() #Cancela el thread
# #This will only work if the timer is still in its waiting stage
            # GPIO.output(18, GPIO.LOW)
            # Carga.apagar_carga()
            # print("Se ha sobrepasado el voltaje límite!")

#####################################

### Main Program ###
# t = threading.Timer(1.0, isr)
# t.start()
pan_disch()
####################

'''
Falta encender el sensado, range de 15 V (pag 47), 
setear en CV (pag 38)
y encender la carga
'''
