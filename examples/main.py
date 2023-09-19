import ujson as json
import urequests as requests
from epd_z98 import *
from efont import *
import gc

BLACK = const(0)
WHITE = const(1)

class EpdImage(EPD):
        
    def __init__(self):
        EPD.__init__(self)
        self.image = Image(self.width, self.height)
    
    def drawImage(self, x, y, filename):
        self.image.load(filename, True)
        self.image.draw(self, x, y)

def main():

    epd = EpdImage()
    epd.init()
    epd.clearBuffer()
    epd.fill(WHITE)
    
    font = FT2("font/simyou-lite.ttf", render=epd, mono=True,size=24)
    
    epd.fill(WHITE)
    epd.rect(2, 230, 230, 3, BLACK, True)
    #epd.drawImage(5, 238, "image/micropython.jpg")
    font.drawString(10, 10, 400, 32, ALIGN_LEFT, "2023-09-14")
        
    epd.displayBuffer()
    gc.collect()
    print("[epd after  darw1 ")

    epd.fill(WHITE)
    epd.rect(2, 230, 230, 3, BLACK, True)
    # font = FT2("font/simyou-lite.ttf", render=epd, size=24)
    
    print("[epd before darwtext 2 ")
    font.drawString(10, 10, 400, 32, ALIGN_LEFT, "2023-09-15")
    epd.displayBuffer()
    
if __name__ == "__main__":
    main()