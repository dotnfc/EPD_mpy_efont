# Table of Contents

* [efont](#efont)
  * [FT2](#efont.FT2)
    * [\_\_init\_\_](#efont.FT2.__init__)
    * [unload](#efont.FT2.unload)
    * [drawString](#efont.FT2.drawString)
    * [getStringWidth](#efont.FT2.getStringWidth)
    * [setSize](#efont.FT2.setSize)
  * [Image](#efont.Image)
    * [\_\_init\_\_](#efont.Image.__init__)
    * [load](#efont.Image.load)
    * [draw](#efont.Image.draw)
    * [unload](#efont.Image.unload)

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
@brief Load font from file(.ttf, .pcf)
@param file, file path to load
@param render, an instance of framebuf.FrameBuffer which pixel() method will be called when self.drawString()
@param size, default size to draw text
@param mono, true for loading as mono font for EPD
@param bold, bold style to draw text
@param italic, italic style to draw text
@return True if font was loaded
</pre>
<a id="efont.FT2.unload"></a>

#### unload

```python
def unload()
```

@Unload font and free resources

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
@brief draw text string
@param x, x coordinate of text drawing box
@param y, y coordinate of text drawing box
@param w, width of text drawing box
@param h, height of text drawing box
@param align, alignment of text, ALIGN_LEFT, ALIGN_CENTER, ALIGN_RIGHT
@param text, text to draw
@param size, optional size to draw text
@return next x coordinate after drawing
</pre>
<a id="efont.FT2.getStringWidth"></a>

#### getStringWidth

```python
def getStringWidth(text: str) -> int
```

@brief get text width when drawing
@param text, text for measurement
@return text width

<a id="efont.FT2.setSize"></a>

#### setSize

```python
def setSize(size: int)
```

@briefset font size to draw
@param size, to modify

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
@param width, height: container width and height when drawing
</pre>
<a id="efont.Image.load"></a>

#### load

```python
def load(self,
         file: str, 
         mono: bool = False)
```
<pre>
@brief Load image from file(.png, .jpg)
@param file, file path to load
@param mono, load as mono image for EPD
@return loaded image (width, height)
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
@brief render image at(render, x, y)
@param render, the container to render, must be a FrameBuffer (derived) instance
@param x, y, left-top pos to draw
@param unload, free image resource after drawing automatically.
</pre>

<a id="efont.Image.unload"></a>

#### unload

```python
def unload()
```

@brief Unload image, free image resource

<hr>

*'pydoc-markdown -I . -m efont --render-toc > efont.md' 2023/09/09*
