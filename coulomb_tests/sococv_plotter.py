import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

datapoints = 1000

def dsoc_interpolation(soc_data, volt_data, soc_in):
    for i in range(len(soc_data)-1):# soc_in.max()):
        if soc_in == 0:
            volt_out = volt_data[0]
            break
        if soc_in == 1:
            volt_out = volt_data[len(soc_data)-1]
            break
        if soc_data[i] >= soc_in and soc_data[i-1] < soc_in: #Función de interpolación
            volt_out = volt_data[i-1] + (volt_data[i] - volt_data[i-1]) * (soc_in - soc_data[i-1]) / (soc_data[i] - soc_data[i-1])
            break
    return volt_out

#################################################################################
################################# PARA DESCARGA #################################
#################################################################################

dsd = pd.read_csv('C:/Repositories/battery_characterizer/soc_test/discharge_data29_09_2021_19_13.csv')#Upload csv
dsd.columns = ['time','seconds','voltage','current','capacity','temperature']

# Limpiando los datos PARA DESCARGA
dsd.capacity = dsd.capacity - dsd.capacity.min()
dsd.seconds = dsd.seconds - dsd.seconds.min()
socd = 1 - dsd.capacity/dsd.capacity.max()
dsd = dsd.assign(soc=socd.values)
dsd = dsd.sort_values(by=['seconds'], ascending=False)
dsd = dsd.reset_index(drop=True)
print(dsd.head())

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

dsc = pd.read_csv('C:/Repositories/battery_characterizer/soc_test/charge_data29_09_2021_19_13.csv')#Upload csv
dsc.columns = ['time','seconds','voltage','current','capacity','temperature']

# Limpiando los datos PARA CARGA
dsc.capacity = dsc.capacity - dsc.capacity.min()
dsc.seconds = dsc.seconds - dsc.seconds.min()
# Coulumb eff
c_eff = dsc.capacity.max() / dsd.capacity.max()
dsc.capacity = c_eff*dsc.capacity
socc = dsc.capacity/dsc.capacity.max()
dsc = dsc.assign(soc=socc.values)

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
sococv.to_csv('sococv.csv', index=False)

R0 = ((newdsc.voltage.values - newdsd.voltage.values)/2)/0.1 #calcular el R para todos los puntos R=dV/i
socR0 = pd.DataFrame(data={"soc":soc,"R0":R0})
socR0.to_csv('socR0.csv', index=False)

fig1 = px.scatter(socR0, x="soc", y="R0")
fig1.show()

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=dsd.soc, y=dsd.voltage,
                    mode='lines',
                    name='Discharge @ C/35'))
fig2.add_trace(go.Scatter(x=newdsd.soc, y=newdsd.voltage,
                    mode='lines',
                    name='Discharge Interpolation'))
fig2.add_trace(go.Scatter(x=dsc.soc, y=dsc.voltage,
                    mode='lines',
                    name='Charge @ C/35'))
fig2.add_trace(go.Scatter(x=newdsc.soc, y=newdsc.voltage,
                    mode='lines',
                    name='Charge Interpolation'))
fig2.add_trace(go.Scatter(x=sococv.soc, y=sococv.ocv,
                    mode='lines',
                    name='Final SOC-OCV'))

fig2.show()
