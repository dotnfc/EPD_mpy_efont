#-*- coding:utf-8 -*-
#----------------------------------------------------------------
# sd mmc 1 data line demo
#

import os, machine
from machine import Pin

# SDMMC
sd = machine.SDCard(slot=1, cd=None, wp=None, sck=Pin(41), miso=Pin(40), mosi=Pin(42))
print(sd.info())

# SPI
# sd = machine.SDCard(slot=2, cd=None, wp=None, sck=Pin(3), mosi=Pin(4),miso=Pin(0), cs=Pin(8))

os.mount(sd, "/sd")
print(os.listdir("/sd"))
