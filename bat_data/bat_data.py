import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

ds40 = pd.read_csv('FRDET40.csv')

ds40.time = round(ds40.time * 60,0) #solo para pasarlo a segundos

bat40 = ds40[['time','ibat','vbat']]
newi = bat40.ibat/2
bat40 = bat40.assign(ibat=newi.values)
power = bat40.apply(lambda row: row.ibat * row.vbat, axis=1)
bat40 = bat40.assign(power=power.values)
bat40.columns = ['time', 'current', 'voltage', 'power']

bat40.iloc[0,1:4] = bat40.iloc[2,1:4]
bat40.iloc[1,1:4] = bat40.iloc[2,1:4]

print(bat40.head())


ds35 = pd.read_csv('FRDET35.csv')

ds35.time = round(ds35.time * 60,0) #solo para pasarlo a segundos

bat35 = ds35[['time','ibat','vbat']]
newi = bat35.ibat/2
bat35 = bat35.assign(ibat=newi.values)
power = bat35.apply(lambda row: row.ibat * row.vbat, axis=1)
bat35 = bat35.assign(power=power.values)
bat35.columns = ['time', 'current', 'voltage', 'power']

bat35.iloc[0,1:4] = bat35.iloc[2,1:4]
bat35.iloc[1,1:4] = bat35.iloc[2,1:4]


def interpolation(x_data, y_data, x_in): #Usar con R0, R1, C1
        for i in range(len(x_data)-1):
            if x_in < x_data[0]:
                x_out = y_data[0] #Cambiar por extrapolación
                break
            if x_in > x_data[len(x_data)-1]:
                x_out = y_data[len(x_data)-1] #Cambiar por extrapolación
                break
            if x_data[i+1] >= x_in and x_data[i] <= x_in: #Función de interpolación
                x_out = y_data[i] + (y_data[i+1] - y_data[i]) * ((x_in - x_data[i]) / (x_data[i+1] - x_data[i]))
                break
        return x_out

modeldf = pd.read_csv('../validation/parameters.csv')
ocvdf = pd.read_csv('../soc_test/sococv.csv')
z_data = modeldf.soc.values
r0_data = modeldf.r0.values
r1_data = modeldf.r1.values
c1_data = modeldf.c1.values
ocv_data = ocvdf.OCV.values

i_R1_0 = 0
z_0_p = 0.98
z_0_r = 0.98
v_0 = 4.0
deltat = 1


z_p = np.array([z_0_p])
z_r = np.array([z_0_r])
i_R1 = np.array([i_R1_0])
v = np.array([v_0])
n = 1
Q = 3.25

for i in range(len(bat40)-1):
    R0 = interpolation(z_data, r0_data, z_p[-1])
    R1 = interpolation(z_data, r1_data, z_p[-1])
    C1 = interpolation(z_data, c1_data, z_p[-1])
    ocv_p = bat40.voltage[i] + R1*i_R1[-1] + R0*bat40.current[i]
    z_new = (z_r[-1] - (n*deltat*bat40.current[i]/(3600*Q)))
    z_r = np.append(z_r, z_new)
    z_p = np.append(z_p, interpolation(ocv_data, z_data, ocv_p)) #predicho
    i_R1 = np.append(i_R1, np.exp(-deltat / (R1 * C1)) * i_R1[-1] + (1 - np.exp(-deltat / (R1 * C1)) * bat40.current[i]))
	

bat40.to_csv('bat40.csv', index=False)
bat35.to_csv('bat35.csv', index=False)

plt.figure(figsize=[15,5])
#plt.plot(bat40.time, bat40.power, label='power')
plt.plot(bat40.time, z_r, label='real')
plt.plot(bat40.time, z_p)
plt.xlabel('time(s)', fontsize=15)
plt.ylabel('power(W)', fontsize=15)
plt.legend()
plt.show()

# plt.figure(figsize=[15,5])
# plt.plot(bat35.time, bat35.power, label='power')
# plt.xlabel('time(s)', fontsize=15)
# plt.ylabel('power(W)', fontsize=15)
# plt.legend()
# plt.show()



