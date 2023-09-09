# Micropython 模块 eFont

中文 | [English](README.md)

此模块为 mpy 提供 TTF, PCF 点阵字体支持，以及 jpg, png 图片显示支持。

## 1. 目录结构

- [docs/](docs/) -- 相关描述文档
- [examples/](examples/) -- 实例代码，以及 efont 模块的代码补全脚本
- [micropython/](micropython/) -- microropython 官方源码
- [mod_efont/](mod_efont/) -- 模块实现
- [script/](script/) -- 工具脚本

## 2. 模块的 API
> [docs/api.md](docs/api.md) 

## 3. 字体转换
efont 采用了 FreeType2，所以可以支持：

### 3.1 ttf 转小字库
使用 python fonttools 的 [pyftsubset 工具](https://fonttools.readthedocs.io/en/latest/subset/index.html)
```
pyftsubset fonts\SimYou3D.ttf --text-file=chardict.txt  --output-file=simyou-lite.ttf
```

### 3.2 压缩的 pcf 文件
X 系统中的 bdf 文件的压缩格式是 pcf，一般能小一半。为便于在 ESP32 环境下使用，还可以进一步压缩 pcf 文件，请使用 [EPD_bdf2pcf](https://github.com/dotnfc/EPD_bdf2pcf) 进行转换。

examples/font/ 已携带两款开源的文泉驿点阵字体。

## 4. 文件系统
目标 ESP32 S3 平台(N8R2) 的内建 Flash 8MB，有 5.5MB 可用于图片、文档、字体等资源，参见 [Partition 文件](mod_efont/boards/EFORE_S3/partitions-8MiB.csv)，以下方法可用于制作此分区的镜像，供写入目标芯片。

### 4.1 创建 examples 目录的 vfs 镜像
> 工具的原始工程 https://github.com/labplus-cn/mkfatfs

其中 -s 后面的参数最好与 partiton 中 vfs 分区的大小一致; PIO_Core 为 PlatformIO 的安装目录，通常是 %userprofile%\\.platformio\

```
> {PIO_Core}\packages\tool-mkfatfs\mkfatfs -c ./examples -t fatfs -s 4194304 efore_s3_vfs.bin 
```

### 4.2 写入镜像
```
> esptool  --before default_reset --after hard_reset --chip esp32s3 --baud 921600 --port com6 write_flash -z 0x290000 efore_s3_vfs.bin
```

### 4.3 测试 vfs 文件系统
```
>>> import os
>>> os.listdir()
```

## 参考
- https://github.com/takkaO/OpenFontRender [FT2 封装接口]
- https://github.com/kikuchan/pngle [png 支持]
- http://elm-chan.org/fsw/tjpgd/00index.html [jpg 支持]
- https://github.com/russhughes/s3lcd [图形接口]


<hr>

*.nfc 2023/09/09*
