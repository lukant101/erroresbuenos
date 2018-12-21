"""Reorders columns in Google Sheets according to image aspect ratio.

The Google Sheets are the source of truth for the questions that are later
ingested into the database.

Input:
hard-code info on each workbook:
workbook / file name
sheet name
and the range of cells holding info on the images:
first column, last column, last row
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import time
from collections import namedtuple
from timedelta_format import timedelta_format

Workbook = namedtuple("Workbook", "name sheet_name first_col last_col last_row")

wb_eng = Workbook("flashcards_en", "deck 1", "G", "N", 511)
wb_pol = Workbook("flashcards_pl", "deck 1", "H", "O", 503)
wb_esp = Workbook("flashcards_es", "deck 1", "H", "O", 502)

_workbooks = [wb_eng, wb_pol, wb_esp]

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds_path = "C:/Users/Lukasz/Python/ErroresBuenos/GCP/"

creds = ServiceAccountCredentials.from_json_keyfile_name(
    creds_path+"qwell-spreadsheets-fc83f3df64bb.json", scope)

client = gspread.authorize(creds)

start_time = time.time()

for wb in _workbooks:
    sheets = client.open(wb.name)
    sheet = sheets.worksheet(wb.sheet_name)

    read_requests = 0
    update_requests = 0
    questions_updated = 0

    for row in range(2, wb.last_row+1):
        img_list = []
        data = sheet.range(f"{wb.first_col}{row}:{wb.last_col}{row}")

        for i in range(0, len(data), 2):
            if data[i].value:
                tup = (data[i].value, float(data[i+1].value))
                print(f"tuple: {tup}")
                img_list.append(tup)

        img_list_sorted = sorted(img_list, key=lambda t: t[1])
        print(f"sorted list: {img_list_sorted}")

        read_requests += 1
        print(f"Number of read requests made: {read_requests}")
        if read_requests > 95:
            print(f"Going to sleep because reached {read_requests} read requests")
            read_requests = 0
            update_requests = 0
            print("went to sleep")
            time.sleep(100)

        update = False
        img_list_len = len(img_list)
        if img_list_len == 0:
            print(f"no image data for question at index {row-1}")
        if img_list_len > 1:
            for img1, img2 in zip(img_list, img_list_sorted):
                if img1 != img2:
                    update = True
                    break

        if update:
            col = data[0].col

            for img in img_list_sorted:
                sheet.update_cell(row, col, img[0])
                sheet.update_cell(row, col+1, img[1])
                col += 2

            update_requests += 1
            print("number of update requests made:", update_requests)
            questions_updated += 1
            print("number of questions updated: ", questions_updated)

            # Google API blocks if more than 100 read requests within 100 seconds
            # so, pause once close to 100 requests
            if update_requests >= 40:
                print("update requests before sleep:", update_requests)
                update_requests = 0
                read_requests = 0
                print("went to sleep")
                time.sleep(100)

    print(f"Finished updating workbook {wb.name}! Updated {questions_updated} questions.")

    print("going to sleep before starting the next workbook")
    time.sleep(100)

end_time = time.time()

total_time = end_time - start_time

print(f"The process took total of (hours:minutes:seconds): "
      f"{timedelta_format(total_time)}")


print("All workbooks completed!")
