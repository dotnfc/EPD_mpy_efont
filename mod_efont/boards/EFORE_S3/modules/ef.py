# eForecast Helper Library
# MIT license; Copyright (c) 2023 .NFC
#

# Import required libraries
from micropython import const
from machine import Pin, ADC
import time

# Hardware Pin Assignments

# LED
LED   = const(4) # BLUE

# Sense Pins
VBUS_SENSE = const(8)
VBAT_SENSE = const(1)

def get_battery_voltage():
    """
    Returns the current battery voltage. If no battery is connected, returns 4.2V which is the charge voltage
    This is an approximation only, but useful to detect if the charge state of the battery is getting low.
    """
    adc = ADC(Pin(VBAT_SENSE))  # Assign the ADC pin to read
    measuredvbat = adc.read()
    measuredvbat /= 4095  # divide by 4095 as we are using the default ADC attenuation of 0dB
    measuredvbat *= 4.2  # Multiply by 4.2V, our max charge voltage for a 1S LiPo
    return round(measuredvbat, 2)


def get_vbus_present():
    """Detect if VBUS (5V) power source is present"""
    return Pin(VBUS_SENSE, Pin.IN).value() == 1

