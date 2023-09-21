#-*- coding:utf-8 -*-
# epd test for unix port
# by dotnfc, 2023/09/11

from efont import *
from panel.epd_sdl_420bw import *
import time
import gc
import ujson as json
import urequests as requests
import machine
from qw_icons import *
try:
    import unetwork as network
except:
    raise RuntimeError("Missing unetwork implementation!")
    
BLACK = const(0)
WHITE = const(1)

class EpdImage(Epd420BW):
        
    def __init__(self):
        Epd420BW.__init__(self)
        self.image = Image(self.WIDTH, self.HEIGHT)
    
    def drawImage(self, x, y, filename):
        self.image.load(filename, True)
        self.image.draw(self, x, y)

def testFT2():
    epd = Epd420BW()
    epd.init()
    epd.clearBuffer()
   
    black = 0
    white = 1
    epd.fill(white)
    
    ico = FT2("font/qweather-icons.ttf", render=epd, size=32)
    ico.mono=True
    ff = FT2("font/simyou-lite.ttf", render=epd, size=16)
    ff.mono=True
    wqy = FT2("font/wenquanyi_12pt.pcf", render=epd, size=16)
    wqy.mono=True
    wqyb = FT2("font/wenquanyi_12ptb.pcf", render=epd, size=16)
    wqyb.mono=True
    
    # ff.drawString(0, 50, 400, 24, ALIGN_CENTER, "你好世界！Hello World!", 24)
    ff.drawString(0, 50, 400, 24, ALIGN_CENTER, "2023-09-14")
    ico.drawString(10, 100, 400, 32, ALIGN_LEFT, qw_icons.ICO_LOGO_NFC, 64)
    ico.drawString(80, 100, 400, 32, ALIGN_LEFT, qw_icons.ICO_LOGO_NFC, 48)
    ico.drawString(132, 100, 400, 32, ALIGN_LEFT, qw_icons.ICO_LOGO_NFC, 32)
    ico.drawString(170, 100, 400, 32, ALIGN_LEFT, qw_icons.ICO_LOGO_NFC, 16)
    
    wqy.drawString(10, 180, 200, 24, ALIGN_LEFT, "文泉驿点阵 16x16") # 你好世界 
    wqyb.drawString(10, 200, 200, 24, ALIGN_LEFT, "文泉驿点阵 16x16 粗体") # 你好世界 
    epd.displayBuffer()
    
    gc.collect()
    epd.fill(white)
    epd.rect(2, 230, 230, 2, black, True)
    ff.drawString(0, 50, 400, 24, ALIGN_CENTER, "2023-09-14")
    epd.displayBuffer()
    
    while(not epd.eventProcess()):
        time.sleep(0.01)
        
def testImage(filename):
    epd = Epd420BW()
    epd.init()
    epd.clearBuffer()
   
    black = 0
    white = 1
    epd.fill(white)
    
    ima = Image(epd.WIDTH, epd.HEIGHT)
    
    # Image.load(self_in, file: str, mono: bool=False)
    ima.load(filename, True)
    print(f"w:{ima.width} h:{ima.height}")
    
    # Image.draw(self_in, fbuf, x: int=0, y: int=0, w: int=-1, h: int=-1, unload: bool=True)
    ima.draw(epd, 0, 0, 200, 200)
    epd.displayBuffer()
    
    while(not epd.eventProcess()):
        time.sleep(0.01)
    pass

def testGC():
    epd = Epd420BW()
    epd.init()
    epd.clearBuffer()
   
    black = 0
    white = 1
    epd.fill(white)
    ff = FT2("font/simyou-lite.ttf", render=epd, mono=True, size=16)

    ff.drawString(0, 50, 400, 24, ALIGN_CENTER, "2023-09-14")
    epd.displayBuffer()
    
    gc.collect()
    epd.fill(white)
    epd.rect(2, 230, 230, 2, black, True)
    ff.drawString(0, 50, 400, 24, ALIGN_CENTER, "2023-09-15")
    epd.displayBuffer()
    
    while(not epd.eventProcess()):
        time.sleep(0.01)
        
def showOffline(epd, font, ssid="7Days"):
    #epd = EpdImage()
    #epd.init()
    #epd.clearBuffer()
    #font = FT2("font/simyou-lite.ttf", render=epd, mono=True, size=16)
    
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
    epd.displayBuffer()

def wifi_connect(epd, font, ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    print("Begin to connect wifi...")
    font.drawString(10, 100, 380, 24, ALIGN_CENTER, f"正在连接 {ssid} ...")
    epd.displayBuffer()
    
    wlan.connect(ssid, password)

    count = 0
    while not wlan.isconnected():
        time.sleep(0.2)
        count += 1
        if count > 15:
            break   # time out about 3s
        pass
    
    if wlan.isconnected():
        print("Wifi connect successful, waitting to get IP...")
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

def weather_demo():
    ssid     = "DOTNFC-HOS"
    password = "********"
    
    epd = EpdImage()
    epd.init()
    epd.fill(WHITE)
    font = FT2("font/simyou-lite.ttf", render=epd, mono=True, size=24)
    ttfIco = FT2("font/qweather-icons.ttf", render=epd, mono=True, size=32)
    if not wifi_connect(epd, font, ssid, password):
        showOffline(epd, font, ssid)
        time.sleep(5)
        # machine.deepsleep(5000)
        
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
    
    #image = "image/" + data["wea_img"] + ".jpg" # (xue, lei, shachen, wu, bingbao, yun, yu, yin, qing)
    #epd.drawImage(190, 166, image)
    ico = getIcon(data["wea_img"])
    ttfIco.drawString(190, 160, 400, 48, ALIGN_LEFT, ico, 32)
        
    epd.drawImage(5, 40, "image/weather.jpg")
    
    epd.rect(2, 230, 230, 3, BLACK, True)
    epd.drawImage(5, 238, "image/micropython.jpg")
    
    epd.displayBuffer()
    time.sleep(3)
    
    ################################ end ################################
    gc.collect()
    epd.fill(WHITE)
    epd.rect(2, 230, 230, 3, BLACK, True)
    epd.drawImage(5, 238, "image/micropython.jpg")
    font.drawString(10, 10, 400, 32, ALIGN_LEFT, "%s %s"%(data["date"], data["week"]))
    epd.displayBuffer()
    
    # machine.deepsleep(15000)
    while(not epd.eventProcess()):
        time.sleep(0.01)

if __name__ == "__main__":
    # testGC()
    #testFT2()
    # testImage("image/hello.png")
    # showOffline()
    weather_demo()
