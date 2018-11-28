"""For images listed in a text file, move these files to a separate folder."""

import os
import time

input_file = "C:/Users/Lukasz/Python/ErroresBuenos/assets/questions/\
used_photos_list_Nov22_2018.txt"

_time = time.asctime(time.localtime(time.time())).replace(" ", "-")


.replace(".", "-")

output_file = f"C:/Users/Lukasz/Python/ErroresBuenos/assets/questions/\
missing_photos_list-{_time}.txt"

images_folder = "C:/Users/Lukasz/Python/ErroresBuenos/\
assets/photos/for_deployment/"

file_versions = ["-480px.webp",
                 "-960px.webp"
                 ]

with open(input_file, "r", encoding="utf8") as fr, \
        open(output_file, "w", encoding="utf8") as fw:
    for file in fr:
        file = file.strip()

        try:
            file_name, _ext = file.split(".")
        except ValueError:
            fw.write(f"Corrupted file name: {file}")
            fw.write("\n")
            continue

        if _ext == "svg":
            try:
                os.rename(images_folder+"svg/"+file,
                          images_folder+"svg/target/"+file)
            except FileNotFoundError:
                print(f"File: {file} does not exist")
                fw.write(file)
                fw.write("\n")
        else:
            file_versions_temp = file_versions.copy()
            file_versions_temp.append(f"-480px.{_ext}")
            file_versions_temp.append(f"-960px.{_ext}")
            for f_ver in file_versions_temp:
                file = file_name + f_ver
                try:
                    os.rename(images_folder+"raster/"+file,
                              images_folder+"raster/target/"+file)
                except FileNotFoundError:
                    print(f"File: {file} does not exist")
                    fw.write(file)
                    fw.write("\n")
