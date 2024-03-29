# Build the efont

First, we need to setup the build environment for the MicroPython and the ESP32-IDF environment. Please refer to:

- [Micropython Getting Started](https://docs.micropython.org/en/latest/develop/gettingstarted.html#compile-and-build-the-code)
- [LeMaRiva|Tech Tutorial](https://lemariva.com/blog/2020/03/tutorial-getting-started-micropython-v20) 👍

Once the environment has setup, you can compile as the followings:

## 1. Unix Port
```shell
~/mpy/EPD_mpy_efont$

$ git clone https://github.com/dotnfc/EPD_mpy_efont
$ git submodule init
$ git submodule update
$ cd microropython
$ make -C mpy-cross
$ cd ports/unix
$ make submodules
$ make USER_C_MODULES=../../../mod_efont/cmodules  DEBUG=1 -j4 CWARN="-Wno-error=unused-variable" FROZEN_MANIFEST=../../../mod_efont/unix_std_manifest.py
```

## 2. esp32 Port
### 2.1 Build the EFORE_S3 
Setup ESP-IDF Once

```shell
$ . ~/esp/esp-idf/export.sh
```

build N8R2 firmware with
```shell
~/mpy/EPD_mpy_efont/micropython/ports/esp32$ 

$ make USER_C_MODULES=../../../../mod_efont/cmodules/micropython.cmake  DEBUG=1 -j4 CWARN="-Wno-error=unused-variable" BOARD_DIR=../../../mod_efont/boards/EFORE_S3

$ cp -f build-EFORE_S3/firmware.bin /mnt/d/mpy-efont-esp32s3_fw.bin
```

build N16R8 firmware with
```shell
~/mpy/EPD_mpy_efont/micropython/ports/esp32$ 

$ make USER_C_MODULES=../../../../mod_efont/cmodules/micropython.cmake -j4 CWARN="-Wno-error=unused-variable" BOARD_DIR=../../../mod_efont/boards/EFORE_S3_N16R8

$ cp -f build-EFORE_S3_N16R8/firmware.bin /mnt/d/mpy-efont-esp32s3_fw_ota.bin
```

On the Windows console, burn the output firmware file:
```ps
> esptool  --before default_reset --after hard_reset --chip esp32s3 --baud 921600 --port com12 write_flash -z 0 d:\mpy-efont-esp32s3_fw.bin
```

### NOTE !

For gcc-v12 (esp-idf-v5.1 or later) modify the {micropython}\ports\esp32\esp32_common.cmake

```cmake
# Disable some warnings to keep the build output clean.
target_compile_options(${MICROPY_TARGET} PUBLIC
    -Wno-clobbered
    -Wno-deprecated-declarations
    -Wno-missing-field-initializers
    -Wno-error=dangling-pointer    <-----
)
```

to fix the 'freetype/smooth/ftgrays.c' compiling error:
```c
storing the address of local variable 'buffer' in '*worker.cell_null' [-Wdangling-pointer=]
1971 |     ras.cell_null        = buffer + FT_MAX_GRAY_POOL - 1;
```

<hr>

*2023/09/09*
