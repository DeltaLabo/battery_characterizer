import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

#Para descarga
dsd = pd.read_csv('C:/Repositories/battery_characterizer/soc_test/discharge_data29_09_2021_19_13.csv')
dsd.columns = ['time','seconds','voltage','current','capacity','temperature']
print("Antes de limpiar")
print(dsd.describe())
dsd.capacity = dsd.capacity - dsd.capacity.min()
dsd.seconds = dsd.seconds - dsd.seconds.min()
soc = 1 - dsd.capacity/dsd.capacity.max()
dsd = dsd.assign(soc=soc.values)
print("Después de limpiar")
print(dsd.describe())


dsc = pd.read_csv('C:/Repositories/battery_characterizer/soc_test/charge_data29_09_2021_19_13.csv')
dsc.columns = ['time','seconds','voltage','current','capacity','temperature']
print("Antes de limpiar")
print(dsc.describe())
dsc.capacity = dsc.capacity - dsc.capacity.min()
dsc.seconds = dsc.seconds - dsc.seconds.min()

c_eff = dsd.capacity.max() / dsc.capacity.max()
print("Eficiencia de Coulomb:", c_eff)
#aplicando la eff de col al dataset

dsc.capacity = c_eff*dsc.capacity

soc = dsc.capacity/dsc.capacity.max()
dsc = dsc.assign(soc=soc.values)
print("Después de limpiar")
print(dsc.describe())



fig = px.scatter(dsc, x="time", y="voltage")
fig.show()

fig = go.Figure()

# Add traces
fig.add_trace(go.Scatter(x=dsd.soc, y=dsd.voltage,
                    mode='lines',
                    name='discharge'))
fig.add_trace(go.Scatter(x=dsc.soc, y=dsc.voltage,
                    mode='lines',
                    name='charge'))

fig.show()