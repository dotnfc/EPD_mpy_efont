__author__ = 'dotnfc'


ALIGN_LEFT = 0    # Left alignment
ALIGN_RIGHT = 1   # Right alignment
ALIGN_CENTER = 2  # Center alignment

class FT2(object):
    """
    A FreeType2 Wrapper class
    """
    mono = False   # monochrome drawing for EPD
    bold = False   # bold style when drawing
    italic = False # italic style when drawing
    
    def __init__(file: str,
             render: framebuf.FrameBuffer,
             size: int = 16,
             mono: bool = False,
             bold: bool = False,
             italic: bool = False):
        ''' 
        @brief Load font from file(.ttf, .pcf)
        @param file, file path to load
        @param render, an instance of framebuf.FrameBuffer which pixel() method will be called when self.drawString()
        @param size, default size to draw text
        @param mono, true for loading as mono font for EPD
        @param bold, bold style to draw text
        @param italic, italic style to draw text
        @return True if font was loaded
        '''
        pass
    
    def unload(self):
        '''@Unload font and free resources
        '''
        pass
    
    def drawString(self,
               x: int,
               y: int,
               w: int = -1,
               h: int = -1,
               align: int = 0,
               text: str = "",
               size: int = 16) -> int:
        '''
        @brief draw text string
        @param x, x coordinate of text drawing box
        @param y, y coordinate of text drawing box
        @param w, width of text drawing box
        @param h, height of text drawing box
        @param align, alignment of text, ALIGN_LEFT, ALIGN_CENTER, ALIGN_RIGHT
        @param text, text to draw
        @param size, optional size to draw text
        @return next x coordinate after drawing
        '''
        pass
    
    def getStringWidth(self, 
                text : str) -> int:
        '''
        @brief get text width when drawing
        @param text, text for measurement
        @return text width
        '''
        pass
    
    def setSize(self, 
                size: int):
        '''
        @briefset font size to draw
        @param size, to modify
        '''
        pass
    
class Image(object):
    """
    PNG, JPG Wrapper Class
    """
    
    def __init__(width: int, height: int):
        '''
        @param width, height: container width and height when drawing
        '''
        pass

    def load(self, file : str, 
        mono : bool = False):
        '''
        @brief Load image from file(.png, .jpg)
        @param file, file path to load
        @param mono, load as mono image for EPD
        @return loaded image (width, height)
        '''
        pass
    
    def draw(self, 
            render:framebuf.FrameBuffer, 
            x : int = 0, 
            y : int = 0, 
            unload : bool = True):
        '''
        @brief render image at(render, x, y)
        @param render, the container to render, must be a FrameBuffer (derived) instance
        @param x, y, left-top pos to draw
        @param unload, free image resource after drawing automatically.
        '''
        pass
    
    def unload(self):
        '''
        @brief Unload image, free image resource
        '''
        pass

