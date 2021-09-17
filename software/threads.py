# import csv 

# with open('prueba.csv', 'r') as csv_file:
#     csv_reader = csv.reader(csv_file)

#     for line in csv_reader:
#         print(line[0])
'''
Este código servirá para escribir y ordenar los datos que se vayan a medir directamente de la fuente.
Leerá los datos, que solamente tendrán que star ordenados en columnas y filas, les añadirá
los headers y los imprimirá en el archivo 'prueba_outputs.csv', para después graficar en Excel
o seguir trabajando con los datos ya ordenados

'''
import pandas as pd 
#df = pd.read_csv("C:/Repositories/battery_characterizer/software/prueba.csv", header=None, names=["Canal","Tensión máxima batería","Corriente batería"}]) #Create a dataframe
df = pd.read_csv("C:/Repositories/battery_characterizer/software/prueba_inputs.csv", header=0, index_col='Canal escogido', names=['Canal escogido','Battery voltage','Battery amperes', 'Tiempo transcurrido'])
#print(df)
df.to_csv('C:/Repositories/battery_characterizer/software/prueba_outputs.csv')

# if colfil == "columna":
#     columna = int(input("Digite la columna:\n"))
#     result = df.iloc([columna])
# elif colfil == "fila":
#     fila = int(input("Digite la fila:\n"))
#     result = df.iloc[[fila]]
# else:
#     print("Respuesta inválida")

#print(result)

