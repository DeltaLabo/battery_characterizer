import pandas as pd
import matplotlib.pyplot as plt

ds = pd.read_csv('discharge_pulse21_10_2021_11_53.csv')
ds.columns = ['timestamp', 'time', 'tag', 'voltage', 'current', 'capacity', 'temprerature' ]
ds = ds.drop('timestamp', axis=1)
print(ds.head())

plt.figure(figsize=[15,5])
plt.plot(ds.time, ds.voltage, label='voltage')
plt.plot(ds.time, ds.tag, label='tag')
plt.xlabel('time(s)', fontsize=15)
plt.ylabel('voltage(V)', fontsize=15)
plt.legend()
plt.show()


# bat40 = ds40[['time','ibat','vbat']]
# power = bat40.apply(lambda row: row.ibat * row.vbat, axis=1)
# bat40 = bat40.assign(power=power.values)
# bat40.columns = ['time', 'current', 'voltage', 'power']

# ds35 = pd.read_csv('FRDET35.csv')

# ds35.time = round(ds35.time * 60,0) #solo para pasarlo a segundos

# bat35 = ds35[['time','ibat','vbat']]
# power = bat35.apply(lambda row: row.ibat * row.vbat, axis=1)
# bat35 = bat35.assign(power=power.values)
# bat35.columns = ['time', 'current', 'voltage', 'power']

# bat40.to_csv('bat40.csv', index=False)
# bat35.to_csv('bat35.csv', index=False)

# plt.figure(figsize=[15,5])
# plt.plot(bat40.time, bat40.power, label='power')
# plt.xlabel('time(s)', fontsize=15)
# plt.ylabel('power(W)', fontsize=15)
# plt.legend()
# plt.show()

# plt.figure(figsize=[15,5])
# plt.plot(bat35.time, bat35.power, label='power')
# plt.xlabel('time(s)', fontsize=15)
# plt.ylabel('power(W)', fontsize=15)
# plt.legend()
# plt.show()



