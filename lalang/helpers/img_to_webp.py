from PIL import Image
from os import listdir
from os.path import isfile, join, splitext

SUPPORTED_RASTER_FORMATS = ['jpg', 'jpeg', 'png']

m_q_size = (480, 360)
xh_q_size = (960, 720)

output_sizes = [m_q_size]
quality = 70

_path = "C:/Users/Lukasz/Python/ErroresBuenos/assets/\
photos/resizing/new_HD_raster/"

files = [f for f in listdir(_path) if isfile(join(_path, f))]

for f in files:
    file_name, _ext = splitext(f)
    _ext = _ext.lstrip(".")
    if _ext in SUPPORTED_RASTER_FORMATS:
        path_file = _path+f

        for size in output_sizes:
            i = Image.open(path_file)
            i.thumbnail(size)
            path_out = f"C:/Users/Lukasz/Python/ErroresBuenos/assets/photos/resizing/resized/webp/new_HD/quality{quality}/"
            i.save(path_out+file_name+f"-{size[0]}px" + ".webp",
                   format="webp", quality=quality, method=6)

print("Finished!")
