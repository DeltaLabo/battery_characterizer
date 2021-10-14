'''
Thevenin Equivalent-Circuit Model
From  some given values of R1 and C1, the code is going to iterate to predict, in a discrete time,
the state of charge (z), the difussion-resistor current (ir1) and the output voltage (v)

'''
import pandas as pd  
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
#z(i+1) = z(i) - ((t2 - t1)) * n * I(i) / Q #1st equation

#ir1(i+1) = exp(-(t2 - t1)/R1 * C1) * Ir1(i) + (1-exp(-(t2 - t1)/R1 * C1)) * I(i) #2nd equation

#v(i) = ocv(i) - (R1 * Ir1(i)) - (R0 * I(i)) #3rd equation

def soc_iteration(soc_in, meas_curr):
    #print(soc_in, type(soc_in))
    for i in range(len(soc_in)):
        if i == 0:
            soc_out = 0.25 - (0.25 * 1 * meas_curr / 3.25)
            #print(soc_out)
        else:
            soc_out = soc_in[i-1] - (0.25 * 1 * meas_curr / 3.25)#Q
            #print("este es", soc_in[i-1], soc_in[i], soc_in[i+1])
            #print(soc_out)
            break
    return soc_out

df = pd.read_csv('C:/Users/Diego/Desktop/OCV(z).csv')
df.columns = ['SOC','OCV']

predicted_soc = np.zeros(len(df.SOC))
soc_in = df.SOC.values
meas_curr = 3.25 #constante

for i in range(len(soc_in)):
    print("AQUI:", len(soc_in))#, type(soc_in))
    predicted_soc[i] = soc_iteration(soc_in, meas_curr)
    print(type(soc_in), len(soc_in))
    #soc_in[i] = predicted_soc[i-1]

newdf = pd.DataFrame()
newdf = newdf.assign(SOC=predicted_soc)

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=df.SOC, y=df.OCV,
                    mode='lines',
                    name='Data'))
fig2.add_trace(go.Scatter(x=newdf.predicted_soc, y=df.OCV,
                    mode='markers',
                    name='Iteration'))

fig2.show()

#z(1) = z(0) - ((t2 - t1)) * n * I(i) / Q
soc = df.SOC - ((1 * 0.25 ) / 3.25) * 3.25 

df = df.assign(soc=soc.values)


fig = px.scatter(df, x="soc", y="OCV")
fig.show()
fig = go.Figure()
fig.add_trace(go.Scatter(x=df.soc, y=df.OCV,
                     mode='marks',
                     name='Interpolation'))
fig.add_trace(go.Scatter(x=df.SOC, y=df.OCV,
                     mode='lines',
                     name='data'))