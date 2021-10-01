import pandas as pd
import plotly.express as px


#Para descarga
dsd = pd.read_csv('C:/Repositories/battery_characterizer/soc_test/discharge_data29_09_2021_19_13.csv')
dsd.columns = ['time','seconds','voltage','current','capacity','temperature']
print("Antes de limpiar")
print(dsd.describe())
dsd.capacity = dsd.capacity - dsd.capacity.min()
dsd.seconds = dsd.seconds - dsd.secondsd.min()
soc = 1 - dsd.capacity/dsd.capacity.max()
ds = dsd.assign(soc=soc.values)
print("Después de limpiar")
print(dsd.describe())
fig = px.scatter(dsd, x="soc", y="voltage")
fig.show()
