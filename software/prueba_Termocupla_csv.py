import time
import board
import digitalio
import adafruit_max31855
import gpiozero
from time import sleep, strftime, time
import matplotlib.pyplot as plt
#from gpiozero import CPUTemperature
#import pandas as pd

plt.ion()
x = []
y = []


spi = board.SPI()
cs = digitalio.DigitalInOut(board.D5)

max31855 = adafruit_max31855.MAX31855(spi, cs)

with open("/home/pi/cpu_temp.csv", "a") as log:

    while True:
        tempC = max31855.temperature
        #tempF = tempC * 9 / 5 + 32
        y.append(tempC)
        x.append(time())
        plt.clf()
        plt.scatter(x,y)
        plt.plot(x,y)
        print("Temperature: {} C".format(tempC))
        log.write("{0},{1}\n".format(strftime("%Y-%m-%d %H:%M:%S"),str(tempC)))
        #sleep(2.0)
        plt.pause(2)
        plt.draw()

