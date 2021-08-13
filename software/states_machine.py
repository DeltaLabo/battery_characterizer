# -*- coding: utf-8 -*-
"""
Created on Fri Jul 30 10:07:51 2021

@author: Diego Fernández Arias
Instituto Tecnológico de Costa Rica
"""
from time import sleep 
import controller
#Se define una variable global que se utilizará dentro de cada función
#Se define para no tener que estar definiéndolo de nuevo en cada estado
state = 'i'
#Primero se definirá la base de la máquina de estados (utilizando diccionarios)

def statemachine (entry):
    global state #Se llama a la variable global que se definió 
    #afuera de las funciones 
    switch = {'i': INIT,
              0 : CHARGE,
              1: DISCHARGE,
              2: WAIT,        
    }         #switch será el diccionario donde se guarden los cuatro estados
    func = switch.get(state)
    return func(entry)

#Se define cada uno de los estados (inicial, carga, descarga y espera)

def INIT(entry):
    global state
    print ("Estado inicial... \n")
    sleep(2)
    entry = input("Deberá digitar la palabra 'avanzar' para avanzar al siguiente estado: \n")
    #Aquí se definirá la condición para que la máquina pase de una estado a otro
    if entry == "avanzar":
        state = 0
        print("Avanzando al estado de CARGA...")
    else:
        state = 'i'
        sleep (2)
        print("Se mantiene el estado inicial...")
        sleep(2)
        
def CHARGE (entry):
    global state
    sleep(2)
    current = int(input("Digite el valor de la corriente (mA): \n"))
    
    #Tres opciones: >=, ==, <=
    if current == 100:
        state = 1
        print("Avanzando al estado de DESCARGA...")
        
    elif current > 100:
        state = 0
        print("El valor de la corriente es mayor a 100 mA...")
        sleep(2)
# Aquí podría definirse qué es la acción que se llevará a cabo si la corriente
# es MAYOR a la que se defina (100 mA, en este caso) 
       
    elif current < 100:
        state = 0
        print ("El valor de la corriente todavía es menor a 100 mA...")
        sleep(2)
# Aquí podría definirse qué es la acción que se llevará a cabo si la corriente
# es MENOR a la que se defina (100 mA, en este caso)   
        
def DISCHARGE(entry):
    global state
    sleep(2)
    voltage = float(input("Digite el valor medido de la tensión de la batería (V): \n"))
    #Tres opciones: -=, ==, +=
    if voltage == 2.5:
        state = 2
        print("Avanzando al estado de ESPERA...")
# A partir de aquí, el circuito debe abrirse y no puede seguirse descargando
# Orden al programa de dejar de descargar       
    elif voltage > 2.5:
        state = 1
        print ("El valor de tensión en la batería es mayor al mínimo para avanzar...")
        sleep(2)

    elif voltage < 2.5:
        state = 1
        print("¡ALERTA! El valor de tensión de la batería es menor al mínimo... ")
        sleep(2)
# Este es un estado crítico. La tensión de la celda no puede bajar 
# más allá de su mínimo.
def WAIT(entry):
    global state
    sleep (10)
    state = 0
    print("Volviendo al estadio inicial...")
        
# Programa Principal
while True:
    statemachine('i')
        