import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

df = pd.read_csv('discharge_pulse_1.0C.csv')
df.columns = ['time','seconds', 'tag','voltage','current','capacity','temperature']
soc = 1 - df.capacity/df.capacity.max() #Cambiar por la cap máx
df = df.assign(soc=soc.values)

# Creación de las listas vacías
soc = []
r0 = []
r1 = []
c1 = []
resis1 = [] #Prueba
resis2 = [] #Prueba

flag = 0
for i in range(len(df)-1):
    if df.tag[i] == 0 and df.tag[i+1] == 1: #Del rest al pulso
        R01 = (df.voltage[i] - df.voltage[i+1]) / (3.5)
        if flag == 0:
            flag = 1
        else:
            soc.append(df.soc[i])
            R1 = (df.voltage[i] - r11) / (3.5)
            r1.append(R1)
            deltat = (df.seconds[i] - t11) #Tiempo para calcular C
            C1 = (deltat / (5 * R1))
            c1.append(C1)
    if df.tag[i] == 1 and df.tag[i+1] == 0: #Del pulso al rest
        R02 = (df.voltage[i+1] - df.voltage[i]) / (3.5)
        resis2.append(R02)
        resis1.append(R01)
        R0 = (R02 + R01) / 2 #Promedio para calcular R0 (son 26 valores)
        r0.append(R0)
        r11 = df.voltage[i+1] #Voltaje 1 segundo después de soltar el pulso de descarga
        t11 = df.seconds[i+1]
        #R1 = abs((volt_start_pulse - r11) / (curr_start_pulse - df.current[i+1]))
        
# Creación de los arrays a partir de las listas generadas #

SOC = np.array(soc)
R_0 = np.array(r0)
R1p = np.array(r1)
C1p = np.array(c1)
Resis1 = np.array(resis1) #Prueba
Resis2 = np.array(resis2) #Prueba

#Create the new dataset

ds = pd.DataFrame({'Soc': SOC, 'R01': Resis1, 'R02': Resis2, 'R_0': R_0, 'R1': R1p, 'C1': C1p})
# print("Parámetros a 1C:\n", ds)

def r0_interpolation(soc_data, r0_data, soc_in):
    for i in range(len(soc_data)-1):# soc_in.max()):
        if soc_in < soc_data[0]:
            r0_out = r0_data[0]
            # print(" primer valor", r0_out)
            break
        if soc_in > soc_data[len(soc_data)-1]:
            r0_out = r0_data[len(soc_data)-1]
            # print("Último valor:\n", r0_out)
            break
        if soc_data[i+1] >= soc_in and soc_data[i] <= soc_in: #Función de interpolación
            r0_out = r0_data[i] + (r0_data[i+1] - r0_data[i]) * ((soc_in - soc_data[i]) / (soc_data[i+1] - soc_data[i]))
            # print("Entré:\n", r0_out)
            break
        # print(soc_in)
    return r0_out

ds = ds.sort_values(by=['Soc'], ascending=True)
ds = ds.reset_index(drop=True)

soc_data1 = ds.Soc.values
r0_data1 = ds.R02.values #Se tomará R02 como R0
r1_data1 = ds.R1.values
c1_data1 = ds.C1.values
new_soc1 = np.linspace(0,1,101) #100 datapoints chosen
new_r01 = np.array([]) #r0 out
new_r11 = np.array([])
new_c11 = np.array([])

# Calculating R0
for i in range(len(new_soc1)):
    new_r01 = np.append(new_r01, r0_interpolation(soc_data1, r0_data1, new_soc1[i]))
# Plot results #
# plt.figure
# plt.plot(new_soc1, new_r01, '+r', soc_data1, r0_data1)
# plt.title("DataFrame 1")
# plt.xlabel("SOC")
# plt.ylabel("R0")
# plt.show()

# Calculating R1
for i in range(len(new_soc1)):
    new_r11 = np.append(new_r11, r0_interpolation(soc_data1, r1_data1, new_soc1[i]))
