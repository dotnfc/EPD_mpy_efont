"""This module provides a general frame buffer which can be used to create bitmap images, 
which can then be sent to a display.
"""

class FrameBuffer:
    """
    The FrameBuffer class provides a pixel buffer which can be drawn upon with pixels, lines, rectangles, ellipses, 
    polygons, text and even other FrameBuffers. It is useful when generating output for displays.
    
    For example::
    
        import framebuf

        # FrameBuffer needs 2 bytes for every RGB565 pixel
        fbuf = framebuf.FrameBuffer(bytearray(100 * 10 * 2), 100, 10, framebuf.RGB565)

        fbuf.fill(0)        
        fbuf.text('MicroPython!', 0, 0, 0xffff)        
        fbuf.hline(0, 9, 96, 0xffff)
    
    """

    def blit(fbuf, x, y, key=-1, palette=None):
        '''
        Blit a frame buffer to the screen.
        '''
        pass
    
    def poly(x, y, coords, c, f):
        '''
        Given a list of coordinates, draw an arbitrary (convex or concave) closed polygon at the given x, y location 
        using the given color.

        The coords must be specified as a array of integers, e.g. array('h', [x0, y0, x1, y1, ... xn, yn]).

        The optional f parameter can be set to True to fill the polygon. Otherwise just a one pixel outline is drawn.
        '''
        pass
    
    def fill(c):
        '''
        Fill the entire frame buffer with the given color.
        '''
        pass

    def vline(x, y, h, c):
        pass
    
    def hline(x, y, w, c):
        pass

    def line(x1, y1, x2, y2, c):
        '''
        Draw a line from a set of coordinates using the given color and a thickness of 1 pixel. 
        
        The line method draws the line up to a second set of coordinates whereas the hline and vline methods 
        draw horizontal and vertical lines respectively up to a given length.
        '''
        pass

    def pixel(x, y, c):
        '''
        If c is not given, get the color value of the specified pixel. 
        If c is given, set the specified pixel to the given color.
        '''
        pass

    def rect(x, y, w, h, c, f=False):
        '''
        Draw a rectangle at the given location, size and color.

        The optional f parameter can be set to True to fill the rectangle.
        Otherwise just a one pixel outline is drawn.
        '''
        pass

    def ellipse(x, y, xr, yr, c, f, m):
        '''
        Draw an ellipse at the given location. Radii xr and yr define the geometry; 
        equal values cause a circle to be drawn. 
        
        The c parameter defines the color.

        The optional f parameter can be set to True to fill the ellipse. 
        Otherwise just a one pixel outline is drawn.

        The optional m parameter enables drawing to be restricted to certain quadrants of the ellipse. 
        
        The LS four bits determine which quadrants are to be drawn, with bit 0 specifying Q1, b1 Q2, b2 Q3 and b3 Q4.
         
        Quadrants are numbered counterclockwise with Q1 being top right.
        '''
        pass
    
    def scroll(xstep, ystep):
        '''
        Scroll the frame buffer by the given steps.
        '''
        pass

    def text(s, x, y, c=1):
        '''
        Write text to the FrameBuffer using the the coordinates as the upper-left corner of the text. 
        
        The color of the text can be defined by the optional argument but is otherwise a default value of 1. 
        
        All characters have dimensions of 8x8 pixels and there is currently no way to change the font.
        '''
        pass


def FrameBuffer1():
    pass


GS2_HMSB = 5
'''
Grayscale (2-bit) color format
'''

GS4_HMSB = 2
'''
Grayscale (4-bit) color format
'''

GS8 = 6
'''
Grayscale (8-bit) color format
'''

MONO_HLSB = 3
'''
Monochrome (1-bit) color format This defines a mapping where the bits in a byte are horizontally mapped. 

Each byte occupies 8 horizontal pixels with bit 7 being the leftmost. 

Subsequent bytes appear at successive horizontal locations until the rightmost edge is reached. 

Further bytes are rendered on the next row, one pixel lower.
'''

MONO_HMSB = 4
'''
Monochrome (1-bit) color format This defines a mapping where the bits in a byte are horizontally mapped. 
Each byte occupies 8 horizontal pixels with bit 0 being the leftmost. 

Subsequent bytes appear at successive horizontal locations until the rightmost edge is reached. 

Further bytes are rendered on the next row, one pixel lower.
'''

MONO_VLSB = 0
'''
Monochrome (1-bit) color format This defines a mapping where the bits in a byte are vertically mapped with 
bit 0 being nearest the top of the screen. 

Consequently each byte occupies 8 vertical pixels. 

Subsequent bytes appear at successive horizontal locations until the rightmost edge is reached. 

Further bytes are rendered at locations starting at the leftmost edge, 8 pixels lower.
'''

RGB565 = 1
'''
Red Green Blue (16-bit, 5+6+5) color format
'''
