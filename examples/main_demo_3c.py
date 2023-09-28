#-*- coding:utf-8 -*-
#----------------------------------------------------------------
#
# R/B/W 3 color EPD demo script for eFont
#
# to run in sdl simulator, run script like 'mpy -X heapsize=8m main_demo_3c.py'
# by dotnfc, 2023/06/02
#
import time
import ujson as json
import urequests as requests
from display3c import *
from efont import *
from qw_icons import *

try:
    import network
except ImportError:
    import unetwork as network

def main():
    epd = EpdImage()
    epd.init()
    epd.loadFont("simyou")
    epd.selectFont("simyou")
    epd.clear(EPD_WHITE, EPD_WHITE)
    epd.setColor(EPD_RED, EPD_WHITE)
            
    epd.line_3c(10, 90, epd.WIDTH -1, 90, 1)        
    epd.drawText(490, 100, 200, 60, ALIGN_LEFT, "Hello 世界 16px")
    epd.drawText(490, 120, 200, 60, ALIGN_LEFT, "Hello 世界 32px", 32)
    epd.drawText(490, 160, 200, 60, ALIGN_LEFT, "Hello 世界 48px", 48)
    epd.line_3c(0, 0, epd.WIDTH -1, epd.HEIGHT - 1, 1)
    epd.drawImage(0, 0, "image/micropython.jpg")
    
    epd.loadFont("icons")
    epd.selectFont("icons")
    epd.line_3c(10, 230, epd.WIDTH -1, 230, 1)
    epd.drawText(10, 240, 400, 32, ALIGN_LEFT, ICO_LOGO_NFC, 64)
    epd.drawText(80, 240, 400, 32, ALIGN_LEFT, ICO_LOGO_NFC, 48)
    epd.drawText(132, 240, 400, 32, ALIGN_LEFT, ICO_LOGO_NFC, 32)
    epd.drawText(170, 240, 400, 32, ALIGN_LEFT, ICO_LOGO_NFC, 16)
    
    epd.loadFont("7seg")
    epd.selectFont("7seg")
    epd.setColor(EPD_BLACK, EPD_WHITE)
    epd.line_3c(10, 320, epd.WIDTH -1, 320, 1)
    epd.drawText(10, 330, 400, 30, ALIGN_LEFT, "2023/09/27 11:11", 112)
    
    epd.text_3c("text here", 20, 500, 1)
    
    epd.refresh()
    epd.deepSleep(15000)
    
if __name__ == "__main__":
    main()
