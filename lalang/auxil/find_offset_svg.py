"""Find svg images with unnecessary white space, and output them to file.

If x,y values in viewBox are not at 0,0 there is white space
around the vector graphic (assuming there are not sprite images).

The script identifies images with viewBox not starting at 0,0 and saves
their file names to a text file.

Files without viewBox set are ignored.

The output text file is used with Adobe Illustrator, etc. to change
the viewBox parameters. By setting the viewBox to 0,0 and adjusting
the viewBox width and height accordinly, the white space around the graphic
is eliminated.
"""

import re
import os
import time
from os import listdir
from os.path import isfile

_time = time.asctime(time.localtime(
    time.time())).replace(" ", "-").replace(":", "")

pattern = re.compile("viewBox=\".+?\"")


os.chdir("C:/Users/Lukasz/Python/ErroresBuenos/\
assets/photos/svg_aspect_ratio/images/")

file_out = f"../svg_offset_from_origin-{_time}.txt"

files = [f for f in listdir(".") if isfile(f)]

with open(file_out, "w", encoding="utf8") as fw:
    for file in files:
        with open(file, "r", encoding="utf8") as fr:
            svg_contents = fr.read()
            match = pattern.search(svg_contents)

            if match:
                match = match[0]
                match = match.lstrip("viewBox").lstrip().\
                    lstrip("=").lstrip().strip('"')
                x, y, _, _ = match.split(" ")
                x = float(x)
                y = float(y)

            if x != 0 or y != 0:
                fw.write(f"{file}, viewBox_origin: {x} {y}")
                fw.write("\n")
