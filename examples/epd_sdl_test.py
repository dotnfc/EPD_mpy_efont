#-*- coding:utf-8 -*-
# epd test for unix port
# by dotnfc, 2023/09/11

from efont import *
from epd_sdl_420bw import *
import time
import gc

def testFT2():
    import qw_icons
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
    ff = FT2("font/simyou-lite.ttf", render=epd, size=16)
    ff.mono=True        

    ff.drawString(0, 50, 400, 24, ALIGN_CENTER, "2023-09-14")
    epd.displayBuffer()
    
    gc.collect()
    epd.fill(white)
    epd.rect(2, 230, 230, 2, black, True)
    ff.drawString(0, 50, 400, 24, ALIGN_CENTER, "2023-09-15")
    epd.displayBuffer()
    
    while(not epd.eventProcess()):
        time.sleep(0.01)
        
   
if __name__ == "__main__":
    testGC()
    #testFT2()
    # testImage("image/hello.png")

    pass