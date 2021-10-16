'''
Thevenin Equivalent-Circuit Model
From  some given values of R1 and C1, the code is going to iterate to predict, in a discrete time,
the state of charge (z), the difussion-resistor current (ir1) and the output voltage (v)

EQUATIONS OF THE MODEL (Now using number 1 and 3):
1) z(i+1) = z(i) - ((t2 - t1)) * n * I(i) / Q 

2) ir1(i+1) = exp(-(t2 - t1)/R1 * C1) * Ir1(i) + (1-exp(-(t2 - t1)/R1 * C1)) * I(i) 

3) v(i) = ocv(i) - (R1 * Ir1(i)) - (R0 * I(i)) 

'''
from numpy.core.function_base import linspace
import pandas as pd 
import matplotlib.pyplot as plt 
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

df = pd.read_csv('C:/Users/Diego/Desktop/OCV(z).csv')
df.columns = ['SOC','OCV']
##### Definition of interpolation and iteration functions used with the csv data #####
# def ocv_interpolation(soc_data, volt_data, soc_in):
#     for i in range(len(soc_data)-1):# soc_in.max()):
#         soc_out = volt_data[i-1] + (volt_data[i] - volt_data[i-1]) * (soc_in - soc_data[i-1]) / (soc_data[i] - soc_data[i-1])
#         break
#     return soc_out

def ocv_interpolation(soc_data, volt_data, soc_in):
    for i in range(len(soc_data)-1):# soc_in.max()):
        soc_out = volt_data[i-1] + (volt_data[i] - volt_data[i-1]) * (soc_in - soc_data[i-1]) / (soc_data[i] - soc_data[i-1])
        break
    return soc_out



# def soc_iteration(soc_in, meas_curr):   
#     for i in range(len(soc_in)):
#         if i == 0:
#             soc_out = 0.25 - (0.25 * 1 * meas_curr / 3.25)
#             #print(soc_out)
#         else:
#             soc_out = soc_in[i-1] - (0.25 * 1 * meas_curr / 3.25)#Q
#             #print("este es", soc_in[i-1], soc_in[i], soc_in[i+1])
#             #print(soc_out)
#             break
#     return soc_out

# predicted_soc = np.zeros(len(df.SOC))
# soc_in = df.SOC.values
# meas_curr = 3.25 #constante

z = np.array([0.25])
t = np.array([0])
v = np.array([3.73]) #?
i = np.array([-3.25])
soc = df.SOC.values
ocv = df.OCV.values

soctest = linspace(0.2,1,1000)
ocvtest = np.zeros(len(soctest))
print(len(soctest))
print(len(ocvtest))

for j in range(len(soctest)):
    ocvtest[j] = ocv_interpolation(soc,ocv,soctest[j])
    
plt.figure
plt.plot(soctest,ocvtest)
plt.show()

#testtocsv = pd.DataFrame(data={"I":I, "z":z, "v":v, "t":t})
#testtocsv.to_csv('C:/Users/Diego/Desktop/csvtest.csv', index=False)

##### Defining the model´s inputs #####
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
    v = np.append(v,ocv_interpolation(soc,ocv,z[ind]) - i[ind]*R0)
    t = np.append(t,t[ind] + Dt)
    ind += 1

##### CV Charging #####
# while i[ind] < CC_charge:
#     n = charge_n
#     i = np.append(i,CC_charge)
#     z = np.append(z,z[ind] - (n*Dt*i[ind])/Q)
#     v = np.append(v,ocv_interpolation(soc,ocv,z[ind]) - i[ind]*R0)
#     t = np.append(t,t[ind] + Dt)
#     ind += 1

# ##### CC Discharging #####
# while i[ind] < CC_disch:
#     n = 
#     i = np.append(i,CC_charge)
#     z = np.append(z,z[ind] - (n*Dt*i[ind])/Q)
#     v = np.append(v,ocv_interpolation(soc,ocv,z[ind]) - i[ind]*R0)
#     t = np.append(t,t[ind] + Dt)
#     ind += 1

##### Prints and plots #####
print(ind)
print(v[1])
plt.plot(t, v)
plt.show()


# for i in range(len(soc_in)):
#     print("AQUI:", len(soc_in))#, type(soc_in))
#     predicted_soc[i] = soc_iteration(soc_in, meas_curr)
#     print(type(soc_in), len(soc_in))
#     #soc_in[i] = predicted_soc[i-1]

# newdf = pd.DataFrame()
# newdf = newdf.assign(SOC=predicted_soc)

# fig2 = go.Figure()
# fig2.add_trace(go.Scatter(x=df.SOC, y=df.OCV,
#                     mode='lines',
#                     name='Data'))
# fig2.add_trace(go.Scatter(x=newdf.predicted_soc, y=df.OCV,
#                     mode='markers',
#                     name='Iteration'))

# fig2.show()

# #z(1) = z(0) - ((t2 - t1)) * n * I(i) / Q
# soc = df.SOC - ((1 * 0.25 ) / 3.25) * 3.25 

# df = df.assign(soc=soc.values)

# fig = px.scatter(df, x="soc", y="OCV")
# fig.show()
# fig = go.Figure()
# fig.add_trace(go.Scatter(x=df.soc, y=df.OCV,
#                      mode='marks',
#                      name='Interpolation'))
# fig.add_trace(go.Scatter(x=df.SOC, y=df.OCV,
#                      mode='lines',
#                      name='data'))