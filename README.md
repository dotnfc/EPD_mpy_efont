# Micropython Module eFont

- [Micropython Module eFont](#micropython-module-efont)
  - [1. Directory Structure](#1-directory-structure)
  - [2. Module API](#2-module-api)
  - [3. Font Conversion](#3-font-conversion)
    - [3.1 TTF to Small Font](#31-ttf-to-small-font)
    - [3.2 Compressed PCF Files](#32-compressed-pcf-files)
  - [4. File System](#4-file-system)
    - [4.1 Create a VFS image of the examples directory](#41-create-a-vfs-image-of-the-examples-directory)
    - [4.2 Write the image](#42-write-the-image)
    - [4.3 Test the VFS file system](#43-test-the-vfs-file-system)
  - [5. Build efont](#5-build-efont)
  - [6. How to test Script](#6-how-to-test-script)
  - [7. Embedded Modules](#7-embedded-modules)
  - [References](#references)

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
--- wsl2 shell ---
> esptool.py  --before default_reset --after hard_reset --chip esp32s3 --baud 921600 --port /dev/ttyACM0 write_flash -z 0x290000 efore_s3_vfs.bin

--- windows ps ---
> esptool  --before default_reset --after hard_reset --chip esp32s3 --baud 921600 --port com6 write_flash -z 0x290000 efore_s3_vfs.bin
```

### 4.3 Test the VFS file system
```python
>>> import os
>>> os.listdir()
```

## 5. Build efont
Please refer to [build.md](docs/build.md)

## 6. How to test Script
Please refer to [Running your first script](https://docs.micropython.org/en/latest/pyboard/tutorial/script.html). there is a main.py is the entry script on the target board, or we can run script from the repl mode.

For the PC enviroment, we can use mpremote, rshell, ... to get REPL, run a script, manage the vfs contents and so on.

For an IDE，[RT-Thread Micropython IDE for VSCode](https://marketplace.visualstudio.com/items?itemName=RT-Thread.rt-thread-micropython) may be a good choice.

And the unix port, its default heap size is too small for 3c 10.2' examples, we can do:

```shell
mpy -X heapsize=8m page/uiDay.py
```

## 7. Embedded Modules
- [MicroDot](https://github.com/miguelgrinberg/microdot) 
  
  “The impossibly small web framework for Python and MicroPython”
- [aioble](https://github.com/micropython/micropython-lib/tree/master/micropython/bluetooth/aioble)
   
  This library provides an object-oriented, asyncio-based wrapper for MicroPython's bluetooth API.

## References
- https://github.com/takkaO/OpenFontRender [FT2 Wrapper Interface]
- https://github.com/kikuchan/pngle [PNG Support]
- http://elm-chan.org/fsw/tjpgd/00index.html [JPG Support]
- https://github.com/russhughes/s3lcd [Graphics Interface]
- https://github.com/qwd/Icons [qWeather-Icons.ttf source]
- https://github.com/coinkite/mpy-qr [qrcode]
- https://github.com/jwygoda/mpy-qr [qrcode for mpy 1.20]
- Chinese Zodiac Signs Icons by StevyG

<hr>

*2023/09/09* | *2023/12/31*
