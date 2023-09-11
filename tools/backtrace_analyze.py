# esp32 backtrace analysis
# .nfc 2023/09/11
#

import sys
import os
from pathlib import Path
import re

path_lin = "xtensa-esp32-elf-addr2line -pfiaC -e "
path_elf = "/home/dotnfc/mpy/EPD_mpy_efont/micropython/ports/esp32/build-EFORE_S3/micropython.elf"
err_str  = "Backtrace: 0x400d4194:0x3ffe2380 0x400d41f7:0x3ffe23a0 0x400d61a3:0x3ffe23c0 0x40089c82:0x3ffe23e0"

find = re.findall(r"0x4(.+?):", err_str)

for sss in find:
    addr = " 0x4"+sss
    os.system(path_lin + path_elf+addr)


