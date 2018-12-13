"""Reads Google Sheets and creates a list of all images used in questions.

The Google Sheets are the source of truth for the questions that are later
ingested into the database.
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import time
from collections import namedtuple

Workbook = namedtuple("Workbook", "name sheet_name first_col last_row")

wb_eng = Workbook("flashcards_en", "deck 1", "H", 511)
wb_pol = Workbook("flashcards_pl", "deck 1", "K", 504)
wb_esp = Workbook("flashcards_es", "deck 1", "J", 505)

_workbooks = [wb_eng, wb_pol, wb_esp]

_path = "assets/questions/"
os.chdir(_path)

_time = time.asctime(time.localtime(
    time.time())).replace(" ", "-").replace(":", "-")

# text file where names of all used image files is stored
output_file = f"used_photos_list-{_time}.txt"

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds_path = "C:/Users/Lukasz/Python/ErroresBuenos/GCP/"

creds = ServiceAccountCredentials.from_json_keyfile_name(
    creds_path+"qwell-spreadsheets-fc83f3df64bb.json", scope)

client = gspread.authorize(creds)

photo_list = []

for wb in _workbooks:
    sheets = client.open(wb.name)
    sheet = sheets.worksheet(wb.sheet_name)

    photo1_list = sheet.range(f"{wb.first_col}2:{wb.first_col}{wb.last_row}")
    first_cell_row = photo1_list[0].row
    first_cell_col = photo1_list[0].col
    photo1_list = [cell.value for cell in photo1_list if cell.value != ""]

    photo2_list = sheet.range(2, first_cell_col+2, wb.last_row, first_cell_col+2)
    photo2_list = [cell.value for cell in photo2_list if cell.value != ""]

    photo3_list = sheet.range(2, first_cell_col+4, wb.last_row, first_cell_col+4)
    photo3_list = [cell.value for cell in photo3_list if cell.value != ""]

    photo4_list = sheet.range(2, first_cell_col+6, wb.last_row, first_cell_col+6)
    photo4_list = [cell.value for cell in photo4_list if cell.value != ""]

    photo_list.extend(photo1_list)
    photo_list.extend(photo2_list)
    photo_list.extend(photo3_list)
    photo_list.extend(photo4_list)

    print(f"{wb.name}:")
    print(len(photo1_list))
    print(len(photo2_list))
    print(len(photo3_list))
    print(len(photo4_list))
    print(len(photo_list))

print("casting the list as a set")
photo_set = set(photo_list)
print(len(photo_set))

with open(output_file, "w", encoding="utf8") as f:
    for photo_file_name in photo_set:
        f.write(photo_file_name)
        f.write("\n")
