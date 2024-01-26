#-*- coding:utf-8 -*-
# GDEQ0426T82 panel driver
# by dotnfc, 2023/09/20

from micropython import const
from machine import SPI, Pin
from time import sleep_ms
from framebuf import *
from logger import *
from board import *

BUSY = const(1)  # 1=busy, 0=idle

class EPD(FrameBuffer):
    # Display resolution
    WIDTH  = const(400)
    HEIGHT = const(300)
    BUF_SIZE = const(WIDTH * HEIGHT // 8)
    
    def __init__(self):
        self.spi = SPI(1, baudrate=20000000, polarity=0, phase=0, sck=EPD_PIN_SCK, mosi=EPD_PIN_SDA)
        self.spi.init()
        
        self.cs = EPD_PIN_CS
        self.dc = EPD_PIN_DC
        self.rst = EPD_PIN_RST
        self.busy = EPD_PIN_BUSY
        
        self.cs.init(self.cs.OUT, value=1)
        self.dc.init(self.dc.OUT, value=0)
        self.rst.init(self.rst.OUT, value=0)
        self.busy.init(self.busy.IN)
        
        self.width = self.WIDTH
        self.height = self.HEIGHT

        self.buf = bytearray(self.BUF_SIZE)
        super().__init__(self.buf, self.WIDTH, self.HEIGHT, MONO_HLSB)

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
