#-*- coding:utf-8 -*-
#----------------------------------------------------------------
#
# demo script for eFont
#
# by dotnfc, 2023/06/02
#

import time
import ujson as json
import urequests as requests
from display import *
from efont import *
from qw_icons import *

try:
    import network
except ImportError:
    import unetwork as network

def showOffline(epd, font, ssid):
    epd.fill(WHITE)
    font.drawString(10, 10, 400, 24, ALIGN_LEFT, "2023-09-14")
    epd.rect(2, 35, 230, 3, BLACK, True)
    font.drawString(10, 105, 400, 24, ALIGN_LEFT, "城市: N/A") # "City: N/A")
    font.drawString(10, 135, 400, 24, ALIGN_LEFT, "湿度: N/A") # "Humidity: N/A")
    font.drawString(10, 165, 400, 24, ALIGN_LEFT, "温度: N/A") # "Temp: N/A")
    font.drawString(10, 195, 380, 24, ALIGN_LEFT, f"无法连接到 {ssid}")
    
    epd.drawImage(5, 40, "image/weather.jpg")    
    epd.drawImage(170, 10, "image/wifi_strong.jpg")    
    
    epd.rect(2, 230, 230, 3, BLACK, True)
    epd.drawImage(5, 238, "image/micropython.jpg")
    epd.refresh()

def wifi_connect(epd, font, ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    print("Begin to connect wifi...")
    font.drawString(10, 100, 380, 24, ALIGN_CENTER, f"正在连接 {ssid} ...")
    epd.refresh()
    
    wlan.connect(ssid, password)

    count = 0
    while not wlan.isconnected():
        time.sleep(0.2)
        count += 1
        if count > 25:
            break   # time out about 3s
        pass
    
    if wlan.isconnected():
        print("Wifi connect successful")
        font.drawString(10, 140, 380, 24, ALIGN_CENTER, "已连接")
        epd.refresh(full=False)
        return True
    else:
        print("Wifi connect failed.")
        return False

def getIcon(weather):
    weathers = { 
                "xue" : QW_499, 
                "lei" : QW_304, 
                "shachen" : QW_503, 
                "wu" : QW_509, 
                "bingbao" : QW_100, 
                "yun" : QW_104, 
                "yu" : QW_306, 
                "yin" : QW_104, 
                "qing" : QW_100
    }
    
    try:
        icon = weathers[weather]
    except KeyError:
        icon = QW_999
        
    return icon
    
def delayStart(n):
    for _ in range(n):
        print(".", end="")
        time.sleep(1)
    print("")
        
def main():
    ssid     = "DOTNFC-HOS"
    password = "20180903"
    
    epd = EpdImage()
    epd.init()
    epd.fill(WHITE)
    font = FT2("font/simyou-lite.ttf", render=epd, mono=True, size=24)
    ttfIco = FT2("font/qweather-icons.ttf", render=epd, mono=True, size=32)
    if not wifi_connect(epd, font, ssid, password):
        showOffline(epd, font, ssid)
        epd.deepsleep(15000)
    
    cityid = "101010100"  
    url = "http://www.tianqiapi.com/api/?version=v6&cityid=" + cityid + "&appid=65251531&appsecret=Yl2bzCYb"
    r = requests.get(url)
    data = json.loads(r.content.decode())
    
    ################################ online weather ################################
    epd.fill(WHITE)
    font.drawString(10, 10, 400, 24,  ALIGN_LEFT, "%s"%data["date"])
    font.drawString(10, 105, 400, 24, ALIGN_LEFT, "城市: %s"%data["city"])
    font.drawString(10, 135, 400, 24, ALIGN_LEFT, "湿度: %s"%data["humidity"])
    font.drawString(10, 165, 400, 24, ALIGN_LEFT, "温度: %s-%s°"%(data["tem2"], data["tem1"]))
    
    ico = getIcon(data["wea_img"])
    ttfIco.drawString(190, 160, 400, 48, ALIGN_LEFT, ico, 32)
        
    epd.drawImage(5, 40, "image/weather.jpg")
    
    epd.rect(2, 230, 230, 3, BLACK, True)
    epd.drawImage(5, 238, "image/micropython.jpg")
    
    epd.refresh()
    time.sleep(1)
    
    ################################ end ################################

    epd.fill(WHITE)
    epd.rect(2, 230, 230, 3, BLACK, True)
    epd.drawImage(5, 238, "image/micropython.jpg")
    font.drawString(10, 10, 400, 32, ALIGN_LEFT, "%s %s"%(data["date"], data["week"]))
    epd.refresh()
    time.sleep(1)
    
    epd.fill(WHITE)
    epd.refresh()
    
    
    #epd.deepsleep(15000)
    
if __name__ == "__main__":
    main()