# Plot results #
# plt.figure
# plt.plot(new_soc1, new_r11, '+r', soc_data, r1_data)
# plt.title("DataFrame 1")
# plt.xlabel("SOC")
# plt.ylabel("R1")
# plt.show()

# Calculating C1
for i in range(len(new_soc1)):
    new_c11 = np.append(new_c11, r0_interpolation(soc_data1, c1_data1, new_soc1[i]))
# Plot results #
# plt.figure
# plt.plot(new_soc1, new_c1, '+r', soc_data, c1_data)
# plt.title("DataFrame 1")
# plt.xlabel("SOC")
# plt.ylabel("C1")
# plt.show()
###################################################################################
################################ SEGUNDO DATAFRAME ################################
################################################################################### 
df = pd.read_csv('discharge_pulse_1.5C.csv')
df.columns = ['time','seconds', 'tag','voltage','current','capacity','temperature']
soc = 1 - df.capacity/df.capacity.max()
df = df.assign(soc=soc.values)

# Creación de las listas vacías
soc = []
r0 = []
r1 = []
c1 = []
resis1 = [] #Prueba
resis2 = [] #Prueba

flag = 0
for i in range(len(df)-1):
    if df.tag[i] == 0 and df.tag[i+1] == 1: #Del rest al pulso
        R01 = (df.voltage[i] - df.voltage[i+1]) / (5.25)
        if flag == 0:
            flag = 1
        else:
            soc.append(df.soc[i])
            R1 = (df.voltage[i] - r11) / (5.25)
            r1.append(R1)
            deltat = (df.seconds[i] - t11) #Tiempo para calcular C
            C1 = (deltat / (5 * R1))
            c1.append(C1)
    if df.tag[i] == 1 and df.tag[i+1] == 0: #Del pulso al rest
        R02 = (df.voltage[i+1] - df.voltage[i]) / (5.25)
        resis2.append(R02)
        resis1.append(R01)
        R0 = (R02 + R01) / 2 #Promedio para calcular R0 (son 26 valores)
        r0.append(R0)
        r11 = df.voltage[i+1] #Voltaje 1 segundo después de soltar el pulso de descarga
        t11 = df.seconds[i+1]
        #R1 = abs((volt_start_pulse - r11) / (curr_start_pulse - df.current[i+1]))
        
# Creación de los arrays a partir de las listas generadas #

SOC = np.array(soc)
R_0 = np.array(r0)
R1p = np.array(r1)
C1p = np.array(c1)
Resis1 = np.array(resis1) #Prueba
Resis2 = np.array(resis2) #Prueba

#Create the new dataset
ds2 = pd.DataFrame({'Soc': SOC, 'R01': Resis1, 'R02': Resis2, 'R_0': R_0, 'R1': R1p, 'C1': C1p})
#print(ds2)

def r0_interpolation(soc_data, r0_data, soc_in):
    for i in range(len(soc_data)-1):# soc_in.max()):
        if soc_in < soc_data[0]:
            r0_out = r0_data[0]
            # print(" primer valor", r0_out)
            break
        if soc_in > soc_data[len(soc_data)-1]:
            r0_out = r0_data[len(soc_data)-1]
            # print("Último valor:\n", r0_out)
            break
        if soc_data[i+1] >= soc_in and soc_data[i] <= soc_in: #Función de interpolación
            r0_out = r0_data[i] + (r0_data[i+1] - r0_data[i]) * ((soc_in - soc_data[i]) / (soc_data[i+1] - soc_data[i]))
            # print("Entré:\n", r0_out)
            break
        # print(soc_in)
    return r0_out

ds2 = ds2.sort_values(by=['Soc'], ascending=True)
ds2 = ds2.reset_index(drop=True)

soc_data2 = ds2.Soc.values
r0_data2 = ds2.R02.values #Se tomará R02 como R0
r1_data2 = ds2.R1.values
c1_data2 = ds2.C1.values
new_soc2 = np.linspace(0,1,101) #100 datapoints chosen
new_r02 = np.array([]) #r0 out
new_r12 = np.array([])
new_c12 = np.array([])

