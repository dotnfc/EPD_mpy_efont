#-*- coding:utf-8 -*-
# epd sdl simulator 4.2' (400x300 black and white)
# by dotnfc, 2023/09/11

from .epd_sdl import * 
from framebuf import *

class FrameBufferEx(FrameBuffer):
    def __init__(self, buf, w, h, mode):
        super().__init__(buf, w, h, mode)

class Epd420BW(EpdSDLBase, FrameBuffer):
    
    def __init__(self, zoom = 1):
        self.WIDTH = 400
        self.HEIGHT = 300
        self.buf = bytearray(self.WIDTH * self.HEIGHT // 8)
        EpdSDLBase.__init__(self, self.WIDTH, self.HEIGHT, zoom)
        FrameBufferEx.__init__(self, self.buf, self.WIDTH, self.HEIGHT, MONO_HLSB)
        
    def init(self):
        pass
    
    def reset(self):
        pass
    
    def sleep(self):
        pass
    
    def clearBuffer(self, color=0xffff):
        self.fillBWRam(color)
        self.updateScreen()
        pass
    
    def displayBuffer(self, buf=None):
        if buf is None:
            buf = self.buf
        self.updateSubWindowBW(buf, 0, 0, self.WIDTH, self.HEIGHT)
        self.updateScreen()
        pass
