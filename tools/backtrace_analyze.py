# esp32 backtrace analysis
# .nfc 2023/09/11
#

import sys
import os
from pathlib import Path
import re

path_lin = "xtensa-esp32-elf-addr2line -pfiaC -e "
path_elf = "/home/dotnfc/mpy/EPD_mpy_efont/micropython/ports/esp32/build-EFORE_S3/micropython.elf"
err_str  = "Backtrace: 0x42169bba:0x3fcb9770 0x420d3406:0x3fcb97a0 0x420a4438:0x3fcb97e0 0x420a4840:0x3fcb9860 0x4206f179:0x3fcb98b0 0x420705f9:0x3fcb98d0 0x40379266:0x3fcb98f0 0x42069888:0x3fcb9990 0x420705f9:0x3fcb99e0 0x4207060e:0x3fcb9a00 0x420a3303:0x3fcb9a20 0x420a3648:0x3fcb9ab0 0x420836fc:0x3fcb9af0"

find = re.findall(r"0x4(.+?):", err_str)

for sss in find:
    addr = " 0x4"+sss
    os.system(path_lin + path_elf+addr)


