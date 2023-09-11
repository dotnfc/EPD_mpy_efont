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

首先下载 ESP-IDF,有三种渠道，(目前 2023/09/09 请使用 5.0.2)
- [ESP-IDF Installer](https://dl.espressif.cn/dl/esp-idf/)  best for windows
- [espressif Github](https://github.com/espressif/esp-idf/releases/tag/v5.0.2)
- [espressif Support](https://dl.espressif.com/github_assets/espressif/esp-idf/releases/download/v5.0.2/esp-idf-v5.0.2.zip) | [Site](https://www.espressif.com/en/support/download/sdks-demos)

然后就是安装工具链，推荐乐鑫国内镜像网站：
```shell
~/esp/esp-idf$

$ export IDF_GITHUB_ASSETS="dl.espressif.com/github_assets" 
$ ./install.sh  esp32s3
$ . ./export.sh
```

如果 安装 python 虚拟环境的时候，很慢，那就开启 pip 全局国内镜像
```shell
$ mkdir ~/pip
$ vi ~/pip/pip.conf
```

新增其内容为:
```ini
[global]
index-url=https://pypi.tuna.tsinghua.edu.cn/simple
timeout = 6000
 
[install]
trusted-host=pypi.tuna.tsinghua.edu.cn
disable-pip-version-check = true
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

对于 gcc-v12 (esp-idf-v5.1 目前不建议用 2023/09/09) 修改 {micropython}\ports\esp32\esp32_common.cmake

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

## 3. 开发中的提示

1. 建议用 ccproxy 的 socks5 二级代理模式
    ```shell
    host_ip=$(cat /etc/resolv.conf |grep "nameserver" |cut -f 2 -d " ")
    export http_proxy="socks5://$host_ip:3128"
    export https_proxy="socks5://$host_ip:3128"
    unset http_proxy
    unset https_proxy
    ```
2. 关闭文件监控
    ```ps
    Set-MpPreference -DisableRealtimeMonitoring $true
    ```

3. 查看 micropython 已加载的模块
    ```python
    help('modules')
    ```

4. 掐 mpy 执行时间和 ram
    ```python
    >>> import time
    >>> import gc
    >>>
    >>> mem_free = gc.mem_free()
    >>> _start = timer.ticks_ms()
    >>> import font24
    >>> _stop = timer.ticks_ms() # module has loaded
    >>> print(mem_free - gc.mem_free())
    36656
    >>> print(_stop - _start)   # in ms
    1666.031
    ```
5. 模块的安装
[micropython-lib](https://github.com/micropython/micropython-lib)
    ```python
    $ ./build-standard/micropython -m mip install hmac
    or
    $ ./build-standard/micropython
    >>> import mip
    >>> mip.install("hmac")
    ```

    > 在 esp32 上，可以开 wifi 联网后，下载到文件系统中：

    ```python
    import network

    ssid_ = [ROUTER_SSID]
    wp2_pass = [ROUTER_WPA2_PASSWORD]

    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(ssid_, wp2_pass)

    while not sta_if.isconnected():
        pass

    print('network config:', sta_if.ifconfig())

    # upip replaced by mip since 1.19
    import mip
    mip.install('hmac')
    ```

    > 查询 micropython 平台的 模块 https://pypi.org/search/?q=micropython-* 

6. 使用 psram
    ```python
    >>> import micropython
    >>> micropython.mem_info()
    stack: 704 out of 15360
    GC: total: 128000, used: 68160, free: 59840, max new split: 1933312
    No. of 1-blocks: 29, 2-blocks: 14, max blk sz: 2048, max free sz: 1952
    >>> arr32k = bytearray(32 * 1024)
    ```

<hr>

*.nfc 2023/09/09*