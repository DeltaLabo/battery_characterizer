import pandas as pd
import matplotlib.pyplot as plt

from google.colab import drive
drive.mount('/content/drive', force_remount=True)

# from google.colab import files
# files.upload()

ds = pd.read_csv('/content/drive/MyDrive/FRDET_4.0V.csv')

ds.time = round(ds.time * 60,0) #solo para pasarlo a segundos

batt40 = ds[['time','ibatt','vbat']]
power = batt40.apply(lambda row: row.ibatt * row.vbat, axis=1)
batt40 = batt40.assign(power=power.values)
batt40.iloc[0, 1:4] = batt40.iloc[1, 1:4]
batt40.columns = ['time', 'current', 'voltage', 'power']

plt.figure(figsize=[15,5])
plt.plot(batt40.time, batt40.voltage, label='voltage')
plt.xlabel('time(s)', fontsize=15)
plt.ylabel('voltage(V)', fontsize=15)
plt.legend()
plt.show()

plt.figure(figsize=[15,5])
plt.plot(batt40.time, batt40.current, label='current')
plt.xlabel('time(s)', fontsize=15)
plt.ylabel('current(A)', fontsize=15)
plt.legend()
plt.show()

plt.figure(figsize=[15,5])
plt.plot(batt40.time, batt40.power, label='power')
plt.xlabel('time(s)', fontsize=15)
plt.ylabel('power(W)', fontsize=15)
plt.legend()
plt.show()

batt40.to_csv(r'/content/batt40.csv', index=False)