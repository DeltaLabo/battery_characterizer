import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# #Para descarga
# dsd = pd.read_csv('C:/Repositories/battery_characterizer/soc_test/discharge_data29_09_2021_19_13.csv')
# dsd.columns = ['time','seconds','voltage','current','capacity','temperature']
# #print("Antes de limpiar")
# #print(dsd.describe())
# dsd.capacity = dsd.capacity - dsd.capacity.min()
# dsd.seconds = dsd.seconds - dsd.seconds.min()
# soc = 1 - dsd.capacity/dsd.capacity.max()
# dsd = dsd.assign(soc=soc.values)
# #print("Después de limpiar")
# #print(dsd.describe())

# # Para carga
# dsc = pd.read_csv('C:/Repositories/battery_characterizer/soc_test/charge_data29_09_2021_19_13.csv')
# dsc.columns = ['time','seconds','voltage','current','capacity','temperature']
# #print("Antes de limpiar")
# #print(dsc.describe())
# dsc.capacity = dsc.capacity - dsc.capacity.min()
# dsc.seconds = dsc.seconds - dsc.seconds.min()
# # soc = dsc.capacity/dsc.capacity.max()
# # dsc = dsc.assign(soc=soc.values)
# # print("Después de limpiar")
# # print(dsc.describe())

# c_eff = dsd.capacity.max() / dsc.capacity.max()
# print("Eficiencia de Coulomb:", c_eff)
# print(max(dsd.capacity))
# print(max(dsc.capacity))
# #Aplicando la eficiencia de Coulomb al dataset

# dsc.capacity = c_eff*dsc.capacity

# soc = dsc.capacity/dsc.capacity.max()
# dsc = dsc.assign(soc=soc.values)
#print("Después de limpiar")
#print(dsc.describe())

# fig = px.scatter(dsc, x="soc", y="voltage")
# fig.show()

# fig = go.Figure()

# #Add traces
# fig.add_trace(go.Scatter(x=dsd.soc, y=dsd.voltage,
#                     mode='lines',
#                     name='discharge'))
# fig.add_trace(go.Scatter(x=dsc.soc, y=dsc.voltage,
#                     mode='lines',
#                     name='charge'))

# fig.show()

#################################################################################################################
#################################################################################################################
new_soc = np.linspace(0, 1, 100)
#print(new_soc)
#print(len(new_soc))
# new_fig = px.scatter(dsc, x=new_soc, y="voltage")
# new_fig.show()
# interp_volt = np.interp(new_soc, dsd.soc, dsd.voltage)
# new_fig = px.scatter(x=new_soc, y=interp_volt)
# new_fig.show()

# print(np.asarray(new_soc).shape)
# print(np.asarray(dsd.voltage).shape)

# import scipy.interpolate
# y_interp = scipy.interpolate.interp1d(new_soc, dsd.voltage)
# print (y_interp(5.0))

######################## INTERPOLATION #########################################
#for i in len(new_soc):
    


# new_fig.add_trace(go.Scatter(x=dsd.soc, y=dsd.voltage,
#                      mode='lines',
#                      name='discharge'))
# new_fig.add_trace(go.Scatter(x=new_soc, y=interp_volt,
#                      mode='lines',
#                      name='charge'))

# new_fig.show()
######################### CHARGE @0.5C #############################
dsc = pd.read_csv('C:/Repositories/battery_characterizer/coulomb_tests/charge_data04_10_2021_11_04.csv')
dsc.columns = ['time','seconds','voltage','current','capacity','temperature']
#print("Antes de limpiar")
#print(dsc.describe())
dsc.capacity = dsc.capacity - dsc.capacity.min()
dsc.seconds = dsc.seconds - dsc.seconds.min()
soc = dsc.capacity/dsc.capacity.max()
dsc = dsc.assign(soc=soc.values)
#print("Después de limpiar")
#print(dsc.describe())
######################### DISCHARGE @1C #############################
dsd = pd.read_csv('C:/Repositories/battery_characterizer/coulomb_tests/discharge_data04_10_2021_16_22.csv')
dsd.columns = ['time','seconds','voltage','current','capacity','temperature']
#print("Antes de limpiar")
#print(dsd.describe())
dsd.capacity = dsd.capacity - dsd.capacity.min()
dsd.seconds = dsd.seconds - dsd.seconds.min()
soc = 1 - dsd.capacity/dsd.capacity.max()
dsd = dsd.assign(soc=soc.values)
dsd.sort_values(by=['soc'],inplace=True)
#print("Después de limpiar")
print(dsd.head())

c_eff = dsd.capacity.max() / dsc.capacity.max()
# print("Eficiencia de Coulomb:", c_eff)
# print(max(dsd.capacity))
# print(max(dsc.capacity))
################### DISCHARGE ###########################

dis_table_soc, dis_table_volt = dsd.values[:, -1], dsd.values[:, 2] # [Filas, columnas]
# print(f"El máximo SoC es:", dis_table_soc.mean())
# print(dis_table_volt.shape)
# print(f"El máximo SoC es:", dis_table_volt.max())

#################################################################


#Aplicando la eficiencia de Coulomb al dataset

dsc.capacity = c_eff*dsc.capacity
soc = dsc.capacity/dsc.capacity.max()
dsc = dsc.assign(soc=soc.values)

# fig = px.scatter(dsc, x="soc", y="voltage")
# fig.show()

# fig = go.Figure()
# #Add traces
# fig.add_trace(go.Scatter(x=dsd.soc, y=dsd.voltage,
#                     mode='lines',
#                     name='discharge'))
# fig.add_trace(go.Scatter(x=dsc.soc, y=dsc.voltage,
#                     mode='lines',
#                     name='precharge'))

# fig.show()

# print("El máximo del new_soc es:", new_soc.max())
# print("El new_soc es del tipo:", type(new_soc))
volt_data = dsd.voltage.values
# print("El máximo del volt_data es:",volt_data.max())
# print("El volt_data es del tipo:", type(volt_data))
soc_data = dsd.soc.values
print(len(soc_data))
# print("El máximo del soc_data es:", soc.max())
# print("El soc_data es del tipo:", type(soc_data))
print(soc_data)
# print(new_soc.describe())
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

new_volt = np.zeros(len(new_soc))
for i in range(len(new_soc)):
    new_volt[i] = dsoc_interpolation(soc_data, volt_data, new_soc[i])
#print(volt_new)

#print(dsoc_interpolation(soc_data, volt_data, 1))

newds = pd.DataFrame()
newds = newds.assign(soc=new_soc)
newds = newds.assign(voltage=new_volt)
print(newds.tail())

# fig = px.scatter(newds, x="soc", y="voltage")
# fig.show()

fig = go.Figure()
#Add traces
fig.add_trace(go.Scatter(x=dsd.soc, y=dsd.voltage,
                    mode='lines',
                    name='discharge'))
fig.add_trace(go.Scatter(x=newds.soc, y=newds.voltage,
                    mode='markers',
                    name='interpolation'))
fig.show()