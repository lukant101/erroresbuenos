"""Translate hints and update the Google Sheets.

The Google Sheets are the source of truth for the questions that are later
ingested into the database.

Sheets contain hints in English. This script translates the hints using
Google Translate and inserts the translation into the Google Sheets
for the corresponding language.


Input:
hard-code info on each workbook:
workbook / file name
sheet name
last row of data in the sheet
and the range of cells holding info on the images:
first column, second column, last row

Pre-requisites:
Column names in the Sheets:
"English Hint" is column X
"Hint" is column Y
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
from google.cloud import translate
from collections import namedtuple
from timedelta_format import timedelta_format

translate_client = translate.Client()

Workbook = namedtuple("Workbook", "language name sheet_name first_col sec_col last_row")

wb_pol = Workbook("pl", "flashcards_pl", "deck 1", "X", "Y", 496)
wb_esp = Workbook("es", "flashcards_es", "deck 1", "X", "Y", 497)

_workbooks = [wb_pol, wb_esp]

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

    update_requests = 0
    hints_updated = 0

    eng_hints = sheet.range(f"{wb.first_col}2:{wb.first_col}{wb.last_row}")

    for eng_hint in eng_hints:
        if eng_hint.value:
            eng_hint
            hint = translate_client.translate(eng_hint.value,
                                              target_language=wb.language,
                                              source_language="en")

            sheet.update_cell(eng_hint.row, eng_hint.col+1, hint["translatedText"])
            update_requests += 1
            hints_updated += 1
            print(f"English hint: {eng_hint.value}")
            print(f"Translated hint: {hint['translatedText']}")

            # Google API blocks if more than 100 requests made within 100 seconds
            # so, pause once close to 100 requests
            if update_requests > 95:
                update_requests = 0
                print("went to sleep")
                time.sleep(100)

    print(f"Finished updating workbook {wb.name}! Updated {hints_updated} hints.")

    print("going to sleep before starting the next workbook")
    time.sleep(100)

end_time = time.time()

total_time = end_time - start_time

print(f"The process took total of (hours:minutes:seconds): "
      f"{timedelta_format(total_time)}")

print("All workbooks completed!")
