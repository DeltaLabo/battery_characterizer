from numpy.core.function_base import linspace
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

val = pd.read_csv('final_validation.csv')

val.columns = ['timestamp','time','voltage','current', 'capacity', 'temperature']
#newi = -bat40.ibat/2 #Cambiar a - al terminar la validación
#bat40 = bat40.assign(ibat=newi.values)
#val.current = val.current
#bat40.iloc[0,1:4] = bat40.iloc[2,1:4]
#bat40.iloc[1,1:4] = bat40.iloc[2,1:4]

print(val.head())

def interpolation(x, y, x_in): #Usar con R0, R1, C1
        for i in range(len(x)-1):
            if x_in < x[0]:
                y_out = y[0] #Cambiar por extrapolación
                break
            if x_in > x[len(x)-1]:
                y_out = y[len(x)-1] #Cambiar por extrapolación
                break
            if x_in >= x[i] and x_in <= x[i+1]: #Función de interpolación
                y_out = y[i] + (y[i+1] - y[i]) * ((x_in - x[i]) / (x[i+1] - x[i]))
                break
        return y_out

def inv_interpolation(x, y, y_in): #Usar con R0, R1, C1
        for i in range(len(y)-1):
            if y_in < y[0]:
                x_out = x[0] #Cambiar por extrapolación
                break
            if y_in > y[len(y)-1]:
                x_out = x[len(y)-1] #Cambiar por extrapolación
                break
            if y_in >= y[i] and y_in <= y[i+1]: #Función de interpolación
                x_out = ((y_in-y[i+1])/(y[i]-y[i+1]))*x[i] + ((y_in-y[i])/(y[i+1]-y[i]))*x[i+1]
                break
        return x_out


modeldf = pd.read_csv('../validation/parameters.csv')
ocvdf = pd.read_csv('../soc_test/sococv.csv')


z_data = modeldf.soc.values
r0_data = modeldf.r0.values
r1_data = modeldf.r1.values
c1_data = modeldf.c1.values
ocv_data = ocvdf.OCV.values


# ###############PRUEBA##################
# ocv_inv = linspace(2.5,4.5,100)
# soc_inv = np.array([0])


# for i in range(len(ocv_inv)-1):
#     soc_inv = np.append(soc_inv, inv_interpolation(z_data,ocv_data,ocv_inv[i]))

# plt.plot(ocv_inv, soc_inv)
# plt.show()
# ###############PRUEBA##################

#i_R1_0 = 0
z_0_p = 0.77
z_0_r = 0.77
v_0 = 4.0
deltat = 1

########## PREDECIR SOC #############

z_p = np.array([z_0_p])
z_r = np.array([z_0_r])
ocv_p = np.array([v_0])
iR1k = 0
#i_R1 = np.array([i_R1_0])
v = np.array([v_0])
n = 1
Q = 3.436 * 3600 #ampere-seconds
alpha = 1
beta = 0.001

for i in range(len(val)-1):
    #### PARAMETERS #######
    vk = val.voltage[i]
    ik = val.current[i]
    zk = z_p[-1]
    R0 = interpolation(z_data, r0_data, zk)
    R1 = interpolation(z_data, r1_data, zk)
    C1 = interpolation(z_data, c1_data, zk)
    
    tau = R1 * C1
    ####### REAL ##########
    z_r = np.append( z_r, ( z_r[-1] - ( n * deltat * ik / Q ) ) )
    ####### PREDICHO ##########
    ocv_new = vk + ik * R0 + iR1k * R1
    ocv_p = np.append( ocv_p, ( ocv_p[-1] + alpha * ( ocv_new - ocv_p[-1] ) ) )   
    #print("V= ", bat40.voltage[i])
    # print("I= ", bat40.current[i])
    # print("OCV_p= ", ocv_p)
    # print("SOC_p=", inv_interpolation(z_data, ocv_data, ocv_p))
    z_new = inv_interpolation(z_data, ocv_data, ocv_p[i])
    z_p = np.append(z_p, z_p[-1] + beta * ( z_new - z_p[-1] ) ) #predicho
    iR1k = np.exp( -deltat / tau ) * iR1k + ( 1 - np.exp( -deltat / tau ) ) * ik
    #iR1 = np.append(iR1, ( np.exp( -deltat / (R1 * C1) ) ) * iR1k + ( 1 - np.exp( -deltat / (R1 * C1) ) ) * bat40.current[i])
	


