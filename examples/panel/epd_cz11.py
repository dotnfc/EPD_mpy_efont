#-*- coding:utf-8 -*-
# panel driver, referenced from GDEW0154T11
# FPC Label: WFH0420CZ11
# Panel    : WF0420T1PCZ11
# IC       : UC8154
# Product  : Stellar-XL
# by dotnfc, 2023/09/20
#----------------------------------------------------------------

# image format
#   2-bit grayscale (4 grayscale), horizontal scanning (from left to right), and bottom to top (from bottom to top)
#   200x300 + 200x300 two images

from micropython import const
from machine import SPI, Pin
from time import sleep_ms
from framebuf import *
from logger import *
from board import *
import struct

BUSY = const(0)  # 0=busy, 1=idle

class EPD(FrameBuffer):
    # Display resolution
    WIDTH  = const(400)
    HEIGHT = const(300)
    BUF_SIZE = const(WIDTH * HEIGHT // 8)
    
    def __init__(self):
        self.spi = SPI(2, baudrate=20000000, polarity=0, phase=0, sck=EPD_PIN_SCK, mosi=EPD_PIN_SDA)
        self.spi.init()
        
        self.cs  = EPD_PIN_CS
        self.cs2 = EPD_PIN_CS2
        self.dc  = EPD_PIN_DC
        self.rst = EPD_PIN_RST
        self.busy = EPD_PIN_BUSY
        
        self.cs.init(self.cs.OUT, value=1)
        self.cs2.init(self.cs2.OUT, value=1)
        self.dc.init(self.dc.OUT, value=0)
        self.rst.init(self.rst.OUT, value=0)
        self.busy.init(self.busy.IN)

        self.buf = bytearray(self.BUF_SIZE)
        super().__init__(self.buf, self.WIDTH, self.HEIGHT, MONO_HLSB)
        
    # lut standard
    LUT_VCOM0 = bytearray(b'\x02\x03\x03\x08\x08\x03\x05\x05\x03\x00\x00\x00\x00\x00\x00')
    LUT_W = bytearray(b'\x42\x43\x03\x48\x88\x03\x85\x08\x03\x00\x00\x00\x00\x00\x00')
    LUT_B = bytearray(b'\x82\x83\x03\x48\x88\x03\x05\x45\x03\x00\x00\x00\x00\x00\x00')
    LUT_G1 = bytearray(b'\x82\x83\x03\x48\x88\x03\x05\x45\x03\x00\x00\x00\x00\x00\x00')
    LUT_G2 = bytearray(b'\x82\x83\x03\x48\x88\x03\x05\x45\x03\x00\x00\x00\x00\x00\x00')

    # lut from firmware
    # LUT_VCOM0 = bytearray(b'\x19\x1e\x04\x28\x28\x05\x1e\x19\x04\x00\x00\x00\x00\x00\x00')
    # LUT_W = bytearray(b'\x19\x5e\x04\xa8\x68\x05\x9e\x19\x04\x00\x00\x00\x00\x00\x00')
    # LUT_B = bytearray(b'\x99\x9e\x04\xa8\x68\x05\x5e\x59\x04\x00\x00\x00\x00\x00\x00')
    # LUT_G1 = bytearray(b'\x99\x9e\x04\xa8\x68\x05\x5e\x59\x04\x00\x00\x00\x00\x00\x00')
    # LUT_G2 = bytearray(b'\x99\x9e\x04\xa8\x68\x05\x5e\x59\x04\x00\x00\x00\x00\x00\x00')
    
    def conv_data(self, dat):
        '''Convert 8 bits to a short'''
        result = 0
        for bit_position in range(7, -1, -1):
            bit_value = (dat >> bit_position) & 1  # 获取当前位的值（0或1）
            if bit_value:
                result = result << 2
            else:
                result = result << 2 | 3
        return result
    
    def refresh(self, buf = None, full=True):
        '''Update screen contents.
        
        Args:
            - buf: the display contents to screen, can be none to use internal buffer
            - full: whether to update the entire screen, or just the partial of it
        '''
        
        pitch = self.WIDTH // 8
        cx = pitch // 2

        startx = 0
        self.init_full()

        self._command(0x10)
        if buf is not None:
            for _ in range(self.HEIGHT):
                for x in range(0, cx):
                    self._datax(buf[startx + x], True)   # to ic1
                for x in range(cx, pitch):
                    self._datax(buf[startx + x], False)  # to ic2
                
                startx = startx + pitch
        else:
            for _ in range(self.HEIGHT):
                for x in range(0, cx):
                    self._datax(self.buf[startx + x], True)   # to ic1
                for x in range(cx, pitch):
                    self._datax(self.buf[startx + x], False)  # to ic2
                
                startx = startx + pitch
                
        if full:
            self.update_full()
        else:
            self.update_partial()
            
        self.wait_until_idle()

    def _command(self, command, data=None):        
        # command sequence
        self.cs(0)
        self.cs2(0)
        self.dc(0)
        
        if isinstance(command, int):
            command = bytearray([command])
        self.spi.write(command)
        
        self.cs(1)
        self.cs2(1)
        
        # now optional data
        if data is not None:
            if isinstance(data, int):
                data = bytearray([data])
            self._data(data)

        self.cs(1)
        self.cs2(1)
        
    def _data(self, data):
        # data sequence
        self.cs(0)
        self.cs2(0)
        self.dc(1)
        
        if isinstance(data, int):
            data = bytearray([data])
        self.spi.write(data)
        
        self.cs(1)
        self.cs2(1)
        
    def _datax(self, data, cs1=True):
        '''Write a byte to the panel'''
        # data sequence
        if cs1:
            self.cs(0)
            self.cs2(1)
        else:
            self.cs(1)
            self.cs2(0)

        self.dc(1)
        
        # caller is responsible for making sure: data is integer
        # if not isinstance(data, int):
        #    raise ValueError('data must be an integer')
        
        # convert data to a 4 grayscale format, in BigEndian format
        self.spi.write(struct.pack('>h', self.conv_data(data)))
        
        self.cs(1)
        self.cs2(1)

    def power_on(self):
        self._command(0x04)
        self.wait_until_idle()
        
    def power_off(self):
        self._command(0x02)
        self.wait_until_idle()
        
    def init(self):
        self.init_full()
        
    def init_panel(self, reset=True):
        if reset:
            self.reset()

        self._command(0x01, b'\x07\x00\x0d\x00'); # power setting
        self.power_on()
        
        self._command(0x00, 0xdf); # panel setting: df-bw cf-r
        self._command(0x50, 0x67); # VCOM AND DATA INTERVAL SETTING
        self._command(0x30, 0x2a); # PLL setting
        
        self._command(0x61, b'\xc8\x01\x2c'); # resolution setting
        
        self._command(0x82, 0x0A); # vcom setting
        
    def init_full(self):
        self.init_panel()
        
        self._command(0x20, self.LUT_VCOM0)
        self._command(0x21, self.LUT_W)
        self._command(0x22, self.LUT_B)
        self._command(0x23, self.LUT_G1)
        self._command(0x24, self.LUT_G2)
            
    def init_partial(self):
        self.init_panel(False)
        self._command(0x20, self.LUT_VCOM0)
        self._command(0x21, self.LUT_W)
        self._command(0x22, self.LUT_B)
        self._command(0x23, self.LUT_G1)
        self._command(0x24, self.LUT_G2)
        
    def update_full(self):
        self._command(0xe0, 0x01)   # CASCADE SETTING (CCSET) 0xe0
        self._command(0x12)         # DISPLAY REFRESH (DRF) (R12H)
        sleep_ms(10)
        self.wait_until_idle()

    def update_partial(self):
        self._command(0xe0, 0x01)   # CASCADE SETTING (CCSET) 0xe0
        self._command(0x12)         # DISPLAY REFRESH (DRF) (R12H)
        sleep_ms(100)
        self.wait_until_idle()
        
    def wait_until_idle(self, timeout=4000):
            while self.busy.value() == BUSY:
                sleep_ms(100)
                timeout = timeout - 100
                if timeout <=0 :
                    raise RuntimeError("Timeout out for waiting busy signal")

    def reset(self):
        self.rst(1)
        sleep_ms(10)

        self.rst(0)
        sleep_ms(10)

        self.rst(1)
        sleep_ms(10)

    # specify the memory area for data R/W
    def set_memory_area(self, x_start, y_start, x_end, y_end):
        # self._command(0x11); # set ram entry mode
        # self._data(0x03);    # x increase, y increase : normal mode
  
        # # x point must be the multiple of 8 or the last 3 bits will be ignored
        # self._command(0x44)
        # self._data(x_start // 8)
        # self._data((x_start + x_end - 1) // 8)
        
        # self._command(0x45)
        # self._data(y_start % 256)
        # self._data(y_start // 256)
        # self._data((y_start + y_end - 1) % 256)
        # self._data((y_start + y_end - 1) // 256)
        
        # self._command(0x4e)
        # self._data(x_start // 8)
        # self._command(0x4f)
        # self._data(y_start % 256)
        # self._data(y_start // 256)

        # self.wait_until_idle()
        pass
    
    # to wakeup panel, just call reset() or init()
    def sleep(self):
        self.power_off()
        self._command(0x82, 0x00) # VCOM_DC SETTING (VDCS) (R82H)
        
        self._data(0x01, b'\x02\x00\x00\x00') # POWER SETTING (PWR) (R01H) , gate switch to external
        sleep_ms(100)
        self.power_off()
        #self.wait_until_idle()

def main():
    import time
    epd = EPD()
    epd.init()
    
    epd.fill(1)
    epd.text('Hello world', 10, 60, 0)
    
    epd.line(0, 10, 380, 10, 1)
    
    epd.refresh()
    #time.sleep(1)

    #epd.text('dotnfc here', 0, 10, 0)
    #epd.refresh(full=False)
    
    # epd.sleep()

if __name__ == "__main__":
    main()

