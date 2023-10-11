import shutil
import zipfile
import datetime
import os

spec_datetime = "2023/10/11 18:30"
spec_datetime = datetime.datetime.strptime(spec_datetime, "%Y/%m/%d %H:%M")

# zip file to modify
zip_filename = r'E:\temp\mpy\PyStand-py38-pyside2-lite\build\eFontTool-gui.zip'

# decompress to a temperary folder
extract_dir = 'temp_extracted'
with zipfile.ZipFile(zip_filename, 'r') as zip_archive:
    zip_archive.extractall(extract_dir)

# change new date and time
for root, dirs, files in os.walk(extract_dir):
    for file in files:
        file_path = os.path.join(root, file)
        os.utime(file_path, (spec_datetime.timestamp(), spec_datetime.timestamp()))

    for d in dirs:
        dir_path = os.path.join(root, d)
        os.utime(dir_path, (spec_datetime.timestamp(), spec_datetime.timestamp()))

# rebuild the zip file
shutil.make_archive('eFontTool-gui+', 'zip', extract_dir)

# remove temp files
shutil.rmtree(extract_dir)