# Calculating R0
for i in range(len(new_soc2)):
    new_r02 = np.append(new_r02, r0_interpolation(soc_data2, r0_data2, new_soc2[i]))
# Plot results #
# plt.figure
# plt.plot(new_soc2, new_r02, '+r', soc_data2, r0_data2)
# plt.title("DataFrame 2")
# plt.xlabel("SOC")
# plt.ylabel("R0")
# plt.show()

# Calculating R1
for i in range(len(new_soc2)):
    new_r12 = np.append(new_r12, r0_interpolation(soc_data2, r1_data2, new_soc2[i]))
# Plot results #
# plt.figure
# plt.plot(new_soc2, new_r12, '+r', soc_data2, r1_data2)
# plt.title("DataFrame 2")
# plt.xlabel("SOC")
# plt.ylabel("R1")
# plt.show()

# Calculating C1
for i in range(len(new_soc2)):
    new_c12 = np.append(new_c12, r0_interpolation(soc_data2, c1_data2, new_soc2[i]))
# Plot results #
# plt.figure
# plt.plot(new_soc2, new_c12, '+r', soc_data2, c1_data2)
# plt.title("DataFrame 2")
# plt.xlabel("SOC")
# plt.ylabel("C1")
# plt.show()

###################################################################################
################################ TERCER DATAFRAME #################################
###################################################################################

df = pd.read_csv('discharge_pulse_0.5C.csv')
df.columns = ['time','seconds', 'tag','voltage','current','capacity','temperature']
soc = 1 - df.capacity/df.capacity.max()
df = df.assign(soc=soc.values)

# Creación de las listas vacías
soc = []
r0 = []
r1 = []
c1 = []
resis1 = [] #Prueba
resis2 = [] #Prueba

flag = 0
for i in range(len(df)-1):
    if df.tag[i] == 0 and df.tag[i+1] == 1: #Del rest al pulso
        R01 = (df.voltage[i] - df.voltage[i+1]) / (1.75)
        if flag == 0:
            flag = 1
        else:
            soc.append(df.soc[i])
            R1 = (df.voltage[i] - r11) / (1.75)
            r1.append(R1)
            deltat = (df.seconds[i] - t11) #Tiempo para calcular C
            C1 = (deltat / (5 * R1))
            c1.append(C1)
    if df.tag[i] == 1 and df.tag[i+1] == 0: #Del pulso al rest
        R02 = (df.voltage[i+1] - df.voltage[i]) / (1.75)
        resis2.append(R02)
        resis1.append(R01)
        R0 = (R02 + R01) / 2 #Promedio para calcular R0 (son 26 valores)
        r0.append(R0)
        r11 = df.voltage[i+1] #Voltaje 1 segundo después de soltar el pulso de descarga
        t11 = df.seconds[i+1]
        #R1 = abs((volt_start_pulse - r11) / (curr_start_pulse - df.current[i+1]))
        
# Creación de los arrays a partir de las listas generadas #

SOC = np.array(soc)
R_0 = np.array(r0)
R1p = np.array(r1)
C1p = np.array(c1)
Resis1 = np.array(resis1) #Prueba
Resis2 = np.array(resis2) #Prueba

#Create the new dataset

ds3 = pd.DataFrame({'Soc': SOC, 'R01': Resis1, 'R02': Resis2, 'R_0': R_0, 'R1': R1p, 'C1': C1p})
#print("Parámetros a 0.5C:\n", ds4)

def r0_interpolation(soc_data, r0_data, soc_in):
    for i in range(len(soc_data)-1):# soc_in.max()):
        if soc_in < soc_data[0]:
            r0_out = r0_data[0]
            # print(" primer valor", r0_out)
            break
        if soc_in > soc_data[len(soc_data)-1]:
            r0_out = r0_data[len(soc_data)-1]
            # print("Último valor:\n", r0_out)
            break
        if soc_data[i+1] >= soc_in and soc_data[i] <= soc_in: #Función de interpolación
            r0_out = r0_data[i] + (r0_data[i+1] - r0_data[i]) * ((soc_in - soc_data[i]) / (soc_data[i+1] - soc_data[i]))
            # print("Entré:\n", r0_out)
            break
        # print(soc_in)
    return r0_out