plt.figure(figsize=[15,5])
plt.plot(val.time, z_r, label='real')
plt.plot(val.time, z_p, label="predicted")
plt.ylim((0.6,1))
plt.xlabel('time(s)', fontsize=15)
plt.ylabel('SOC', fontsize=15)
plt.legend()
plt.show()

from sklearn.metrics import r2_score

print('R2:', end='') 
print(r2_score(z_r, z_p))

from sklearn.metrics import mean_absolute_percentage_error

# print('MAPE:', end='') 
# print(mean_absolute_percentage_error(z_r, z_p)*100,'%')

###Predecir v

# #i_R1_0 = 0
# z_0_p = 0.77
# v_0 = 4.0
# deltat = 1

# z_p = np.array([z_0_p])
# v_p = np.array([])
# v_r = np.array([])
# iR1k = 0
# #i_R1 = np.array([i_R1_0])

# n = 1
# Q = 3.436 * 3600 #ampere-seconds


# ########## PREDECIR VOLT #############

# for i in range(len(val)-1):
#     #### PARAMETERS #######
#     #vk = bat40.voltage[i]
#     ik = val.current[i]
#     zk = z_p[-1]
#     R0 = interpolation(z_data, r0_data, zk)
#     R1 = interpolation(z_data, r1_data, zk)
#     C1 = interpolation(z_data, c1_data, zk) 
    
#     tau = R1 * C1
#     ####### PREDICCION ##########
#     ocv_p = interpolation(z_data, ocv_data, zk)
#     vk = ocv_p - ik * R0 - iR1k * R1 
#     v_p = np.append(v_p, vk)
#     v_r = np.append(v_r,val.voltage[i])
    
    
#     if ik > 0:
#         n = 1
#     else:
#         n = 0.93

#     z_p = np.append( z_p, ( zk - ( n * deltat * ik / Q ) ) )      
#     iR1k = np.exp( -deltat / tau ) * iR1k + ( 1 - np.exp( -deltat / tau ) ) * ik

# ocv_p = interpolation(z_data, ocv_data, zk)
# vk = ocv_p - ik * R0 #- iR1k * R1 
# v_p = np.append(v_p, vk)
# v_r = np.append(v_r, val.voltage[i])


# print('R2volt:', end='') 
# print(r2_score(v_r, v_p))

# print('MAPE:', end='') 
# print(mean_absolute_percentage_error(z_r, z_p)*100,'%')


# # bat40.to_csv('bat40.csv', index=False)
# # bat35.to_csv('bat35.csv', index=False)

# plt.figure(figsize=[15,5])
# #plt.plot(bat40.time, bat40.current/bat40.current.max(), label='normalized current')
# #plt.plot(bat40.time, bat40.voltage/bat40.voltage.max(), label='normalized voltage')
# plt.plot(val.time, v_r, label='real')
# plt.plot(val.time, v_p, label="predicted")
# plt.ylim((3.8,4.1))
# plt.xlabel('time(s)', fontsize=15)
# plt.ylabel('power(W)', fontsize=15)
# plt.legend()
# plt.show()

# # plt.figure(figsize=[15,5])
# # plt.plot(bat35.time, bat35.power, label='power')
# # plt.xlabel('time(s)', fontsize=15)
# # plt.ylabel('power(W)', fontsize=15)
# # plt.legend()
# # plt.show()



