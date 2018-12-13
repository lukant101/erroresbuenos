""" Check whether this script can be deleted.

We have another script that handles several raster formats.
"""
from PIL import Image
# import sys
from os import listdir
from os.path import isfile, join, splitext

l_q_size = (280, 210)
m_q_size = (480, 360)
h_q_size = (640, 480)
xh_q_size = (960, 720)
hd_q_size = (1280, 960)
fhd_q_size = (1920, 1440)


output_sizes = [m_q_size, xh_q_size]
quality_set = [70]

_path = "C:/Users/Lukasz/Python/ErroresBuenos/assets/\
photos/resizing/HD/source/"

files = [f for f in listdir(_path) if isfile(join(_path, f))]

for f in files:
    file_name, _ext = splitext(f)
    if _ext in {".jpeg", ".jpg"}:
        path_file = _path + f

        for size in output_sizes:
            i = Image.open(path_file)
            i.thumbnail(size)
            for quality in quality_set:
                path_out = f"C:/Users/Lukasz/Python/ErroresBuenos/assets/photos/resizing/resized/webp/from_jpg/quality{quality}/target/"
                i.save(path_out+file_name+f"-{size[0]}px" + ".webp",
                       format="webp", quality=quality, method=6)
