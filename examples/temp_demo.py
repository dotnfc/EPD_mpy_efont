#-*- coding:utf-8 -*-
#----------------------------------------------------------------
# temperature from SHT sensor and the ESP chip internal sensor
#

from machine import Pin
import time
from sht30 import SHT3x_Sensor
import efont

sens_en = Pin(40)
sens_en.init(sens_en.OUT, value=1)


sht3x_sensor = SHT3x_Sensor(freq=100000, sdapin=38, sclpin=39)
measure_data = sht3x_sensor.read_temp_humd()
# measure_data = [22.9759, 73.8277]
# The default decimal place is 4 digits
temp = measure_data[0]
humd = measure_data[1]

print('Temp:', temp)
print('Humd:', humd)

print('Chip', efont.chipTemperature())
