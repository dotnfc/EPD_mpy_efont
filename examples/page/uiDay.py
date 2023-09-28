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
import ulunar

try:
    import network
except ImportError:
    import unetwork as network

wday_number_cn = ("一", "二", "三", "四", "五", "六", "天")

def init():
    epd = EpdImage()
    epd.init()
    epd.loadFont("simyou")
    epd.loadFont("7seg")
    epd.loadFont("icons")
    epd.selectFont("simyou")
    epd.clear(EPD_WHITE, EPD_WHITE)
    epd.setColor(EPD_BLACK, EPD_WHITE)
    
    return epd

def drawBody(epd):
    epd.line_3c(1, 55, epd.WIDTH -2, 55, 1)
    
    year, month, mday, hour, minute, second, weekday, yearday, *_ = time.localtime()
    lunar = ulunar.Lunar(year, month, mday)
    
    # 时:分 星期
    s = "%02d:%02d 星期%s " % (hour, minute, wday_number_cn[weekday])
    x = epd.drawText(2, 10, 200, 24, ALIGN_LEFT, s, 32)
    
    # 阴历年份/生肖 日子
    ganzhi = lunar.getGanZhi()
    shengxiao = lunar.getZodiac()
    ymon = lunar.getMonth()
    yday = lunar.getDate()
    s = "%s(%s)年 %s%s" % (ganzhi, shengxiao, ymon, yday)
    epd.drawText(x + 2, 10, 200, 24, ALIGN_LEFT, s, 32)
        
    # 年月
    s = "%04d/%02d" % (year, month)
    epd.drawText(0, 100, epd.WIDTH, 48, ALIGN_CENTER, s, 64)
    
    # 图标 / 日
    s = "%02d" % (mday)
    epd.drawText(0, 300, epd.WIDTH, 96, ALIGN_CENTER, s, 156)
    
    epd.selectFont("icons")
    epd.drawText(0, 200, epd.WIDTH, 192, ALIGN_CENTER, ICO_CALENDAR, 272)
        
    epd.line_3c(1, 540, epd.WIDTH -2, 540, 1)
    pass

def drawFootbar(epd):
        
    url = "https://v1.hitokoto.cn/?encode=json&min_length=1&max_length=28"
    r = requests.get(url)
    jdoc = json.loads(r.content.decode())
    text = jdoc["hitokoto"]
    
    epd.selectFont("icons")
    x = epd.drawText(8, 560, epd.WIDTH, 192, ALIGN_LEFT, ICO_GIFT, 48)
    
    epd.selectFont("simyou")
    epd.drawText(x + 4, 568, epd.WIDTH, 32, ALIGN_LEFT, text, 32)

def main():
    epd = init()
    drawBody(epd)
    drawFootbar(epd) 
    epd.refresh()
    epd.deepSleep(15000)
    
if __name__ == "__main__":
    main()
