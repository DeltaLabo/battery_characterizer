import pandas as pd
#from pandas.io.parsers import read_csv
# import plotly.express as px
# import plotly.graph_objects as go
import matplotlib.pyplot as plt
import numpy as np

datapoints = 101

def dsoc_interpolation(soc_data, volt_data, soc_in):
    for i in range(len(soc_data)-1):# soc_in.max()):
        if soc_in == 0:
            volt_out = volt_data[0]
            break
        if soc_in == 1:
            volt_out = volt_data[len(soc_data)-1]
            break
        if soc_data[i+1] >= soc_in and soc_data[i] < soc_in: #Función de interpolación
            volt_out = volt_data[i] + (volt_data[i+1] - volt_data[i]) * (soc_in - soc_data[i]) / (soc_data[i+1] - soc_data[i])
            break
    return volt_out


#################################################################################
################################# PARA DESCARGA #################################
#################################################################################

dsd = pd.read_csv('discharge_data09_10_2021_22_55.csv')#Upload csv
dsd.columns = ['time','seconds','voltage','current','capacity','temperature']

# Limpiando los datos PARA DESCARGA
dsd.capacity = dsd.capacity - dsd.capacity.min()
dsd.seconds = dsd.seconds - dsd.seconds.min()
socd = 1 - dsd.capacity/dsd.capacity.max()
dsd = dsd.assign(soc=socd.values)
dsd = dsd.sort_values(by=['seconds'], ascending=False)
dsd = dsd.reset_index(drop=True)
# print(dsd.head())

#c_eff = dsd.capacity.max() / dsd.capacity.max()
#dsd.capacity = c_eff*dsd.capacity
#soc = 1 - dsc.capacity/dsc.capacity.max()
#dsd = dsd.assign(soc=soc.values)

volt_datad = dsd.voltage.values
soc_datad = dsd.soc.values

new_socd = np.linspace(0,1,datapoints) #1000 divisions of the new x axis (SoC)
new_voltd = np.zeros(len(new_socd))
for i in range(len(new_socd)):
    new_voltd[i] = dsoc_interpolation(soc_datad, volt_datad, new_socd[i])

newdsd = pd.DataFrame() #New empty DataFrame
newdsd = newdsd.assign(soc=new_socd)
newdsd = newdsd.assign(voltage=new_voltd)

##################################################################################
################################### PARA CARGA ###################################
##################################################################################

dsc = pd.read_csv('charge_data11_10_2021_23_55.csv')#Upload csv
dsc.columns = ['time','seconds','voltage','current','capacity','temperature']

# Limpiando los datos PARA CARGA
dsc.capacity = dsc.capacity - dsc.capacity.min()
dsc.seconds = dsc.seconds - dsc.seconds.min()
# Coulumb eff
c_eff = dsd.capacity.max() / dsc.capacity.max()
print(c_eff)

dsc.capacity = c_eff*dsc.capacity
socc = dsc.capacity/dsc.capacity.max()
dsc = dsc.assign(soc=socc.values)

##Prueba
print("Carga: ", dsc.capacity.max())
print("Descarga: ", dsd.capacity.max())

volt_datac = dsc.voltage.values
soc_datac = dsc.soc.values

new_socc = np.linspace(0,1,datapoints) #1000 divisions of the new x axis (SoC)
new_voltc = np.zeros(len(new_socc))
for i in range(len(new_socc)):
    new_voltc[i] = dsoc_interpolation(soc_datac, volt_datac, new_socc[i])

newdsc = pd.DataFrame() #New empty DataFrame
newdsc = newdsc.assign(soc=new_socc)
newdsc = newdsc.assign(voltage=new_voltc)

soc = np.linspace(0,1,datapoints)
ocv = (newdsc.voltage.values + newdsd.voltage.values)/2
sococv = pd.DataFrame(data={"soc":soc,"ocv": ocv})
sococv.to_csv('sococv.csv',index=False, mode='w', header=["SOC", "OCV"])

R0 = (newdsc.voltage.values - sococv.ocv.values)/0.1 #calcular el R para todos los puntos R=dV/i
socR0 = pd.DataFrame(data={"soc":soc,"R0":R0})
socR0.to_csv('socR0.csv', index=False, mode='w', header=["SOC", "R0"])

# fig1 = px.scatter(socR0, x="soc", y="R0")
# fig1.show()

# fig2 = go.Figure()
# fig2.add_trace(go.Scatter(x=dsd.soc, y=dsd.voltage,
                    # mode='lines',
                    # name='Discharge @ C/35'))
# fig2.add_trace(go.Scatter(x=newdsd.soc, y=newdsd.voltage,
                    # mode='lines',
                    # name='Discharge Interpolation'))
# fig2.add_trace(go.Scatter(x=dsc.soc, y=dsc.voltage,
                    # mode='lines',
                    # name='Charge @ C/35'))
# fig2.add_trace(go.Scatter(x=newdsc.soc, y=newdsc.voltage,
                    # mode='lines',
                    # name='Charge Interpolation'))
# fig2.add_trace(go.Scatter(x=sococv.soc, y=sococv.ocv,
                    # mode='lines',
                    # name='Final SOC-OCV'))

# fig2.show()


# print(v)
##### Prints and plots #####
plt.figure(figsize=(10,5))
plt.title("SOC vrs OCV")
plt.plot(newdsd.soc, newdsd.voltage, label='Discharge Interpolation')
plt.plot(newdsc.soc, newdsc.voltage, label='Charge Interpolation')
plt.plot(sococv.soc, sococv.ocv, label='Final SOC-OCV')
plt.xlabel("State of Charge")
plt.ylabel("Open Circuit Voltage (V)")
plt.legend()
plt.show()

