# Micropython Module eFont

[中文](README_CN.md) | English

This module provides TTF, PCF bitmap font support, as well as JPG and PNG image display support for MicroPython (mpy).

## 1. Directory Structure

- [docs/](docs/) -- Related documentation
- [examples/](examples/) -- Example code and code completion script for the eFont module
- [micropython/](micropython/) -- MicroPython official source code (git submodule)
- [mod_efont/](mod_efont/) -- Module implementation
- [tools/](tools/) -- Utility scripts

## 2. Module API
> [docs/api.md](docs/api.md)

## 3. Font Conversion
eFont uses FreeType2, so it supports:

### 3.1 TTF to Small Font
Use the [pyftsubset tool](https://fonttools.readthedocs.io/en/latest/subset/index.html) from Python fonttools.

```shell
pyftsubset fonts\SimYou3D.ttf --text-file=chardict.txt  --output-file=simyou-lite.ttf
```

### 3.2 Compressed PCF Files
The compressed format of BDF files on X systems is PCF, which is generally half the size. To further compress PCF files for use in the ESP32 environment, use [EPD_bdf2pcf](https://github.com/dotnfc/EPD_bdf2pcf) for conversion.

examples/font/ includes two open-source WenQuanYi bitmap fonts.

## 4. File System
The target ESP32 S3 platform (N8R2) has a built-in 8MB Flash, with 5.5MB available for images, documents, fonts, and other resources. Refer to [Partition File](mod_efont/boards/EFORE_S3/partitions-8MiB.csv) for this partition. The following methods can be used to create an image of this partition for writing to the target chip.

### 4.1 Create a VFS image of the examples directory
> Original project of the tool: https://github.com/labplus-cn/mkfatfs

The parameter after -s should preferably match the size of the vfs partition in the partition; PIO_Core is the installation directory of PlatformIO, usually %userprofile%\\.platformio\\.

```ps
> {PIO_Core}\packages\tool-mkfatfs\mkfatfs -c ./examples -t fatfs -s 4194304 efore_s3_vfs.bin 
```

### 4.2 Write the image

```ps
> esptool  --before default_reset --after hard_reset --chip esp32s3 --baud 921600 --port com6 write_flash -z 0x290000 efore_s3_vfs.bin
```

### 4.3 Test the VFS file system
```python
>>> import os
>>> os.listdir()
```

## 5. Build efont
Please refer to [build.md](docs/build.md)


<hr>

## <span style="color:red;">NOTE</span>
the ESP32 port of MicroPython (mpy) requires applying a [patch](tools/esp32-patch.diff)

- To debug ESP32-S3, it's necessary to prioritize JTAG.
- The current FT2 middleware implementation requires a larger stack space, so you need to adjust the size of ESP32's MP_TASK_STACK_SIZE in
micropython/ports/esp32/main.c

```c
#define MP_TASK_STACK_SIZE      (32 * 1024)
```

<hr>

## References
- https://github.com/takkaO/OpenFontRender [FT2 Wrapper Interface]
- https://github.com/kikuchan/pngle [PNG Support]
- http://elm-chan.org/fsw/tjpgd/00index.html [JPG Support]
- https://github.com/russhughes/s3lcd [Graphics Interface]



<hr>

*.nfc 2023/09/09*
