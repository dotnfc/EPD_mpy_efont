
# also works for black/white/yellow GDEW075C21?

from micropython import const
from machine import SPI, Pin
from time import sleep_ms
import ustruct
from framebuf import *
from logger import *
from board import *
import time

# Display commands
PANEL_SETTING                  = const(0x00)
POWER_SETTING                  = const(0x01)
POWER_OFF                      = const(0x02)
#POWER_OFF_SEQUENCE_SETTING     = const(0x03)
POWER_ON                       = const(0x04)
#POWER_ON_MEASURE               = const(0x05)
BOOSTER_SOFT_START             = const(0x06)
DEEP_SLEEP                     = const(0x07)
DATA_START_TRANSMISSION_1      = const(0x10)
#DATA_STOP                      = const(0x11)
DISPLAY_REFRESH                = const(0x12)
#IMAGE_PROCESS                  = const(0x13)
#LUT_FOR_VCOM                   = const(0x20)
#LUT_BLUE                       = const(0x21)
#LUT_WHITE                      = const(0x22)
#LUT_GRAY_1                     = const(0x23)
#LUT_GRAY_2                     = const(0x24)
#LUT_RED_0                      = const(0x25)
#LUT_RED_1                      = const(0x26)
#LUT_RED_2                      = const(0x27)
#LUT_RED_3                      = const(0x28)
#LUT_XON                        = const(0x29)
PLL_CONTROL                    = const(0x30)
#TEMPERATURE_SENSOR_COMMAND     = const(0x40)
TEMPERATURE_CALIBRATION        = const(0x41)
#TEMPERATURE_SENSOR_WRITE       = const(0x42)
#TEMPERATURE_SENSOR_READ        = const(0x43)
VCOM_AND_DATA_INTERVAL_SETTING = const(0x50)
#LOW_POWER_DETECTION            = const(0x51)
TCON_SETTING                   = const(0x60)
TCON_RESOLUTION                = const(0x61)
#SPI_FLASH_CONTROL              = const(0x65)
#REVISION                       = const(0x70)
#GET_STATUS                     = const(0x71)
#AUTO_MEASUREMENT_VCOM          = const(0x80)
#READ_VCOM_VALUE                = const(0x81)
VCM_DC_SETTING                 = const(0x82)
FLASH_MODE                     = const(0xE5)

BUSY = const(0)  # 0=busy, 1=idle

class EPD(FrameBuffer):
# Display resolution
    WIDTH  = const(640)
    HEIGHT = const(384)
    BUF_SIZE = const(WIDTH * HEIGHT // 4)
    
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
        super().__init__(self.buf, self.WIDTH, self.HEIGHT, GS2_HMSB)
        
    def _command(self, command, data=None):
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([command]))
        self.cs(1)
        if data is not None:
            self._data(data)

    def _data(self, data):
        self.dc(1)
        self.cs(0)
        self.spi.write(data)
        self.cs(1)

    def init(self):
        self.reset()
        self._command(POWER_SETTING, b'\x37\x00')
        self._command(PANEL_SETTING, b'\xCF\x08')
        self._command(BOOSTER_SOFT_START, b'\xC7\xCC\x28')
        self._command(POWER_ON)
        self.wait_until_idle()
        self._command(PLL_CONTROL, b'\x3C')
        self._command(TEMPERATURE_CALIBRATION, b'\x00')
        self._command(VCOM_AND_DATA_INTERVAL_SETTING, b'\x77')
        self._command(TCON_SETTING, b'\x22')
        self._command(TCON_RESOLUTION, ustruct.pack(">HH", self.WIDTH, self.HEIGHT))
        self._command(VCM_DC_SETTING, b'\x1E') # decide by LUT file
        self._command(FLASH_MODE, b'\x03')
        
    def wait_until_idle(self):
        while self.busy.value() == BUSY:
            sleep_ms(100)

    def reset(self):
        self.rst(0)
        sleep_ms(200)
        self.rst(1)
        sleep_ms(200)

    def msb_to_lsb(self, byte):
        lsb_byte = 0
        for i in range(8):
            lsb_byte = (lsb_byte << 1) | ((byte >> i) & 1)
        return lsb_byte

    # draw the current frame memory
    def display_frame(self):
   
        self._command(DATA_START_TRANSMISSION_1)
        data = []
        for i in range(0, self.BUF_SIZE):
            temp1 = self.buf[i] # bit-order: GS2_HMSB
            # temp1 = self.msb_to_lsb(self.buf[i])
            j = 0
            while (j < 4):
                if ((temp1 & 0x03) == 0x03):
                    temp2 = 0x03
                elif ((temp1 & 0xC0) == 0x00):
                    temp2 = 0x00
                else:
                    temp2 = 0x04
                temp2 = (temp2 << 4) & 0xFF
                temp1 = (temp1 >> 2) & 0xFF
                j += 1
                if ((temp1 & 0x03) == 0x03):
                    temp2 |= 0x03
                elif ((temp1 & 0xC0) == 0x00):
                    temp2 |= 0x00
                else:
                    temp2 |= 0x04
                temp1 = (temp1 >> 2) & 0xFF
                data.append(temp2)
                j += 1
        
        self._data(bytearray(data))
        self._command(DISPLAY_REFRESH)
        sleep_ms(100)
        self.wait_until_idle()

    # to wake call reset() or init()
    def sleep(self):
        self._command(POWER_OFF)
        self.wait_until_idle()
        self._command(DEEP_SLEEP, b'\xA5')

def main():
    black = 0
    red = 1
    white = 3
    
    epd = EPD()
    _start = time.ticks_ms()
    epd.init()
    _stop = time.ticks_ms()
    print("init used: %d ms" % (_stop - _start))
    
    _start = time.ticks_ms()
    epd.fill(white)
    _stop = time.ticks_ms()
    print("fill used: %d ms" % (_stop - _start))
    epd.text('Hello world', 10, 60, red)
    epd.line(0, 10, 380, 10, 0)
    
    _start = time.ticks_ms()
    epd.display_frame()
    _stop = time.ticks_ms()
    print("time used: %d ms" % (_stop - _start))
    
    
if __name__ == '__main__':

    main()