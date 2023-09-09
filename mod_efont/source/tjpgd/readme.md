# TJpgDec - Tiny JPEG Decompressor

> http://elm-chan.org/fsw/tjpgd/00index.html

TJpgDec is a generic JPEG image decompressor module that highly optimized for small embedded systems. It works with very low memory consumption, so that it can be incorporated into tiny microcontrollers, such as AVR, 8051, PIC, Z80, Cortex-M0 and etc.

## Features
- Platform Independent. Written in Plain C (C99).
- Easy to Use Master Mode Operation.
- Fully Re-entrant Architecture.
- Configurable Optimization Level for both 8/16-bit and 32-bit MCUs.
- Very Small Memory Footprint:
  - 3.5K Bytes of RAM for Work Area Independent of Image Dimensions.
  - 3.5-8.5K Bytes of ROM for Text and Constants.
- Output Format:
  - Pixel Format: RGB888, RGB565 or Grayscale Pre-configurable.
  - Scaling Ratio: 1/1, 1/2, 1/4 or 1/8 Selectable on Decompression.

## Application Interface
There are two API functions to analyze and decompress the JPEG image.

- [jd_prepare](http://elm-chan.org/fsw/tjpgd/en/prepare.html) - Prepare decompression of the JPEG image
- [jd_decomp](http://elm-chan.org/fsw/tjpgd/en/decomp.html) - Execute decompression of the JPEG image

## I/O functions
To input the JPEG data and output the decompressed image, TJpgDec requires two user defined I/O functions. These are called back from the TJpgDec module in the decompression process.

- [Input Function](http://elm-chan.org/fsw/tjpgd/en/input.html) - Read JPEG data from the input stream
- [Output Function](http://elm-chan.org/fsw/tjpgd/en/output.html) - Output the decompressed image to the destination object
