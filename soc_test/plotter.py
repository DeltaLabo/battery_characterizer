import pandas as pd
import matplotlib.pyplot as plt

ds = pd.read_csv('C:/Repositories/battery_characterizer/soc_test/discharge_data29_09_2021_19_13.csv')

batt18650 = ds#[['time','seconds','voltage','current','capacity','temperature']]
batt18650.columns = ['time','seconds','voltage','current','capacity','temperature']
print(batt18650.describe())

plt.figure(figsize=[10,5])
plt.plot(batt18650.time, batt18650.voltage, label='voltage')
plt.xlabel('time(s)', fontsize=15)
plt.ylabel('voltage(V)', fontsize=15)
plt.legend()
plt.show()