#-*- coding:utf-8 -*-
# epd hardware demo
# by dotnfc, 2023/06/02

from micropython import const
from machine import SPI, Pin
from time import sleep_ms
import ustruct
from framebuf import *
import time
from efont import *
import qw_icons


# datasheet says 250x122 (increased to 128 to be multiples of 8)

# Display commands
DRIVER_OUTPUT_CONTROL                = const(0x01)
# Gate Driving Voltage Control       0x03
# Source Driving voltage Control     0x04
BOOSTER_SOFT_START_CONTROL           = const(0x0C) # not in datasheet
#GATE_SCAN_START_POSITION             = const(0x0F) # not in datasheet
DEEP_SLEEP_MODE                      = const(0x10)
DATA_ENTRY_MODE_SETTING              = const(0x11)
#SW_RESET                             = const(0x12)
#TEMPERATURE_SENSOR_CONTROL           = const(0x1A)
MASTER_ACTIVATION                    = const(0x20)
#DISPLAY_UPDATE_CONTROL_1             = const(0x21)
DISPLAY_UPDATE_CONTROL_2             = const(0x22)
# Panel Break Detection              0x23
WRITE_RAM                            = const(0x24)
WRITE_VCOM_REGISTER                  = const(0x2C)
# Status Bit Read                    0x2F
WRITE_LUT_REGISTER                   = const(0x32)
SET_DUMMY_LINE_PERIOD                = const(0x3A)
SET_GATE_TIME                        = const(0x3B)
#BORDER_WAVEFORM_CONTROL              = const(0x3C)
SET_RAM_X_ADDRESS_START_END_POSITION = const(0x44)
SET_RAM_Y_ADDRESS_START_END_POSITION = const(0x45)
SET_RAM_X_ADDRESS_COUNTER            = const(0x4E)
SET_RAM_Y_ADDRESS_COUNTER            = const(0x4F)
TERMINATE_FRAME_READ_WRITE           = const(0xFF) # not in datasheet, aka NOOP

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

        self.size = self.width * self.height // 8
        self.buf = bytearray(self.size)
        super().__init__(self.buf, self.WIDTH, self.HEIGHT, MONO_HLSB)
        
    LUT_FULL_UPDATE    = bytearray(b'\x80\x60\x40\x00\x00\x00\x00\x10\x60\x20\x00\x00\x00\x00\x80\x60\x40\x00\x00\x00\x00\x10\x60\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x03\x00\x00\x02\x09\x09\x00\x00\x02\x03\x03\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x15\x41\xA8\x32\x30\x0A')
    LUT_PARTIAL_UPDATE = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x40\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x15\x41\xA8\x32\x30\x0A')

    def clearBuffer(self):
        self._command(b'\x24')
        for i in range(0, len(self.buf)):
            self.buf[i] = 255
            self._data(bytearray([self.buf[i]]))

    def displayBuffer(self, buf = None):
        self._command(b'\x24')
        
        if buf is not None:
            for i in range(0, len(buf)):
                self._data(bytearray([buf[i]]))
        else:
            for i in range(0, len(self.buf)):
                self._data(bytearray([self.buf[i]]))
        self._command(b'\x22')
        self._command(b'\xC7')
        self._command(b'\x20')
        self._command(bytearray([TERMINATE_FRAME_READ_WRITE]))
        self.wait_until_idle()

    def _command(self, command, data=None):
        self.cs(1) # according to LOLIN_EPD
        self.dc(0)
        self.cs(0)
        self.spi.write(command)
        self.cs(1)
        if data is not None:
            self._data(data)

    def _data(self, data):
        self.cs(1) # according to LOLIN_EPD
        self.dc(1)
        self.cs(0)
        self.spi.write(data)
        self.cs(1)

    def init(self):
        self.reset()

        self.wait_until_idle()
        self._command(b'\x12'); # soft reset
        self.wait_until_idle()

        self._command(b'\x74', b'\x54'); #set analog block control
        self._command(b'\x7E', b'\x3B'); #set digital block control
        self._command(b'\x0f', b'\x00'); #set gate scan start position
        self._command(b'\x01', b'\x2b\x01\x00'); #Driver output control  ### CHANGED x00 to x01 ###
        self._command(b'\x11', b'\x03'); #data entry mode    ### CHANGED x01 to x00 ###
        #set Ram-X address start/end position
        self._command(b'\x44', b'\x00\x31'); #0x0C-->(31+1)*8=400
        #set Ram-Y address start/end position
        self._command(b'\x45', b'\x00\x00\x2b\x01'); # 0xF9-->(249+1)=250   ### CHANGED xF9 to x00 ###

        self._command(b'\x3C', b'\x03'); # BorderWavefrom
        self._command(b'\x2C', b'\x70'); # VCOM Voltage

        self._command(b'\x03', b'\x15'); # bytes([self.LUT_FULL_UPDATE[70]])); # ??

        self._command(b'\x04', b'\x41\xa8\x32'); # Source Driving voltage Control
        #self._data(bytes([self.LUT_FULL_UPDATE[71]])); # ??
        #self._data(bytes([self.LUT_FULL_UPDATE[72]])); # ??
        #self._data(bytes([self.LUT_FULL_UPDATE[73]])); # ??


        self._command(b'\x3A', b'\x30'); # bytes([self.LUT_FULL_UPDATE[74]])); # Dummy Line
        self._command(b'\x3B', b'\x0A'); # bytes([self.LUT_FULL_UPDATE[75]])); # Gate time

        self.set_lut(self.LUT_FULL_UPDATE)

        self._command(b'\x4E', b'\x00'); # set RAM x address count to 0;
        self._command(b'\x4F', b'\x00\x00'); # set RAM y address count to 0X127;
        self.wait_until_idle()

    def wait_until_idle(self):
            while self.busy.value() == BUSY:
                sleep_ms(100)

    def reset(self):
        self.rst(1)
        sleep_ms(1)

        self.rst(0)
        sleep_ms(10)

        self.rst(1)

    def set_lut(self, lut):
        self._command(bytearray([WRITE_LUT_REGISTER]), lut)

    # put an image in the frame memory
    def set_frame_memory(self, image, x, y, w, h):
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        x = x & 0xF8
        w = w & 0xF8

        if (x + w >= self.width):
            x_end = self.width - 1
        else:
            x_end = x + w - 1

        if (y + h >= self.height):
            y_end = self.height - 1
        else:
            y_end = y + h - 1

        self.set_memory_area(x, y, x_end, y_end)
        self.set_memory_pointer(x, y)
        self._command(bytearray([WRITE_RAM]), image)

    # replace the frame memory with the specified color
    def clear_frame_memory(self, color):
        self.set_memory_area(0, 0, self.width - 1, self.height - 1)
        self.set_memory_pointer(0, 0)
        self._command(bytearray([WRITE_RAM]))
        # send the color data
        for i in range(0, (self.width * self.height)//8):
            self._data(bytearray([color]))

    # draw the current frame memory and switch to the next memory area
    def display_frame(self):
        self._command(bytearray([DISPLAY_UPDATE_CONTROL_2]), b'\xC7')
        self._command(bytearray([MASTER_ACTIVATION]))
        self._command(bytearray([TERMINATE_FRAME_READ_WRITE]))
        self.wait_until_idle()

    # specify the memory area for data R/W
    def set_memory_area(self, x_start, y_start, x_end, y_end):
        self._command(bytearray([SET_RAM_X_ADDRESS_START_END_POSITION]))
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self._data(bytearray([(x_start >> 3) & 0xFF]))
        self._data(bytearray([(x_end >> 3) & 0xFF]))
        self._command(bytearray([SET_RAM_Y_ADDRESS_START_END_POSITION]), ustruct.pack("<HH", y_start, y_end))

    # specify the start point for data R/W
    def set_memory_pointer(self, x, y):
        self._command(bytearray([SET_RAM_X_ADDRESS_COUNTER]))
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self._data(bytearray([(x >> 3) & 0xFF]))
        self._command(bytearray([SET_RAM_Y_ADDRESS_COUNTER]), ustruct.pack("<H", y))
        self.wait_until_idle()

    # to wake call reset() or init()
    def sleep(self):
        self._command(bytearray([DEEP_SLEEP_MODE]))
        self.wait_until_idle()

def test_font():
    epd = EPD()
    epd.init()
    epd.clearBuffer()
   
    black = 0
    white = 1
    epd.fill(white)
    epd.text('Hello',0,20,black)
    epd.text('World',0,40,black)
    #epd.displayBuffer()
    
    #time.sleep(1.5)
    ico = FT2("font/qweather-icons.ttf", render=epd, size=32)
    ico.mono=True
    ff = FT2("font/simyou-lite.ttf", render=epd, size=16)
    ff.mono=True
    wqy = FT2("font/wenquanyi_12pt.pcf", render=epd, size=16)
    wqy.mono=True
    wqyb = FT2("font/wenquanyi_12ptb.pcf", render=epd, size=16)
    wqyb.mono=True

    epd.fill(white)
    
    ff.drawString(0, 50, 400, 24, ALIGN_CENTER, "你好世界！Hello World!", 24)

    ico.drawString(10, 100, 400, 32, ALIGN_LEFT, qw_icons.ICO_LOGO_NFC, 64)
    ico.drawString(80, 100, 400, 32, ALIGN_LEFT, qw_icons.ICO_LOGO_NFC, 48)
    ico.drawString(132, 100, 400, 32, ALIGN_LEFT, qw_icons.ICO_LOGO_NFC, 32)
    ico.drawString(170, 100, 400, 32, ALIGN_LEFT, qw_icons.ICO_LOGO_NFC, 16)
    
    wqy.drawString(10, 180, 200, 24, ALIGN_LEFT, "文泉驿点阵 16x16") # 你好世界 
    wqyb.drawString(10, 200, 200, 24, ALIGN_LEFT, "文泉驿点阵 16x16 粗体") # 你好世界 
    epd.displayBuffer()

def test_image():
    epd = EPD()
    epd.init()
    epd.clearBuffer()
   
    black = 0
    white = 1
    epd.fill(white)
    
    ima = Image(epd.WIDTH, epd.HEIGHT)
    
    ima.load("image/hello.png", True)
    print(f"w:{ima.width} h:{ima.height}")
    
    ima.draw(epd, 0, 0, 200, 200)
    epd.displayBuffer()
    
if __name__ == "__main__":
    test_font()
    #test_image()

