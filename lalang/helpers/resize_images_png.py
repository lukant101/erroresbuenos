from PIL import Image
import os
from os import listdir
from os.path import isfile, join, splitext


h_q_size = (640, 480)
m_q_size = (480, 360)
l_q_size = (280, 210)
xh_q_size = (960, 720)
hd_q_size = (1280, 960)
fhd_q_size = (1920, 1440)

output_sizes = [m_q_size, xh_q_size]

_path = "C:/Users/Lukasz/Python/ErroresBuenos/assets/\
photos/resizing/HD_from_640px_raster/"

files = [f for f in listdir(_path) if isfile(join(_path, f))]

for f in files:
    file_name, _ext = splitext(f)
    if _ext == ".png":
        path_file = _path + f

        for size in output_sizes:
            i = Image.open(path_file)
            i.thumbnail(size)
            path_out = f"C:/Users/Lukasz/Python/ErroresBuenos/assets/photos/resizing/resized/png/target/"
            i.save(path_out+file_name+f"-{size[0]}px"+_ext, optimize=True)
            print(f"File saved: {file_name+_ext}")

# single file
# f = "zero.png"
# file_name, _ext = splitext(f)
# if _ext == ".png":
#     path_file = f"C:/Users/Lukasz/Python/ErroresBuenos/assets/photos/image_tests/HD/{f}"
#
#     i = Image.open(path_file)
#
#     for size in output_sizes:
#         i = Image.open(path_file)
#         print(f"image size: {size}")
#         i.thumbnail(size)
#         path_out = f"C:/Users/Lukasz/Python/ErroresBuenos/assets/photos/image_tests/resized/png/"
#         i.save(path_out+file_name+f"-{size[0]}px"+_ext, optimize=True)
