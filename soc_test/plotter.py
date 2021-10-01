import pandas as pd
import plotly.express as px

ds = pd.read_csv('C:/Repositories/battery_characterizer/soc_test/discharge_data29_09_2021_19_13.csv')


ds.columns = ['time','seconds','voltage','current','capacity','temperature']


soc = ds.capacity/ds.capacity.max()
print(soc)

print(ds.seconds)

ds = ds.assign(soc=soc.values)
print(ds.describe())
fig = px.scatter(ds, x="soc", y="voltage")
fig.show()
