input_file_path = "all.bin"  # 你的输入二进制文件路径
output_file_path = "lunar_data.py"  # 输出文件路径

# 读取二进制文件内容
with open(input_file_path, "rb") as input_file:
    binary_data = input_file.read()

# 转换为bytearray
byte_array = bytearray(binary_data)

# 生成输出文件内容
output_content = f"byte_array = {byte_array}\n"

# 将输出内容写入输出文件
with open(output_file_path, "w") as output_file:
    output_file.write(output_content)

print("转换完成并已写入输出文件。")

