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
                path_out = f"C:/Users/Lukasz/Python/ErroresBuenos/assets/photos/resizing/resized/jpg/quality{quality}/target/"
                i.save(path_out+file_name+f"-{size[0]}px"+_ext, quality=quality)

print("Finished!")

# to resize, once you have the window dimensions, divide each dimension
# of the image by the window dimensions; take the bigger ratio and
# divide both the width and height of the image by this ratio.
# This way either width or height will be maximized,
# and the other dimension will fall below the maximum,
# without changing the image’s aspect ratio
