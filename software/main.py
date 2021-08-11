import pyvisa
import numpy as np
import matplotlib.pyplot as plt
import math
import controller
import time

InputIsc = 0.5196
InputImp = 0.5029
InputVmp = 2.409
InputVoc = 2.690
InputVoc_Tcomp = 0
InputVmp_Tcomp = 0
InputPcos = 1
InputT = 0


def scalevars(voc_tcomp, vmp_tcomp, pcos, voc, vmp, imp, isc, t):
    sVoc = voc - (t * voc_tcomp)
    sVmp = vmp - (t * vmp_tcomp)
    sImp = pcos * imp
    sIsc = pcos * isc
    return sVoc, sVmp, sImp, sIsc


sVoc, sVmp, sImp, sIsc = scalevars(InputVoc_Tcomp, InputVmp_Tcomp, InputPcos, InputVoc, InputVmp, InputImp, InputIsc,
                                   InputT)


def generate_table(Voc, Vmp, Imp, Isc):
    Rs = (Voc - Vmp) / Imp
    a = (Vmp * (1 + (Rs * Isc) / Voc) + Rs * (Imp - Isc)) / Voc
    N = math.log10(2 - 2 ** a) / math.log10(Imp / Isc)
    i = np.zeros(1024)
    v = np.zeros(1024)
    r = np.zeros(1024)
    for x in range(0, 1024):
        I = (x * Isc) / 1023.0
        V = Voc * math.log10(2 - ((I / Isc) ** N))
        V = V / math.log10(2)
        V = V - Rs * (I - Isc)
        V = V / (1 + ((Rs * Isc) / Voc))
        P = V * I
        v[x] = V
        i[x] = I
        if I == 0:
            r[x] = 10000
        else:
            r[x] = V / I

    return v, i, r


v, i, r = generate_table(sVoc, sVmp, sImp, sIsc)


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

def interpolate_voltage(tableVoltage, tableCurrent, desiredCurrent):
    n = len(tableVoltage)
    vOut = 0
    for j in range(n - 1):
        j += 1
        i = 1024 - j
        if desiredCurrent < tableCurrent[i]:
            # Puede que haya un error, puede que el desired current va en el multiplicador y no en el numerador
            vOut = tableVoltage(i) + (tableVoltage(i + 1) - tableVoltage(i)) * (
                        (desiredCurrent - tableCurrent(i)) / (tableCurrent(i + 1) - tableCurrent(i)))
            break
    return vOut


def interpolate_current(tableVoltage, tableCurrent, desiredVoltage):
    n = len(tableVoltage)
    cOut = 0
    for j in range(n - 1):
        j += 1
        i = 1024 - j
        if desiredVoltage < tableVoltage[i]:
            # Puede que haya un error, puede que el desired voltage va en el multiplicador y no en el numerador
            cOut = tableCurrent(i) + (tableCurrent(i + 1) - tableCurrent(i)) * (
                        (desiredVoltage - tableVoltage(i)) / (tableVoltage(i + 1) - tableVoltage(i)))
            break
    return cOut


# MODOS DE CARGA:
# RES, CURR, VOLT, POW

rm = pyvisa.ResourceManager()
print(rm.list_resources())

# carga = rm.open_resource(rm.list_resources()[0])
fuente = rm.open_resource(rm.list_resources()[0])

print(fuente.query("*IDN?"))

Fuente = controller.Fuente(fuente, "Fuentesita")
# Carga = controller.Carga(carga, "carguita")

# Se va a encender la fuente y poner en CV

print("Extremos: {}V {}A".format(sVoc, sIsc))
print(Fuente.aplicar_voltaje_corriente(1, sVoc, sIsc))
print(Fuente.encender_canal(1))
time.sleep(5)
contador = 0
inicio = time.time()

tiempo = time.time()


# while contador <= 30:
#     voltaje, corriente, potencia = Fuente.medir_todo(1)
#     print("Medición: {}V {}A {}W".format(voltaje, corriente, potencia))
#     # time.sleep(1)
#     resistenciaCarga = voltaje / corriente
#     resistenciaCercana = find_nearest(r, resistenciaCarga)
#     indice = np.where(r == resistenciaCercana)[0][0]
#     voltajeAplicado = round(v[indice], 2)
#     corrienteAplicada = round(i[indice], 2)
#     print("Valores a escribir: {}V. {}A".format(voltajeAplicado, corrienteAplicada))
#     print(Fuente.aplicar_voltaje_corriente(1, voltajeAplicado, corrienteAplicada))
#     # time.sleep(1)
#     contador += 1
#     time.sleep(3)
# elapsado = time.time() - inicio
# print("Tardó: {}".format(elapsado))
# print(Fuente.apagar_canal(1))
