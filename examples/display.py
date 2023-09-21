
import sys
if sys.platform == 'linux':
    from panel.epd_sdl_420bw import *
else:
    from panel.epd_z96 import *
    
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

    def deepsleep(self, microseconds):
        '''deep sleep for microseconds'''
        if sys.platform == "linux":
            print("sys deepsleep")
            while(not self.eventProcess()):
                time.sleep(0.01)
        else:
            machine.deepsleep(microseconds)