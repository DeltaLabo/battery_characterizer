import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('C:/Repositories/battery_characterizer/bat_data/bat40.csv')
df.columns = ['time', 'current', 'voltage', 'power']
def sec_interpolation(sec_data, pow_data, sec_in):
    for i in range(len(sec_data)-1):
        if sec_in < sec_data[0]:
            pow_out = pow_data[0]
            break
        if sec_in > sec_data[len(sec_data)-1]:
            pow_out = pow_data[len(sec_data)-1]
            break
        if sec_data[i+1] >= sec_in and sec_data[i] <= sec_in:
            pow_out = pow_data[i] + (pow_data[i+1] - pow_data[i]) * ((sec_in - sec_data[i]) / (sec_data[i+1] - sec_data[i]))
            break
    return pow_out
new_sec = np.linspace(0,5560,113)
new_pow = np.array([])
sec_data = df.time.values
pow_data = df.power.values

for i in range(len(new_sec)):
    new_pow = np.append(new_pow, sec_interpolation(sec_data, pow_data, new_sec[i]))

plt.figure
plt.plot(new_sec, new_pow, 'xr', sec_data, pow_data)
# plt.title("DataFrame 2")
plt.xlabel("time (s)")
plt.ylabel("power (W)")
plt.show()


