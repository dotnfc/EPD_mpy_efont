import time
#import network
import ujson as json
import urequests as requests
from epd_sdl_420bw import *
#from epd_z96 import *
from efont import *
import qw_icons

BLACK = const(0)
WHITE = const(1)

def init():
    epd = Epd420BW() # EPD()
    epd.init()
    epd.clearBuffer()
    epd.ima = Image(epd.WIDTH, epd.HEIGHT)
    
    # font = FT2("font/wenquanyi_12pt.pcf", render=epd, size=16)
    font = FT2("font/simyou-lite.ttf", render=epd, size=24)
    font.mono=True
    
    epd.fill(WHITE)
    font.drawString(10, 10, 400, 24, ALIGN_LEFT, "0000-00-00")
    epd.rect(2, 35, 230, 3, BLACK, True)
    font.drawString(10, 105, 400, 24, ALIGN_LEFT, "城市: N/A") # "City: N/A")
    font.drawString(10, 135, 400, 24, ALIGN_LEFT, "湿度: N/A") # "Humidity: N/A")
    font.drawString(10, 165, 400, 24, ALIGN_LEFT, "温度: N/A") # "Temp: N/A")

    epd.drawImage = lambda epd, x, y, file: (epd.ima.load(file, True), epd.ima.draw(epd, x, y))

    epd.drawImage(epd, 5, 40, "image/weather.jpg")
    # ima.load("image/weather.jpg", True)
    # ima.draw(epd, 5, 40)
    
    epd.drawImage(epd, 170, 10, "image/wifi_strong.jpg")    
    # ima.load("image/wifi_strong.jpg", True)
    # ima.draw(epd, 170, 10)
    
    epd.rect(2, 230, 230, 3, BLACK, True)
    epd.drawImage(epd, 5, 238, "image/micropython.jpg")
    # ima.load("image/micropython.jpg", True)
    # ima.draw(epd, 5, 238)

    epd.displayBuffer()
    return epd, font

def wifi_connect(ssid, password, epd):
    wlan = network.WLAN(network.STA_IF)

    print("Begin to connect wifi...")
    wlan.connect(ssid, password)

    if wlan.isconnected():
        print("Wifi connect successful, waitting to get IP...")
    else:
        print("Wifi connect failed.")

    count = 0
    while count < 3:
        epd.drawImage(epd, 170, 10, "image/wifi_week.jpg")
        time.sleep(0.3)
        epd.drawImage(epd, 170, 10, "image/wifi_middle.jpg")
        time.sleep(0.3)
        epd.drawImage(epd, 170, 10, "image/wifi_strong.jpg")
        time.sleep(0.3) 
        count += 1

def main():
    ssid     = "DOTNFC-HOS"
    password = "20180903"

    epd, font = init()
    #wifi_connect(ssid, password, epd)
    
    epd.fill(WHITE)
    font.drawString(10, 10, 400, 24, ALIGN_LEFT, "2000-12-31")
    epd.displayBuffer()
    
    while(not epd.eventProcess()):
        time.sleep(0.01)
        
if __name__ == "__main__":
    main()
