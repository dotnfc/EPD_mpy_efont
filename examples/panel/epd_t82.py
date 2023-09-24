#-*- coding:utf-8 -*-
#----------------------------------------------------------------
#
# panel: GDEQ0426T82 | SSD1677
#
# by dotnfc, 2023/09/20
#

from micropython import const
from machine import SPI, Pin
from time import sleep_ms
from framebuf import *
import time
from logger import *
from board import *

BUSY = const(1)  # 1=busy, 0=idle

class EPD(FrameBuffer):
    # Display resolution
    WIDTH  = const(400)
    HEIGHT = const(300)
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
        
        self.self.width = self.self.WIDTH
        self.height = self.HEIGHT

        self.size = self.self.WIDTH * self.HEIGHT // 8
        self.buf = bytearray(self.size)
        super().__init__(self.buf, self.self.WIDTH, self.HEIGHT, MONO_HLSB)

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
        
    # Full screen refresh initialization
    def EPD_HW_Init(self):
        self.reset()
    
        self.wait_until_idle()   
        self._command(0x12)  # SWRESET
        self.wait_until_idle()   

        self._command(0x18)   
        self._data(0x80) 
    
        self._command(0x0C)
        self._data(0xAE)
        self._data(0xC7)
        self._data(0xC3)
        self._data(0xC0)
        self._data(0x80)
    
        self._command(0x01)  # Driver output control      
        self._data((self.WIDTH-1) % 256)    
        self._data((self.WIDTH-1) // 256)
        self._data(0x02) 

        self._command(0x3C)  # BorderWavefrom
        self._data(0x01)  
    
        self._command(0x11)  # Data entry mode       
        self._data(0x03)

        self._command(0x44)  # Set Ram-X address start/end position   
        self._data(0x00)
        self._data(0x00)
        self._data((self.HEIGHT-1) % 256)   
        self._data((self.HEIGHT-1) // 256)

        self._command(0x45)  # Set Ram-Y address start/end position          
        self._data(0x00)
        self._data(0x00) 
        self._data((self.WIDTH-1) % 256)   
        self._data((self.WIDTH-1) // 256)

        self._command(0x4E)   # Set RAM x address count to 0;
        self._data(0x00)
        self._data(0x00)
        self._command(0x4F)   # Set RAM y address count to 0X199;    
        self._data(0x00)
        self._data(0x00)
        self.wait_until_idle()

    # Fast refresh 1 initialization
    def EPD_HW_Init_Fast(self):
        self.reset()
    
        self.wait_until_idle()   
        self._command(0x12)  # SWRESET
        self.wait_until_idle()   

        self._command(0x18)   
        self._data(0x80) 
    
        self._command(0x0C)
        self._data(0xAE)
        self._data(0xC7)
        self._data(0xC3)
        self._data(0xC0)
        self._data(0x80)
    
        self._command(0x01)  # Driver output control      
        self._data((self.WIDTH-1) % 256)   
        self._data((self.WIDTH-1) // 256)
        self._data(0x02)

        self._command(0x3C)  # BorderWavefrom
        self._data(0x01)  
    
        self._command(0x11)  # Data entry mode       
        self._data(0x03)

        self._command(0x44)  # Set Ram-X address start/end position   
        self._data(0x00)
        self._data(0x00)
        self._data((self.HEIGHT-1) % 256)    
        self._data((self.HEIGHT-1) // 256)

        self._command(0x45)  # Set Ram-Y address start/end position          
        self._data(0x00)
        self._data(0x00) 
        self._data((self.WIDTH-1) % 256)    
        self._data((self.WIDTH-1) // 256)

        self._command(0x4E)   # Set RAM x address count to 0;
        self._data(0x00)
        self._data(0x00)
        self._command(0x4F)   # Set RAM y address count to 0X199;    
        self._data(0x00)
        self._data(0x00)
        self.wait_until_idle()

        # TEMP (1.5s)
        self._command(0x1A) 
        self._data(0x5A)

        self._command(0x22) 
        self._data(0x91)
        self._command(0x20)

        self.wait_until_idle()  

    # Display Update Function
    # Full screen refresh update function
    def EPD_Update(self):   
        self._command(0x22)  # Display Update Control
        self._data(0xF7)   
        self._command(0x20)  # Activate Display Update Sequence
        self.wait_until_idle()   

    # Fast refresh 1 update function
    def EPD_Update_Fast(self):   
        self._command(0x22)  # Display Update Control
        self._data(0xC7)   
        self._command(0x20)  # Activate Display Update Sequence
        self.wait_until_idle()   

    # Partial refresh update function
    def EPD_Part_Update(self):
        self._command(0x22)  # Display Update Control
        self._data(0xFF)   
        self._command(0x20)  # Activate Display Update Sequence
        self.wait_until_idle()

    # Full screen refresh display function
    def EPD_WhiteScreen_ALL(self, datas):
        self._command(0x24)  # Write RAM for black(0)/white (1)
        for data in datas:
            self._data(data)
        self.EPD_Update()

    # Fast refresh display function
    def EPD_WhiteScreen_ALL_Fast(self, datas):
        self._command(0x24)  # Write RAM for black(0)/white (1)
        for data in datas:
            self._data(data)
        self.EPD_Update_Fast()

    # Clear screen display
    def EPD_WhiteScreen_White(self):
        self._command(0x24)  # Write RAM for black(0)/white (1)
        for _ in range(self.BUF_SIZE):
            self._data(0xFF)
        self.EPD_Update()

    # Display all black
    def EPD_WhiteScreen_Black(self):
        self._command(0x24)  # Write RAM for black(0)/white (1)
        for _ in range(self.BUF_SIZE):
            self._data(0x00)
        self.EPD_Update()

    # Partial refresh of background display, this function is necessary, please do not delete it!!!
    def EPD_SetRAMValue_BaseMap(self, datas):
        self._command(0x24)  # Write Black and White image to RAM
        for data in datas:
            self._data(data)
        
        self._command(0x26)  # Write Black and White image to RAM
        for data in datas:
            self._data(data)
        
        self.EPD_Update()

    # Partial refresh display
    def EPD_Dis_Part(self, x_start, y_start, datas, PART_COLUMN, PART_LINE):
        x_start = x_start - x_start % 8  # x address start
        x_end = x_start + PART_LINE - 1  # x address end
        y_start = y_start  # Y address start
        y_end = y_start + PART_COLUMN - 1  # Y address end

        # Reset
        self.reset()

        self._command(0x18)
        self._data(0x80)

        self._command(0x3C)  # BorderWavefrom
        self._data(0x80)

        self._command(0x44)  # set RAM x address start/end
        self._data(x_start % 256)  # x address start2
        self._data(x_start // 256)  # x address start1
        self._data(x_end % 256)  # x address end2
        self._data(x_end // 256)  # x address end1
        self._command(0x45)  # set RAM y address start/end
        self._data(y_start % 256)  # y address start2
        self._data(y_start // 256)  # y address start1
        self._data(y_end % 256)  # y address end2
        self._data(y_end // 256)  # y address end1

        self._command(0x4E)  # set RAM x address count to 0
        self._data(x_start % 256)  # x address start2
        self._data(x_start // 256)  # x address start1
        self._command(0x4F)  # set RAM y address count to 0X127
        self._data(y_start % 256)  # y address start2
        self._data(y_start // 256)  # y address start1

        self._command(0x24)  # Write Black and White image to RAM
        for i in range(len(datas)):
            self._data(datas[i])
        
        self.EPD_Part_Update()

    # Full screen partial refresh display
    def EPD_Dis_PartAll(self, datas):
        PART_COLUMN = self.HEIGHT
        PART_LINE = self.WIDTH

        # Reset
        self.reset()

        self._command(0x18)
        self._data(0x80)

        self._command(0x3C)  # BorderWavefrom
        self._data(0x80)

        self._command(0x24)  # Write Black and White image to RAM
        for i in range(len(datas)):
            self._data(datas[i])

        self.EPD_Part_Update()

    def deepsleep(self):
        self._command(0x10)  # Enter deep sleep
        self._data(0x01)
        time.sleep(0.1)

    # Partial refresh write address and data
    def EPD_Dis_Part_RAM(self, x_start, y_start, datas, PART_COLUMN, PART_LINE):
        x_start = x_start - x_start % 8  # x address start
        x_end = x_start + PART_LINE - 1  # x address end
        y_start = y_start  # Y address start
        y_end = y_start + PART_COLUMN - 1  # Y address end

        # Reset
        self.reset()

        self._command(0x18)
        self._data(0x80)

        self._command(0x3C)  # BorderWavefrom
        self._data(0x80)

        self._command(0x44)  # set RAM x address start/end
        self._data(x_start % 256)  # x address start2
        self._data(x_start // 256)  # x address start1
        self._data(x_end % 256)  # x address end2
        self._data(x_end // 256)  # x address end1
        self._command(0x45)  # set RAM y address start/end
        self._data(y_start % 256)  # y address start2
        self._data(y_start // 256)  # y address start1
        self._data(y_end % 256)  # y address end2
        self._data(y_end // 256)  # y address end1

        self._command(0x4E)  # set RAM x address count to 0
        self._data(x_start % 256)  # x address start2
        self._data(x_start // 256)  # x address start1
        self._command(0x4F)  # set RAM y address count to 0X127
        self._data(y_start % 256)  # y address start2
        self._data(y_start // 256)  # y address start1

        self._command(0x24)  # Write Black and White image to RAM
        for i in range(len(datas)):
            self._data(datas[i])

    # Display rotation 180 degrees initialization
    def EPD_HW_Init_180(self):
        # Module reset
        self.reset()

        self.wait_until_idle()
        self._command(0x12)  # SWRESET
        self.wait_until_idle()

        self._command(0x18)
        self._data(0x80)

        self._command(0x0C)
        self._data(0xAE)
        self._data(0xC7)
        self._data(0xC3)
        self._data(0xC0)
        self._data(0x80)

        self._command(0x01)  # Driver output control
        self._data((self.WIDTH - 1) % 256)
        self._data((self.WIDTH - 1) // 256)
        self._data(0x02)

        self._command(0x3C)  # BorderWavefrom
        self._data(0x01)

        self._command(0x11)  # data entry mode
        self._data(0x00)  # 180

        self._command(0x44)  # set Ram-X address start/end position

        self._data((self.HEIGHT - 1) % 256)
        self._data((self.HEIGHT - 1) // 256)
        self._data(0x00)
        self._data(0x00)

        self._command(0x45)  # set Ram-Y address start/end position
        self._data((self.WIDTH - 1) % 256)
        self._data((self.WIDTH - 1) // 256)
        self._data(0x00)
        self._data(0x00)

        self._command(0x4E)  # set RAM x address count to 0;
        self._data(0x00)
        self._data(0x00)
        self._command(0x4F)  # set RAM y address count to 0X199;
        self._data(0x00)
        self._data(0x00)
        self.wait_until_idle()


def test_panel():
    pass

if __name__ == "__main__":
    test_panel()