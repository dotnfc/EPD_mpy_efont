#-*- coding:utf-8 -*-
#----------------------------------------------------------------
#
# demo script for eFont
#
# by dotnfc, 2023/06/02
#
from display import *
from efont import *
from qw_icons import *

def main():
    epd = EpdImage()
    epd.init()
   
    black = 0
    white = 1
    epd.fill(white)
    epd.text('Hello',0,20,black)
    epd.text('World',0,40,black)
    #epd.refresh()
    
    #time.sleep(1.5)
    ico = FT2("font/qweather-icons.ttf", render=epd, size=32)
    ico.mono=True
    ff = FT2("font/simyou-lite.ttf", render=epd, size=16)
    ff.mono=True
    wqy = FT2("font/wenquanyi_12pt.pcf", render=epd, size=16)
    wqy.mono=True
    wqyb = FT2("font/wenquanyi_12ptb.pcf", render=epd, size=16)
    wqyb.mono=True

    epd.fill(white)
    
    ff.drawString(0, 50, 400, 24, ALIGN_CENTER, "你好世界！Hello World!", 24)

    ico.drawString(10, 100, 400, 32, ALIGN_LEFT, ICO_LOGO_NFC, 64)
    ico.drawString(80, 100, 400, 32, ALIGN_LEFT, ICO_LOGO_NFC, 48)
    ico.drawString(132, 100, 400, 32, ALIGN_LEFT, ICO_LOGO_NFC, 32)
    ico.drawString(170, 100, 400, 32, ALIGN_LEFT, ICO_LOGO_NFC, 16)
    
    wqy.drawString(10, 180, 200, 24, ALIGN_LEFT, "文泉驿点阵 16x16") # 你好世界 
    wqyb.drawString(10, 200, 200, 24, ALIGN_LEFT, "文泉驿点阵 16x16 粗体") # 你好世界 
    epd.refresh()
    epd.deepsleep(15000)
    
if __name__ == "__main__":
    main()
