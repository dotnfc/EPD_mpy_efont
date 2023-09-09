#
# 批量 繁体转简体 文件转换
# for https://github.com/hungtcs/traditional-chinese-calendar-database
# .nfc 2023/06/05
#

import opencc
import os

def processFile(root, file):
    file_path = os.path.join(root, file)
    
    # 创建一个转换器对象，指定繁体中文转换为简体中文
    converter = opencc.OpenCC('t2s.json')

    # 读取繁体中文文件
    with open(file_path, 'r', encoding='utf-8') as f:
        traditional_text = f.read()

    # 将繁体中文文本转换为简体中文
    simplified_text = converter.convert(traditional_text)

    # 保存转换后的简体中文文本
    with open('./min/'+file, 'w', encoding='utf-8') as f:
        f.write(simplified_text)


def enumerate_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            processFile(root, file)
            print(file)
            # print(file_path)  # 在这里可以对文件路径进行处理，比如保存到列表中或进行其他操作

        #for folder in dirs:
        #    folder_path = os.path.join(root, folder)
        #    print(folder_path)  # 在这里可以对文件夹路径进行处理，比如保存到列表中或进行其他操作

# 指定目录路径
directory_path = '..\\database\\json\\min\\'
enumerate_files (directory_path)
