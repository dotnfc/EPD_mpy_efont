#-*- coding:utf-8 -*-
#----------------------------------------------------------------
#
# monochrome epd with image support, based on frameBuffer
#
# by dotnfc, 2023/09/22
#

import sys
if sys.platform == 'linux':
    from panel.epd_sdl_420bw import *
else:
    # from panel.epd_z96 import *
    # from panel.epd_z98 import *
    # from panel.epd_cz11 import *
    from panel.epd_075a01 import *
    # from panel.epd_102a012c import *
    
from efont import *
import machine
import time

BLACK = const(0)
WHITE = const(1)

class EpdImage(EPD):
        
    def __init__(self):
        EPD.__init__(self)
        self.image = Image(self.WIDTH, self.HEIGHT)
    
    def drawImage(self, x, y, filename):
        '''Draw image file at (x, y).'''
        self.image.load(filename, True)
        self.image.draw(self, x, y)

    def deepSleep(self, microseconds):
        '''deep sleep for microseconds'''
        if sys.platform == "linux":
            print("sys deep sleep")
            while(not self.eventProcess()):
                time.sleep(0.01)
        else:
            machine.deepsleep(microseconds)