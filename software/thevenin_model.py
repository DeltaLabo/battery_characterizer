'''
Thevenin Equivalent-Circuit Model
given values of R1 and C1, the code is going to iterate to predict, in a discrete time,
the state of charge (z), the difussion-resistor current (ir1) and the output voltage (v)

EQUATIONS OF THE MODEL (Now using number 1 and 3):
1) z(i+1) = z(i) - ((t2 - t1)) * n * I(i) / Q 

2) ir1(i+1) = exp(-(t2 - t1)/R1 * C1) * Ir1(i) + (1-exp(-(t2 - t1)/R1 * C1)) * I(i) 

3) v(i) = ocv(i) - (R1 * Ir1(i)) - (R0 * I(i)) 

'''
#from numpy.core.function_base import linspace
import pandas as pd 
import matplotlib.pyplot as plt 
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import math

##### Definition of interpolation function used with the csv data #####
def ocv_interpolation(soc_data, ocv_data, soc_in):
    ocv_out = 0
    for i in range(len(soc_data)):# soc_in.max()):
        if soc_in <= soc_data[i]:
            if soc_data[i-1] == soc_data[i]:
                ocv_out = ocv_data[i]
                break
            ocv_out = ocv_data[i-1] + (ocv_data[i] - ocv_data[i-1]) * ((soc_in - soc_data[i-1]) / (soc_data[i] - soc_data[i-1]))
            break
    return ocv_out

#Definición de datos de entrada
# df = pd.read_csv('C:/Users/Diego/Desktop/OCV(z).csv')
# df.columns = ['soc','ocv']
# soc_data = df.soc.values #Valores del csv
# ocv_data = df.ocv.values #Valores del csv
############################################
df = pd.read_csv('C:/Repositories/battery_characterizer/coulomb_tests/sococv.csv')
df.columns = ['soc','ocv']
soc_data = df.soc.values #Valores del csv
ocv_data = df.ocv.values #Valores del csv
############################################
# Initial values given in the PDF
v_0 = ocv_interpolation(soc_data,ocv_data, 0.2)
# print(v_0)
z = np.array([0.2]) #Soc en tiempo 0
t = np.array([0]) #Tiempo inicial es 0
v = np.array([v_0]) #Primer valor de V del csv
i = np.array([0]) #Corriente es 0 al inicio
 
# plt.plot(soc_data,ocv_data)
# plt.show()

##### INICIA PRUEBA DE LA INTERPOLACIÓN #####
# soctest = np.linspace(0,1,101)
# ocvtest = np.array([])

# # Probar si la interpolación es correcta #
# for j in range(len(soctest)):
#     ocvtest = np.append(ocvtest, ocv_interpolation(soc_data, ocv_data, soctest[j]))

# plt.figure
# plt.plot(soctest,ocvtest, 'or', soc_data, ocv_data)
# plt.show()
##### TERMINA PRUEBA DE LA INTERPOLACIÓN #####

##### Defining the model´s inputs #####
dfp = pd.read_csv('C:/Users/Diego/Desktop/battery_data/parameters/parameters.csv')
dfp.columns = ['r0', 'r1', 'c1']
r0 = dfp.r0.values
r1 = dfp.r1.values
c1 = dfp.c1.values

charge_n = 0.99 # Charging Efficiency 
disch_n = 1 # Discharging Efficiency 
R0 = 0.085 # Internal Resistance
Q = 3.250 # Capacity 
CC_charge = -1*Q # Charging C Rate. In charge, i < 0 
CV = 4.2
CC_disch = 1*Q # Discharging C Rate. In discharge, i > 0 
eoc = -0.3 # End of Charge 300 mA
eod = 3.2 # End of Discharge 3.2 V
Dt = 0.25/3600 # Discrete integration interval
ind = 0 # Starts in zero and goes on until reaching a condition 

##### CC Charging #####
n = charge_n
while v[ind] < CV:
    i = np.append(i,CC_charge)
    z = np.append(z,z[ind] - (n*Dt*i[ind])/Q)
    v = np.append(v,ocv_interpolation(soc_data,ocv_data,z[ind+1]) - i[ind+1]*R0)
    t = np.append(t,t[ind] + Dt)
    ind += 1

##### CV Charging #####
while i[ind] < eoc:
    v = np.append(v,CV)
    z = np.append(z,z[ind] - (n*Dt*i[ind])/Q)
    i = np.append(i,(ocv_interpolation(soc_data,ocv_data,z[ind+1]) - v[ind+1])/R0)
    # ir2 = math.exp(-Dt / r1 * c1) + (1 - math.exp(-Dt / r1 * c1)) * i
    t = np.append(t,t[ind] + Dt)
    ind += 1

# ##### CC Discharging #####
n = disch_n
while v[ind] > eod:
    i = np.append(i,CC_disch)
    z = np.append(z,z[ind] - (n*Dt*i[ind])/Q)
    v = np.append(v,ocv_interpolation(soc_data,ocv_data,z[ind+1]) - i[ind+1]*R0)
    t = np.append(t,t[ind] + Dt)
    ind += 1

# print(v)
##### Prints and plots #####
plt.plot(t,v)
plt.show()
plt.plot(t,i)
plt.show()
plt.plot(t,z)
plt.show()

# fig2 = go.Figure()
# fig2.add_trace(go.Scatter(x=t, y=v,
#                     mode='lines',
#                     name='Data'))

# fig2.show()
