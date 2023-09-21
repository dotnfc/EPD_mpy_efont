#-*- coding:utf-8 -*-
# panel driver
# FPC Label: WFH0420CZ11
# Panel    : WF0420T1PCZ11
# IC       : UC8154
# by dotnfc, 2023/09/20
#----------------------------------------------------------------

# image format
#   2-bit grayscale (4 grayscale), horizontal scanning (from left to right), and bottom to top (from bottom to top)
#   200x300 + 200x300 two images

from micropython import const
from machine import SPI, Pin
from time import sleep_ms
from framebuf import *


BUSY = const(1)  # 1=busy, 0=idle

class EPD(FrameBuffer):
    # Display resolution
    WIDTH  = const(400)
    HEIGHT = const(300)
    BUF_SIZE = const(WIDTH * HEIGHT // 8)
    
    def __init__(self):
        self.spi = SPI(2, baudrate=20000000, polarity=0, phase=0, sck=Pin(12), mosi=Pin(11))
        #self.spi = SPI(1, 10000000, sck=Pin(14), mosi=Pin(13), miso=Pin(12))
        self.spi.init()

        dc = Pin(14)
        cs = Pin(13)
        rst  = Pin(21)
        busy = Pin(47)
        
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.busy = busy
        
        self.cs.init(self.cs.OUT, value=1)
        self.dc.init(self.dc.OUT, value=0)
        self.rst.init(self.rst.OUT, value=0)
        self.busy.init(self.busy.IN)
        
        self.buf = bytearray(self.BUF_SIZE)
        super().__init__(self.buf, self.WIDTH, self.HEIGHT, GS2_HMSB)

    def _command(self, command, data=None):
        self.cs(1) # according to LOLIN_EPD
        self.dc(0)
        self.cs(0)
        if isinstance(command, int):
            command = bytearray([command])
        self.spi.write(command)
        self.cs(1)
        if data is not None:
            if isinstance(data, int):
                data = bytearray([data])
            self._data(data)

    def _data(self, data):
        self.cs(1) # according to LOLIN_EPD
        self.dc(1)
        self.cs(0)
        if isinstance(data, int):
            data = bytearray([data])
        self.spi.write(data)
        self.cs(1)
        
    def wait_until_idle(self):
            while self.busy.value() == BUSY:
                sleep_ms(100)

    def reset(self):
        self.rst(1)
        sleep_ms(10)

        self.rst(0)
        sleep_ms(10)

        self.rst(1)
        
def test_panel():
    pass

if __name__ == "__main__":
    test_panel()
