"""Find aspect ratio of svg images, then output to a text file.

For the images that have viewBox specified, use the width
and height of the viewbox.

For images that don't have viewBox, use the width and height attributes.

Otherwise, output message that there is no information
about the image dimensions.
"""


import re
import os
import time
from os import listdir
from os.path import isfile

_time = time.asctime(time.localtime(
    time.time())).replace(" ", "-").replace(":", "")

pattern = re.compile("viewBox=\".+?\"")

pattern_width = re.compile("width=\"\d+\.?\d*\w*\"")
pattern_height = re.compile("height=\"\d+\.?\d*\w*\"")

os.chdir("C:/Users/Lukasz/Python/ErroresBuenos/assets/photos/svg_aspect_ratio/images/")

file_out = f"../svg_images_aspect_ratio-{_time}.txt"

files = [f for f in listdir(".") if isfile(f)]

with open(file_out, "w", encoding="utf8") as fw:
    for file in files:
        with open(file, "r", encoding="utf8") as fr:
            svg_contents = fr.read()
            match = pattern.search(svg_contents)
            if not match:
                match_width = pattern_width.search(svg_contents)
                if match_width:
                    width = match_width[0].lstrip("width").lstrip().\
                        lstrip("=").lstrip().strip('"')
                    width = float(width)

                match_height = pattern_height.search(svg_contents)
                if match_height:
                    height = match_height[0].lstrip("height").lstrip().\
                        lstrip("=").lstrip().strip('"')
                    height = float(height)

            if match:
                match = match[0]
                match = match.lstrip("viewBox").lstrip().\
                    lstrip("=").lstrip().strip('"')
                _, _, width, height = match.split(" ")
                width = float(width)
                height = float(height)

            if width and height:
                aspect_ratio = round(width/height, 3)
                fw.write(f"{file}, {aspect_ratio}")
                fw.write("\n")
            else:
                print(f"File: {file} has no dimensions information.")