ds3 = ds3.sort_values(by=['Soc'], ascending=True)
ds3 = ds3.reset_index(drop=True)

soc_data3 = ds3.Soc.values
r0_data3 = ds3.R02.values #Se tomará R02 como R0
r1_data3 = ds3.R1.values
c1_data3 = ds3.C1.values
new_soc3 = np.linspace(0,1,101) #100 datapoints chosen
new_r03 = np.array([]) #r0 out
new_r13 = np.array([])
new_c13 = np.array([])

# Calculating R0
for i in range(len(new_soc3)):
    new_r03 = np.append(new_r03, r0_interpolation(soc_data3, r0_data3, new_soc3[i]))
# Plot results #
# plt.figure
# plt.plot(new_soc3, new_r03, '+r', soc_data3, r0_data3)
# plt.title("DataFrame 3")
# plt.xlabel("SOC")
# plt.ylabel("R0")
# plt.show()

# Calculating R1
for i in range(len(new_soc3)):
    new_r13 = np.append(new_r13, r0_interpolation(soc_data3, r1_data3, new_soc3[i]))
# Plot results #
# plt.figure
# plt.plot(new_soc1, new_r13, '+r', soc_data3, r1_data3)
# plt.title("DataFrame 3")
# plt.xlabel("SOC")
# plt.ylabel("R1")
# plt.show()

# Calculating C1
for i in range(len(new_soc3)):
    new_c13 = np.append(new_c13, r0_interpolation(soc_data3, c1_data3, new_soc3[i]))
# Plot results #
# plt.figure
# plt.plot(new_soc1, new_c13, '+r', soc_data3, c1_data3)
# plt.title("DataFrame 3")
# plt.xlabel("SOC")
# plt.ylabel("C1")
# plt.show()

r0df = pd.DataFrame(data={"r01":new_r01, "r02":new_r02, "r03":new_r03})
r1df = pd.DataFrame(data={"r11":new_r11, "r12":new_r12, "r13":new_r13})
c1df = pd.DataFrame(data={"c11":new_c11, "c12":new_c12, "c13":new_c13})
# Plot results #
# print(r0df)
# print(r1df)
# print(c1df)

###################################################################################
################################ PROMEDIO ENTRE DFs ###############################
###################################################################################
new_soc = np.linspace(0,1,101)
# print(r0df)
r0 = (r0df.r01.values + r0df.r02.values + r0df.r03.values) / 3
r1 = (r1df.r11.values + r1df.r12.values + r1df.r13.values) / 3
c1 = (c1df.c11.values + c1df.c12.values + c1df.c13.values) / 3
parameters = pd.DataFrame(data={"r0":r0,"r1":r1, "c1":c1})
parameters.to_csv('C:/Users/Diego/Desktop/battery_data/parameters/parameters.csv', index=False, mode='w', header=["r0", "r1", "c1"])

plt.figure
plt.plot(new_soc1, new_r01, label="1C")
plt.plot(new_soc2, new_r02, label="1.5C")
plt.plot(new_soc3, new_r03, label="0.5C")
plt.plot(new_soc,r0, label="Promedio")
plt.legend(loc="upper right")
plt.xlabel("SOC")
plt.ylabel("R0")
plt.show()

plt.figure
plt.plot(new_soc1, new_r11, label="1C")
plt.plot(new_soc2, new_r12, label="1.5C")
plt.plot(new_soc3, new_r13, label="0.5C")
plt.plot(new_soc,r1, label="Promedio")
plt.legend(loc="upper right")
plt.xlabel("SOC")
plt.ylabel("R1")
plt.show()

plt.figure
plt.plot(new_soc1, new_c11, label="1C")
plt.plot(new_soc2, new_c12, label="1.5C")
plt.plot(new_soc3, new_c13, label="0.5C")
plt.plot(new_soc,c1, label="Promedio")
plt.legend(loc="upper right")
plt.xlabel("SOC")
plt.ylabel("C1")
plt.show()