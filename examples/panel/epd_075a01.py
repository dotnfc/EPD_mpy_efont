#-*- coding:utf-8 -*-
# panel driver, referenced from GDEW0154T11
# FPC Label: HINK-E075A01-A8
# Panel    : GDEW075Z09 (640 x 384)
# IC       : IL0371
# Product  : Stellar-XXXL
# by dotnfc, 2023/09/20
#----------------------------------------------------------------

from micropython import const
from machine import SPI, Pin
from time import sleep_ms
from framebuf import *
from logger import *
from board import *
import struct

BUSY = const(0)  # 0=busy, 1=idle


# EPD7IN5 commands
PANEL_SETTING                               = 0x00
POWER_SETTING                               = 0x01
POWER_OFF                                   = 0x02
POWER_OFF_SEQUENCE_SETTING                  = 0x03
POWER_ON                                    = 0x04
POWER_ON_MEASURE                            = 0x05
BOOSTER_SOFT_START                          = 0x06
DEEP_SLEEP                                  = 0x07
DATA_START_TRANSMISSION_1                   = 0x10
DATA_STOP                                   = 0x11
DISPLAY_REFRESH                             = 0x12
IMAGE_PROCESS                               = 0x13
LUT_FOR_VCOM                                = 0x20
LUT_BLUE                                    = 0x21
LUT_WHITE                                   = 0x22
LUT_GRAY_1                                  = 0x23
LUT_GRAY_2                                  = 0x24
LUT_RED_0                                   = 0x25
LUT_RED_1                                   = 0x26
LUT_RED_2                                   = 0x27
LUT_RED_3                                   = 0x28
LUT_XON                                     = 0x29
PLL_CONTROL                                 = 0x30
TEMPERATURE_SENSOR_COMMAND                  = 0x40
TEMPERATURE_CALIBRATION                     = 0x41
TEMPERATURE_SENSOR_WRITE                    = 0x42
TEMPERATURE_SENSOR_READ                     = 0x43
VCOM_AND_DATA_INTERVAL_SETTING              = 0x50
LOW_POWER_DETECTION                         = 0x51
TCON_SETTING                                = 0x60
TCON_RESOLUTION                             = 0x61
SPI_FLASH_CONTROL                           = 0x65
REVISION                                    = 0x70
GET_STATUS                                  = 0x71
AUTO_MEASUREMENT_VCOM                       = 0x80
READ_VCOM_VALUE                             = 0x81
VCM_DC_SETTING                              = 0x82


class EPD(FrameBuffer):
    # Display resolution
    WIDTH  = const(640)
    HEIGHT = const(384)
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

    def conv_data(self, dat):
        '''Convert 8 bits to a short'''
        result = 0
        for bit_position in range(7, -1, -1):
            bit_value = (dat >> bit_position) & 1  # 获取当前位的值（0或1）
            if bit_value:
                result = result << 4 | 3
            else:
                result = result << 4
        return result
    
    def refresh(self, buf = None, full=True):
        '''Update screen contents.
        
        Args:
            - buf: the display contents to screen, can be none to use internal buffer
            - full: whether to update the entire screen, or just the partial of it
        '''
        
        pitch = self.WIDTH // 8
        cx = pitch

        startx = 0
        self.init_full()

        self._command(0x10)
        if buf is not None:
            for _ in range(self.HEIGHT):
                for x in range(0, cx):
                    dat = struct.pack('>I', self.conv_data(buf[startx + x]))        
                    self._data(dat)
                startx = startx + pitch
        else:
            for _ in range(self.HEIGHT):
                for x in range(0, cx):
                    dat = struct.pack('>I', self.conv_data(self.buf[startx + x]))
                    self._data(dat)
                startx = startx + pitch
        
        startx = 0
        if buf is not None:
            for _ in range(self.HEIGHT):
                for x in range(0, cx):
                    dat = struct.pack('>I', self.conv_data(buf[startx + x]))        
                    self._data(dat)
                startx = startx + pitch
        else:
            for _ in range(self.HEIGHT):
                for x in range(0, cx):
                    dat = struct.pack('>I', self.conv_data(self.buf[startx + x]))
                    self._data(dat)
                startx = startx + pitch
        if full:
            self.update_full()
        else:
            self.update_partial()
            
        self.wait_until_idle()
        
    def init(self):

        self.reset()

        self._command(POWER_SETTING)
        self._data(0x37)
        self._data(0x00)

        self._command(PANEL_SETTING)
        self._data(0xCF)
        self._data(0x08)

        self._command(BOOSTER_SOFT_START)
        self._data(0xc7)
        self._data(0xcc)
        self._data(0x28)

        self._command(POWER_ON)
        self.wait_until_idle()

        self._command(PLL_CONTROL)
        self._data(0x3c)

        self._command(TEMPERATURE_CALIBRATION)
        self._data(0x00)

        self._command(VCOM_AND_DATA_INTERVAL_SETTING)
        self._data(0x77)

        self._command(TCON_SETTING)
        self._data(0x22)

        self._command(TCON_RESOLUTION)
        self._data(0x02)     #source 640
        self._data(0x80)
        self._data(0x01)     #gate 384
        self._data(0x80)

        self._command(VCM_DC_SETTING)
        self._data(0x1E)      #decide by LUT file

        self._command(0xe5)           #FLASH MODE
        self._data(0x03)
    
    def init_full(self):
        self.init()
        
    def wait_until_idle(self, timeout=40000):
            while self.busy.value() == BUSY:
                sleep_ms(100)
                timeout = timeout - 100
                if timeout <=0 :
                    raise RuntimeError("Timeout out for waiting busy signal")

    def update_full(self):
        print("refresh before")
        self._command(DISPLAY_REFRESH)
        print("100ms before")
        sleep_ms(100)
        print("wait idle before")
        self.wait_until_idle()
        print("wait idle after")
        
    def reset(self):
        self.rst(1)
        sleep_ms(20)

        self.rst(0)
        sleep_ms(200)

        self.rst(1)
        sleep_ms(200)
        
    def power_off(self):
        self._command(POWER_OFF) 
        self.wait_until_idle()
        
    def sleep(self):
        self.power_off()        
        self._command(DEEP_SLEEP, 0xa5)
        
def main():
    import time
    epd = EPD()
    epd.init()
    
    epd.fill(1)
    epd.text('Hello world', 10, 60, 0)
    
    epd.line(0, 10, 380, 10, 0)
    
    epd.refresh()
    pass

if __name__ == "__main__":
    main()
