#-*- coding:utf-8 -*-
# epd hardware demo
# by dotnfc, 2023/06/02

from micropython import const
from machine import SPI, Pin
from time import sleep_ms
from framebuf import *

BUSY = const(1)  # 1=busy, 0=idle

class EPD(FrameBuffer):
    # Display resolution
    WIDTH  = const(400)
    HEIGHT = const(300)
    
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
        
        self.width = self.WIDTH
        self.height = self.HEIGHT

        self.size = self.WIDTH * self.HEIGHT // 8
        self.buf = bytearray(self.size)
        super().__init__(self.buf, self.WIDTH, self.HEIGHT, MONO_HLSB)
        
    LUT_FULL_UPDATE = bytearray(b'\x01\x05\x00\x00\x05\x01\x01\x03\x06\x06\x06\x06\x01\x01\x01\x00\x00\x15\x20\x01\x01\x01\x35\x00\x00\x00\x01\x00\x02\x05\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x05\x00\x00\x05\x01\x01\x03\x46\x86\x46\x86\x01\x01\x01\x00\x00\x15\xa0\x01\x01\x01\x35\x00\x00\x00\x01\x00\x02\x05\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x05\x00\x00\x05\x01\x01\x03\x46\x86\x46\x86\x01\x01\x01\x00\x00\x95\x20\x01\x01\x01\x75\x00\x00\x00\x01\x00\x02\x05\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x05\x00\x00\x05\x01\x01\x03\x46\x86\x46\x86\x01\x01\x01\x00\x00\x15\xa0\x01\x01\x01\x35\x00\x00\x00\x01\x00\x02\x05\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x05\x00\x00\x05\x01\x01\x03\x46\x86\x46\x86\x01\x01\x01\x00\x00\x95\x20\x01\x01\x01\x75\x00\x00\x00\x01\x00\x02\x05\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04')
    LUT_PARTIAL_UPDATE = bytearray(b'\x01\x19\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x59\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x99\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04')

    def clearBuffer(self, color=255):
        for i in range(0, len(self.buf)):
            self.buf[i] = color

    def displayBuffer(self, buf = None):
        self._command(0x24)
        
        if buf is not None:
            self._data(buf)
        else:
            self._data(self.buf)

        self._command(0x26)
        if buf is not None:
            self._data(buf)
        else:
            self._data(self.buf)

        self._command(0x22)
        self._data(0xcf)
        self._command(0x20)
        self.wait_until_idle()

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

    def powerOn(self):
        self._command(0x22)
        self._data(0xc0)
        self._command(0x20)
        self.wait_until_idle()
        
    def init(self):
        self.reset()
        self.wait_until_idle()
        
        self._command(0x12); # soft reset
        self.wait_until_idle()

        self._command(0x01, b'\x2B\x01\x00')  # Set MUX as 300
        
        self._command(0x3C)  # BorderWavefrom
        self._data(0x01)
        
        self._command(0x2C)  # VCOM Voltage
        self._data(0x4b)
        
        self._command(0x03)  # Gate Driving voltage Control
        self._data(0x13)     # 19V

        self._command(0x04, b'\x3c\xa3\x2e')  # Gate Driving voltage Control
        
        self._command(0x11, 0x01)  # Data entry mode
        
        self._command(0x18)
        self._data(0X80)
        
        self.set_lut(self.LUT_FULL_UPDATE)
        
        self._command(0x11, 0x03)  # Data entry mode
        
        self.set_memory_area(0, 0, self.WIDTH, self.HEIGHT)
        self.wait_until_idle()
        self.powerOn()
        
    def wait_until_idle(self):
            while self.busy.value() == BUSY:
                sleep_ms(100)

    def set_lut(self, lut):
        self._command(0x32, lut)
        
    def reset(self):
        self.rst(1)
        sleep_ms(1)

        self.rst(0)
        sleep_ms(10)

        self.rst(1)

    # specify the memory area for data R/W
    def set_memory_area(self, x_start, y_start, x_end, y_end):
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self._command(0x44)
        self._data(x_start // 8)
        self._data((x_start + x_end - 1) // 8)
        
        self._command(0x45)
        self._data(y_start % 256)
        self._data(y_start // 256)
        self._data((y_start + y_end - 1) % 256)
        self._data((y_start + y_end - 1) // 256)
        self._command(0x4e)
        self._data(x_start // 8)
        self._command(0x4f)
        self._data(y_start % 256)
        self._data(y_start // 256)

    # to wake call reset() or init()
    def sleep(self):
        self._command(0x10)
        self._data(0x01)
        #self.wait_until_idle()


def main():
    epd = EPD()
    epd.init()
    epd.fill(1)
    epd.text('Hello world', 0, 20, 0)
    epd.displayBuffer()
        
if __name__ == "__main__":
    main()