"""Updates Google Sheets that store questions: adds image aspect ratios.

Supported file formats: all raster image formats supported by PILLOW.

Input: text file with svg file names and corresponding image aspect ratio.
"""

import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

workbook_name = "Flashcards_pol"
sheet_name = "deck 1"

# full path to input file
_file = "C:/Users/Lukasz/Python/ErroresBuenos/assets/\
photos/svg_aspect_ratio/svg_images_aspect_ratio.txt"

scope = (['https://spreadsheets.google.com/feeds',
          'https://www.googleapis.com/auth/drive'])
creds_path = "C:/Users/Lukasz/Python/ErroresBuenos/GCP/"
creds = ServiceAccountCredentials.from_json_keyfile_name(
    creds_path+"qwell-spreadsheets-fc83f3df64bb.json", scope)
client = gspread.authorize(creds)

sheets = client.open(workbook_name)

sheet = sheets.worksheet(sheet_name)

read_req = 0
write_req = 0
img_updated = 0

with open(_file, "r", encoding="utf8") as f:
    for line in f.readlines():
        _file, aspect_ratio = line.split()
        _file = _file.rstrip(",")
        print(_file)
        print(aspect_ratio)

        cells = sheet.findall(_file)
        read_req += 1
        print("read requests: ", read_req)

        for c in cells:
            sheet.update_cell(c.row, c.col+1, aspect_ratio)
            write_req += 1
            print("write requests: ", write_req)

        # Google API blocks if more than 100 read requests within 100 seconds
        # so, pause once close to 100 requests
        if read_req >= 98 or write_req >= 98:
            print("read requests before sleep:", read_req)
            print("write requests before sleep: ", write_req)
            read_req = 0
            write_req = 0
            print("went to sleep")
            time.sleep(90)
            print("woke up")
        img_updated += 1
        print("number of images updated: ", img_updated)

print("Finished!")
