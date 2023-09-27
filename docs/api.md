# Table of Contents

* [efont](#efont)
  * [FT2](#efont.FT2)
    * [\_\_init\_\_](#efont.FT2.__init__)
    * [unload](#efont.FT2.unload)
    * [drawString](#efont.FT2.drawString)
    * [getStringWidth](#efont.FT2.getStringWidth)
    * [setSize](#efont.FT2.setSize)
    * [setColor](#efont.FT2.setColor)
    * [setRender](#efont.FT2.setRender)
  * [Image](#efont.Image)
    * [\_\_init\_\_](#efont.Image.__init__)
    * [load](#efont.Image.load)
    * [draw](#efont.Image.draw)
    * [unload](#efont.Image.unload)
    * [setColor](#efont.Image.setColor)

<a id="efont"></a>

# efont
<a id="efont.ALIGN_LEFT"></a>

#### ALIGN\_LEFT

Left alignment

<a id="efont.ALIGN_RIGHT"></a>

#### ALIGN\_RIGHT

Right alignment

<a id="efont.ALIGN_CENTER"></a>

#### ALIGN\_CENTER

Center alignment

<a id="efont.FT2"></a>

## FT2 Objects

```python
class FT2(object)
```
A FreeType2 Wrapper class

Class Attributes:
mono for EPD mode

<a id="efont.FT2.mono"></a>

#### mono

monochrome drawing for EPD

<a id="efont.FT2.bold"></a>

#### bold

bold style when drawing

<a id="efont.FT2.italic"></a>

#### italic

italic style when drawing
<a id="efont.FT2.__init__"></a>

#### \_\_init\_\_

```python
def __init__(file: str,
             render: FrameBuffer,
             size: int = 16,
             mono: bool = False,
             bold: bool = False,
             italic: bool = False) -> instance
```
<pre>
Load font from file(.ttf, .pcf).
        
Args:
    file: file path to load.
    render: an instance of framebuf.FrameBuffer which pixel() method will be called when drawString().
    size: default size to draw text
    mono: true for loading as mono font for EPD
    bold: bold style to draw text
    italic: italic style to draw text
    
Returns:
    return True if font was loaded

Raises:
    Error - raises an exception
</pre>
<a id="efont.FT2.unload"></a>

#### unload

```python
def unload()
```

Unload font and free resources.

<a id="efont.FT2.drawString"></a>

#### drawString

```python
def drawString(x: int,
               y: int,
               w: int = -1,
               h: int = -1,
               align: int = 0,
               text: str = "",
               size: int = 16) -> int
```
<pre>
Draw text string.
        
Args:
    x: x coordinate of text drawing box
    y: y coordinate of text drawing box
    w: width of text drawing box
    h: height of text drawing box
    align: alignment of text, ALIGN_LEFT, ALIGN_CENTER, ALIGN_RIGHT
    text: text to draw
    size: optional size to draw text
    
Return:
    next x coordinate after drawing
</pre>
<a id="efont.FT2.getStringWidth"></a>

#### getStringWidth

```python
def getStringWidth(text: str) -> int
```
<pre>
Get text width when drawing.
        
Args:
    text: text for measurement

Return:
    text width
</pre>
<a id="efont.FT2.setSize"></a>

#### setSize

```python
def setSize(size: int)
```

<pre>
Set font size to draw.
        
Args:
    Size, to modify
</pre>

<a id="efont.FT2.setColor"></a>

#### setColor

```python
def setColor(fg: int, bg: int)
```

<pre>
Set the foreground and background color when monochrome mode
        
Args:
    fg: foreground color
    bg: background color
</pre>

<a id="efont.FT2.setRender"></a>

#### setRender

```python
def setRender(render: FrameBuffer)
```

<pre>
Set font new render
        
Args:
    render, new render to use
</pre>

<a id="efont.Image"></a>

## Image Objects

```python
class Image(object)
```
PNG, JPG Wrapper Class
<a id="efont.Image.__init__"></a>

#### \_\_init\_\_

```python
def __init__(width: int,
             height: int) -> instance
```
<pre>
Args:
    width, height: container width and height when drawing
</pre>
<a id="efont.Image.load"></a>

#### load

```python
def load(self,
         file: str, 
         mono: bool = False)
```
<pre>
Load image from file(.png, .jpg).
        
Args:
    file: file path to load
    mono: load as mono image for EPD

Return:
    loaded image (width, height)
</pre>
<a id="efont.Image.draw"></a>

#### draw

```python
def draw(self, 
         render:framebuf.FrameBuffer, 
         x: int = 0, 
         y: int = 0, 
         unload: bool = True)
```
<pre>
Render image at(render, x, y).
        
Args:
    render: the container to rend, must be a FrameBuffer (derived) instance
    x, y: left-top position to draw
    unload: free image resources after drawing automatically.
</pre>

<a id="efont.Image.unload"></a>

#### unload

```python
def unload()
```
<pre>
Unload image, free image resource
</pre>

<a id="efont.Image.setColor"></a>

#### setColor

```python
def setColor()
```

<pre>
Set the foreground and background color when monochrome mode.
Args:
    fg: foreground color
    bg: background color
</pre>

<hr>

*'pydoc-markdown -I . -m efont --render-toc > efont.md' 2023/09/09*
