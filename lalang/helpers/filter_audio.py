"""For audio files listed in a text file, move them to a separate folder."""

import os
import time
import sys

sys.path.append("C:/Users/Lukasz/Python/ErroresBuenos")

from lalang.constants import SUPPORTED_LANGUAGES_ABBREV, AUDIO_FORMATS

_time = time.asctime(time.localtime(
    time.time())).replace(" ", "-").replace(":", "-")

for lang in SUPPORTED_LANGUAGES_ABBREV.values():
    input_file = ("C:/Users/Lukasz/Python/ErroresBuenos/assets/questions/"
                  "audio_info/used_audio_list-"
                  f"{lang}-Thu-Nov-29-19-37-07-2018.txt")

    audio_source_folder = ("C:/Users/Lukasz/Python/ErroresBuenos/"
                           "assets/audio_recordings/"
                           f"for_deployment_test/{lang}/")

    with open(input_file, "r", encoding="utf8") as fr:
        for row in fr:
            file_name_no_ext = row.strip()

            for format in AUDIO_FORMATS:
                file_name = file_name_no_ext + "." + format

                output_file = ("C:/Users/Lukasz/Python/ErroresBuenos/assets/"
                               "questions/audio_info/missing_audio_list-"
                               f"{lang}-{format}-{_time}.txt")

                with open(output_file, "a", encoding="utf8") as fw:
                    try:
                        os.rename(audio_source_folder+file_name,
                                  audio_source_folder+"target/" + file_name)
                    except FileNotFoundError:
                        fw.write(format+", "+file_name_no_ext)
                        fw.write("\n")
