from PIL import Image
# import sys
from os import listdir
from os.path import isfile, join, splitext

# sys.path.append("C:\\Users\\Lukasz\\Python\\ErroresBuenos")

l_q_size = (280, 210)
m_q_size = (480, 360)
h_q_size = (640, 480)
xh_q_size = (960, 720)
hd_q_size = (1280, 960)
fhd_q_size = (1920, 1440)


# output_sizes = [h_q_size, m_q_size, l_q_size]
output_sizes = [l_q_size, m_q_size, h_q_size, xh_q_size]
quality_set = [70]

_path = "C:/Users/Lukasz/Python/ErroresBuenos/assets/\
photos/image_tests/HD/"

# path_file = f"C:/Users/Lukasz/Python/ErroresBuenos/assets/\
# photos/image_tests/HD/{file_name_orig}.{file_extension}"

files = [f for f in listdir(_path) if isfile(join(_path, f))]

for f in files:
    file_name, _ext = splitext(f)
    if _ext == ".jpg":
        path_file = f"C:/Users/Lukasz/Python/ErroresBuenos/assets/photos/image_tests/HD/{f}"

        for size in output_sizes:
            i = Image.open(path_file)
            i.thumbnail(size)
            for quality in quality_set:
                path_out = f"C:/Users/Lukasz/Python/ErroresBuenos/assets/photos/image_tests/resized/webp/quality{quality}/"
                i.save(path_out+file_name+f"-{size[0]}px" + ".webp",
                       format="webp", quality=quality, method=6)
