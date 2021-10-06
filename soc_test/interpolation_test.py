import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 2*np.pi, 10)
y = np.sin(x) #Función original
xvals = np.linspace(0, 2*np.pi, 50)
yinterp = np.interp(xvals, x, y)
plt.plot(x, y, 'o')
plt.plot(xvals, yinterp, '-x')
plt.show()