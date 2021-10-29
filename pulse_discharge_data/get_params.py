import pandas as pd
import matplotlib.pyplot as plt

oneC = pd.read_csv('discharge_pulse_1.0C.csv')
oneC.columns = ['timestamp', 'time', 'tag', 'voltage', 'current', 'capacity', 'temprerature']
oneC = oneC.drop('timestamp', axis=1)
oneCsoc = 1 - oneC.capacity/oneC.capacity.max() #esto hay que corregirlo porque la capacidad maxima no es la capacidad que ocupamos, se tiene que sacar de las pruebas a C/35
oneC = oneC.assign(soc=oneCsoc.values)
oneCreltime = oneC.time/oneC.time.max()
oneC = oneC.assign(reltime=oneCreltime.values)
print(oneC.head())
halfC = pd.read_csv('discharge_pulse_0.5C.csv')
halfC.columns = ['timestamp', 'time', 'tag', 'voltage', 'current', 'capacity', 'temprerature' ]
halfC = halfC.drop('timestamp', axis=1)
halfCsoc = 1 - halfC.capacity/oneC.capacity.max()
halfC = halfC.assign(soc=halfCsoc.values)
halfCreltime = halfC.time/halfC.time.max()
halfC = halfC.assign(reltime=halfCreltime.values)
print(halfC.head())
quarterC = pd.read_csv('discharge_pulse_0.25C.csv')
quarterC.columns = ['timestamp', 'time', 'tag', 'voltage', 'current', 'capacity', 'temprerature' ]
quarterC = quarterC.drop('timestamp', axis=1)
quarterCsoc = 1 - quarterC.capacity/oneC.capacity.max()
quarterC = quarterC.assign(soc=quarterCsoc.values)
quarterCreltime = quarterC.time/quarterC.time.max()
quarterC = quarterC.assign(reltime=quarterCreltime.values)
print(halfC.head())



plt.figure(figsize=[15,5])
plt.plot(oneC.reltime, oneC.voltage, label='1.0C')
#plt.plot(oneC.time, oneC.soc, label='1.0C')
plt.plot(halfC.reltime, halfC.voltage, label='0.5C')
plt.plot(quarterC.reltime, quarterC.voltage, label='0.5C')
plt.xlabel('relative time', fontsize=15)
plt.ylabel('voltage(V)', fontsize=15)
plt.legend()
plt.show()


