# -*- coding: utf-8 -*-
import csv
import os

'''
https://github.com/qwd/LocationList
用 和风天气的国内城市列表，产生 WEB 和 固件使用的 城市查询数据
by .NFC 2023/07/14
'''
def containsLetter(string):
    return any(letter in string for letter in 'ABCDEF')

# 读取 CSV 文件
def read_csv_file(file_path):
    data = []
    with open(file_path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            #print(row)
            if row[0].find('China-City-List') != -1 :
                continue
            if row[0].find('Location_ID') != -1 :
                continue
            
            #if containsLetter(row[0]):  # 十六进制形式
            #    continue # nCityId = "0x" + row[0]
            if len(row[0]) != 9:
                continue
            else:                       # 十进制形式
                nCityId = hex(int(row[0]))
                
            newRow = [nCityId] + [row[0], row[1], row[2], row[7]]
                        
            data.append(newRow)
    
    sorted_list = sorted(data, key=lambda x: next(iter(x)))
    return sorted_list

def write_inc_file(file_path, data):
    '''for native'''
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        file.write("/** generated by city_parse.py */\n")
        file.write("#define CHN_CITY_COUNT %d\n" % (len(data)))
        file.write("const china_city_t china_city_map[CHN_CITY_COUNT] = {\n")
        
        for row in data:
            file.write("  { %s, /* \"%s\", */ \"%s\", \"%s\", \"%s\" },\n" % (row[0], row[1], row[2], row[3], row[4]))
        
        file.write("};\n")
        
def write_js_file(file_path, data):
    '''for web'''
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        file.write("/** generated by city_parse.py */\n")
        file.write("let cityCount = %d;\n" % (len(data)))
        file.write("let china_city_list = [\n")
        
        for row in data:
            file.write("  { /* id:%s, */ code:\"%s\", name_en:\"%s\", name_cn:\"%s\", prov:\"%s\" },\n" % (row[0], row[1], row[2], row[3], row[4]))
        
        file.write("]\n")

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
print("当前工作目录:", os.getcwd())

cityMap = read_csv_file('China-City-List-latest.csv')
write_inc_file("CityMap.inc", cityMap)  # for firmware
write_js_file("citymap.js", cityMap)    # for webserver

print("转换完成！")
