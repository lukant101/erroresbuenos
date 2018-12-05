"""Reads Google Sheets and creates a list of all audio files used in questions.

The Google Sheets are the source of truth for the questions that are later
ingested into the database.
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import time
from collections import namedtuple

Workbook = namedtuple("Workbook", "language name sheet_name col last_row")

wb_eng = Workbook("en", "flashcards_en", "deck 1", "F", 511)
wb_pol = Workbook("pl", "flashcards_pl", "deck 1", "G", 503)
wb_esp = Workbook("es", "flashcards_es", "deck 1", "G", 502)

_workbooks = [wb_eng, wb_pol, wb_esp]

_path = "assets/questions/audio_info"
os.chdir(_path)

_time = time.asctime(time.localtime(
    time.time())).replace(" ", "-").replace(":", "-")

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds_path = "C:/Users/Lukasz/Python/ErroresBuenos/GCP/"

creds = ServiceAccountCredentials.from_json_keyfile_name(
    creds_path+"qwell-spreadsheets-fc83f3df64bb.json", scope)

client = gspread.authorize(creds)

for wb in _workbooks:
    sheets = client.open(wb.name)
    sheet = sheets.worksheet(wb.sheet_name)

    audio_cells = sheet.range(f"{wb.col}2:{wb.col}{wb.last_row}")
    audio_list = [cell.value for cell in audio_cells if cell.value != ""]

    print(f"Number of records for {wb.language}: {len(audio_list)}")
    print(f"casting the list for {wb.language} as a set")
    audio_set = set(audio_list)
    print(f"Number of unique audio files for {wb.language}: {len(audio_set)}")

    # text file where names of all used image files is stored
    output_file = f"used_audio_list-{wb.language}-{_time}.txt"

    with open(output_file, "w", encoding="utf8") as f:
        for audio_file_name in audio_set:
            f.write(audio_file_name)
            f.write("\n")
