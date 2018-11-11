from PIL import Image
# import sys
import os
from os import listdir
from os.path import isfile, join, splitext

# sys.path.append("C:\\Users\\Lukasz\\Python\\ErroresBuenos")

h_q_size = (640, 480)
m_q_size = (480, 360)
l_q_size = (280, 210)
xh_q_size = (960, 720)
hd_q_size = (1280, 960)
fhd_q_size = (1920, 1440)


# output_sizes = [h_q_size, m_q_size, l_q_size]
output_sizes = [m_q_size, xh_q_size]

_path = "C:/Users/Lukasz/Python/ErroresBuenos/assets/\
photos/image_tests/HD/"

files = [f for f in listdir(_path) if isfile(join(_path, f))]

# for f in files:
#     file_name, _ext = splitext(f)
#     if _ext == ".png":
#         path_file = f"C:/Users/Lukasz/Python/ErroresBuenos/assets/photos/image_tests/HD/{f}"
#
#         i = Image.open(path_file)
#
#         for size in output_sizes:
#             i = Image.open(path_file)
#             print(f"image size: {size}")
#             i.thumbnail(size)
#             path_out = f"C:/Users/Lukasz/Python/ErroresBuenos/assets/photos/image_tests/resized/png/"
#             i.save(path_out+file_name+f"-{size[0]}px"+_ext, optimize=True)

# single file
f = "zero.png"
file_name, _ext = splitext(f)
if _ext == ".png":
    path_file = f"C:/Users/Lukasz/Python/ErroresBuenos/assets/photos/image_tests/HD/{f}"

    i = Image.open(path_file)

    for size in output_sizes:
        i = Image.open(path_file)
        print(f"image size: {size}")
        i.thumbnail(size)
        path_out = f"C:/Users/Lukasz/Python/ErroresBuenos/assets/photos/image_tests/resized/png/"
        i.save(path_out+file_name+f"-{size[0]}px"+_ext, optimize=True)
