import pyvisa
import numpy


class Fuente:  # Esta clase describe cada neurona
    def __init__(self, instrument, name=None):
        self.fuente = instrument
        self.name = name  # Nombre para identificar en depuracion

    def encender_canal(self, channel: int):
        self.fuente.write(":OUTPUT CH{:n},ON".format(channel))
        return self.fuente.query(":OUTP? CH{}".format(channel))

    def apagar_canal(self, channel: int):
        self.fuente.write(":OUTPUT CH{:n},OFF".format(channel))
        return self.fuente.query(":OUTP? CH{}".format(channel))

    def aplicar_voltaje_corriente(self, channel: int, voltaje: float, corriente: float):
        self.fuente.write(":APPLY CH{},{},{}".format(channel, voltaje, corriente))
        return self.fuente.query("APPLY? CH{}".format(channel))

    def medir_todo(self, channel: int):
        medicion = self.fuente.query(":MEASURE:ALL?").split(",")
        medicion[-1] = medicion[-1][:-1]
        voltaje = medicion[0]
        corriente = medicion[1]
        potencia = medicion[2]
        return float(voltaje), float(corriente), float(potencia)

class Carga:  # Esta clase describe cada neurona
    def __init__(self, instrument, name=None):
        self.carga = instrument
        self.name = name  # Nombre para identificar en depuracion

    def fijar_funcion(self, funcion: str):
        self.carga.write(":SOUR:FUNC {}".format(funcion))
        return self.carga.query(":SOUR:FUNC?")

    def encender_carga(self):
        self.carga.write(":SOUR:INP:STAT 1")
        return self.carga.query(":SOUR:INP:STAT?")

    def apagar_carga(self):
        self.carga.write(":SOUR:INP:STAT 0")
        return self.carga.query(":SOUR:INP:STAT?")

    def fijar_corriente(self, corriente: float):
        self.carga.write(":SOUR:CURR:LEV:IMM {}".format(corriente))
        return self.carga.query(":SOUR:CURR:LEV:IMM?")

    def fijar_voltaje(self, voltaje: float):
        self.carga.write(":SOUR:VOLT:LEV:IMM {}".format(voltaje))
        return self.carga.query(":SOUR:VOLT:LEV:IMM?")

    def fijar_resistencia(self, resistencia: float):
        self.carga.write(":SOUR:RES:LEV:IMM {}".format(resistencia))
        return self.carga.query(":SOUR:RES:LEV:IMM?")
