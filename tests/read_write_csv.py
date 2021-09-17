import numpy as np
import pandas as pd

data = np.random.randint(5,30,size=(10,3))
df = pd.DataFrame(data, columns=['Voltaje', 'Corriente', 'Tiempo']) 

df.to_csv('C:/Repositories/battery_characterizer/tests/csv_tests_write_read.csv', index = 'Voltaje', columns = ('Voltaje','Corriente','Tiempo'))
# Use index_label=False for easier importing in R.

#print(df.iloc[0,1])
#print(df)
df2 = pd.read_csv("C:/Repositories/battery_characterizer/software/prueba_inputs.csv", header=0)
print(df2.iloc[0,2]) #[Fila,columna] 
print(df2.head())
# Con esto puedo leer la celda que indique entre los []