#-*- coding:utf-8 -*-
# panel driver, based on https://www.good-display.cn/product/452.html
#
# Panel    : GDEQ0426T82 (800 x 480)
# IC       : SSD1677
#
# by dotnfc, 2023/10/24
#----------------------------------------------------------------

from micropython import const
from machine import SPI, Pin
from time import sleep_ms
import time
from framebuf import *
from logger import *
from board import *


BUSY = const(1)  # 1=busy, 0=idle

class EPD(FrameBuffer):
    # Display resolution
    WIDTH  = const(480)
    HEIGHT = const(800)
    BUF_SIZE = const(WIDTH * HEIGHT // 8)
    
    def __init__(self):
        self.spi = SPI(2, baudrate=20000000, polarity=0, phase=0, sck=EPD_PIN_SCK, mosi=EPD_PIN_SDA)
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
        super().__init__(self.buf, self.HEIGHT, self.WIDTH, MONO_HLSB)
       
    def _command(self, command, data=None):
        self.cs(1)
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
        self.cs(1)
        self.dc(1)
        self.cs(0)
        if isinstance(data, int):
            data = bytearray([data])
        self.spi.write(data)
        self.cs(1)
            
    def power_on(self):
        ...
        
    def power_off(self):
        ...
    
    def refresh(self, buf = None, full=True):
        '''Update screen contents.
        
        Args:
            - buf: dummy, only internal buffer
            - full: True if do full update, false for fast update
        '''        
        self._command(0x24)        
        self._data(self.buf)
        if full:
            self.update_full()
        else:
            self.update_fast()
        
    def init(self):
        self.init_full()
        
    def init_panel(self, reset=True):
        if reset:
            self.reset()

        self.wait_until_idle()
        self._command(0x12)  # SWRESET
        self.wait_until_idle()

        self._command(0x18, '\x80')

        self._command(0x0C, b'\xAE\xC7\xC3\xC0\x80')

        self._command(0x01)  # Driver output control
        self._data((self.WIDTH - 1) % 256)
        self._data((self.WIDTH - 1) // 256)
        self._data(0x02)

        self._command(0x3C, b'\x01')  # BorderWavefrom
        self._command(0x11, b'\x03')  # data entry mode

        self._command(0x44)  # set Ram-X address start/end position
        self._data(0x00)
        self._data(0x00)
        self._data((self.HEIGHT - 1) % 256)
        self._data((self.HEIGHT - 1) // 256)

        self._command(0x45)  # set Ram-Y address start/end position
        self._data(0x00)
        self._data(0x00)
        self._data((self.WIDTH - 1) % 256)
        self._data((self.WIDTH - 1) // 256)

        self._command(0x4E, b'\x00\x00')  # set RAM x address count to 0
        self._command(0x4F, b'\x00\x00')  # set RAM y address count to 0X199
        
        self.wait_until_idle()
        
    def init_full(self):
        self.init_panel()
        self.power_on()
        
    def init_partial(self):
        self.init_panel()
        self.power_on()
        
        # TEMP (1.5s)
        self._command(0x1A, b'x5A')

        self._command(0x22, b'\x91')
        self._command(0x20)

        self.wait_until_idle() 
        
    def update_full(self):
        self._command(0x22, b'\xF7') # Display Update Control
        self._command(0x20) # Activate Display Update Sequence
        self.wait_until_idle(5000)

    def update_partial(self):
        self._command(0x22, b'\xFF') # Display Update Control
        self._command(0x20) # Activate Display Update Sequence
        self.wait_until_idle(5000)

    def update_fast(self):
        self._command(0x22, b'\xC7') # Display Update Control
        self._command(0x20) # Activate Display Update Sequence
        self.wait_until_idle(5000)
        
    def wait_until_idle(self, timeout=5000):
            while self.busy.value() == BUSY:
                sleep_ms(100)
                timeout = timeout - 100
                if timeout <=0 :
                    raise RuntimeError("Timeout out for waiting busy signal")
       
    def reset(self):
        self.rst(0)
        sleep_ms(10)

        self.rst(1)
        sleep_ms(10)

    def sleep(self):
        self._command(0x10, 0x01)
        sleep_ms(100)
        
def main():
    BLACK = 0
    RED = 1
    WHITE = 3
    
    epd = EPD()
    epd.init()

    epd.fill(WHITE)
        
    epd.text('Hello world', 10, 60, BLACK)
    epd.line(0, 0, 799, 479, BLACK)
     
    _start = time.ticks_ms()
    epd.refresh()
    _stop = time.ticks_ms()
    print("time used: %d ms" % (_stop - _start))
    
    epd.sleep()
    
    pass

if __name__ == "__main__":
    main()
