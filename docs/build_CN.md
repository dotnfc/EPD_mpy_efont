# 构建 efont 扩展

首先，我们需要搭建 micropython 的构建环境，以及 esp32-idf 的环境，请参考

- [Micropython Getting Started](https://docs.micropython.org/en/latest/develop/gettingstarted.html#compile-and-build-the-code)
- [LeMaRiva|Tech Tutorial](https://lemariva.com/blog/2020/03/tutorial-getting-started-micropython-v20)

环境搭建好以后，可以这样编译：

## 1. unix 平台的编译
```shell
~/mpy/EPD_mpy_efont$

$ git clone --recursive https://github.com/dotnfc/EPD_mpy_efont
$ cd microropython
$ make -C mpy-cross
$ cd ports/unix
$ make submodules
$ make USER_C_MODULES=../../../mod_efont/  DEBUG=1 -j4 CWARN="-Wno-error=unused-variable" FROZEN_MANIFEST=../../../mod_efont/unix_std_manifest.py
```

## 2. esp32 平台的编译

### 2.1 ESP-IDF 的安装

首先下载 ESP-IDF,有三种渠道，(目前建议使用 5.0.2)
- [ESP-IDF Installer](https://dl.espressif.cn/dl/esp-idf/)
- [espressif Github](https://github.com/espressif/esp-idf/releases/tag/v5.0.2)
- [espressif Support](https://dl.espressif.com/github_assets/espressif/esp-idf/releases/download/v5.0/esp-idf-v5.0.zip) | [Site](https://www.espressif.com/en/support/download/sdks-demos)

然后就是安装工具链，推荐乐鑫国内镜像网站：
```shell
~/esp/esp-idf$

$ export IDF_GITHUB_ASSETS="dl.espressif.com/github_assets" 
$ ./install.sh  esp32s3
$ . ./export.sh
```

### 2.2 EFORE_S3 编译
设置 esp-idf 环境
```shell
$ . ~/esp/esp-idf/export.sh
```

编译固件
```shell
~/mpy/EPD_mpy_efont/micropython/ports/esp32$ 

$ make USER_C_MODULES=../../../../mod_efont/source/micropython.cmake  DEBUG=1 -j4 CWARN="-Wno-error=unused-variable" BOARD_DIR=../../../mod_efont/boards/EFORE_S3

$ cp -f build-EFORE_S3/firmware.bin /mnt/d/mpy-efore-s3.bin
```

在 Windows 命令行，下载固件
```ps
> esptool  --before default_reset --after hard_reset --chip esp32s3 --baud 921600 --port com12 write_flash -z 0 d:\mpy-efore-s3.bin
```

### 注意 !

对于 gcc-v12 (esp-idf-v5.1) 修改 {micropython}\ports\esp32\esp32_common.cmake

```cmake
# Disable some warnings to keep the build output clean.
target_compile_options(${MICROPY_TARGET} PUBLIC
    -Wno-clobbered
    -Wno-deprecated-declarations
    -Wno-missing-field-initializers
    -Wno-error=dangling-pointer    <-----
)
```

以解决 freetype/smooth/ftgrays.c 的编译错误
```c
storing the address of local variable 'buffer' in '*worker.cell_null' [-Wdangling-pointer=]
1971 |     ras.cell_null        = buffer + FT_MAX_GRAY_POOL - 1;
```

