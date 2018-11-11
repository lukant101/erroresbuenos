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
output_sizes = [m_q_size]
# quality_set = [10, 20, 30, 40, 50, 60, 70]
quality_set = [70]

_path = "C:/Users/Lukasz/Python/ErroresBuenos/assets/\
photos/image_tests/HD/"

# path_file = f"C:/Users/Lukasz/Python/ErroresBuenos/assets/\
# photos/image_tests/HD/{file_name_orig}.{file_extension}"

# files = [f for f in listdir(_path) if isfile(join(_path, f))]
files = "woman-with-blue-hair.jpg"

for f in files:
    file_name, _ext = splitext(f)
    if _ext == ".jpg":
        path_file = f"C:/Users/Lukasz/Python/ErroresBuenos/assets/photos/image_tests/HD/{f}"

        i = Image.open(path_file)

        for size in output_sizes:
            i.copy().thumbnail(size)
            for quality in quality_set:
                path_out = f"C:/Users/Lukasz/Python/ErroresBuenos/assets/photos/image_tests/resized/quality{quality}/"
                print(path_out)
                i.save(path_out+file_name+f"-{size[0]}px"+_ext, quality=quality)


# file_name_orig = "water-bottle"
# file_extension = "jpg"
# path_file_name, _ext = path_file.split(".")
# file_name = path_file_name.rsplit("/", 1)[1]
# i.save(path_out+file_name+f"-{size[0]}px"+"."+_ext, quality=quality)

# to resize, once you have the window dimensions, divide each dimension
# of the image by the window dimensions; take the bigger ratio and
# divide both the width and height of the image by this ratio.
# This way either width or height will be maximized,
# and the other dimension will fall below the maximum,
# without changing the image’s aspect ratio
