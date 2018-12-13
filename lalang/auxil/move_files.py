"""Move files to a new folder based on a substring match in the file name."""

import os
from os import listdir
from os.path import isfile

# folder where the files are currently located
_path = "assets/photos/resizing/resized/jpg/quality70"

# folder where the matched files should be moved
target_dir_name = "target"

# substrings to find in file names based on which files are moved
text_matches = ["480px", "960px"]

os.chdir(_path)

cwd = os.getcwd()
print("Changed current working directory to: ", cwd)

dir_contents = listdir(".")

if target_dir_name not in dir_contents:
    os.mkdir(target_dir_name)
    print(f"Created folder: {target_dir_name}")

files = [f for f in dir_contents if isfile(f)]

print(f"Number of files in origin directory: {len(files)}")

num_files_moved = 0

for f in files:
    for text in text_matches:
        if f.find(text) != -1:
            os.rename(f, target_dir_name+"/"+f)
            num_files_moved += 1

print(f"Number of files moved: {num_files_moved}")

print("Finished!")
