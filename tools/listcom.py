 #!/usr/bin/env python
#-*- coding:utf-8 -*-
#
# by dotnfc, 2023/06/02

import sys
import time
import serial
from serial.tools.list_ports import comports

def list_coms():
    ports_list = list(serial.tools.list_ports.comports())
    if len(ports_list) <= 0:
        print("无串口设备。")
    else:
        print("可用的串口设备如下：")
        for comport in ports_list:
            print("%-8s - %s" % (list(comport)[0], list(comport)[1]))
            
if __name__ == "__main__":
    list_coms()
