"""Updates Google Sheets that store questions: adds image aspect ratios.

Supported file formats: all raster image formats supported by PILLOW.

Input: folder with raster images.
"""

from PIL import Image
from os import listdir
from os.path import isfile, join
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

workbook_name = "Flashcards_pol"
sheet_name = "deck 1"

# path to folder where images are located
_path = "C:/Users/Lukasz/Python/ErroresBuenos/assets/\
photos/raster_img_aspect_ratio/"

scope = (['https://spreadsheets.google.com/feeds',
          'https://www.googleapis.com/auth/drive'])
creds_path = "C:/Users/Lukasz/Python/ErroresBuenos/GCP/"
creds = ServiceAccountCredentials.from_json_keyfile_name(
    creds_path+"qwell-spreadsheets-fc83f3df64bb.json", scope)
client = gspread.authorize(creds)

sheets = client.open(workbook_name)

sheet = sheets.worksheet(sheet_name)

files = [f for f in listdir(_path) if isfile(join(_path, f))]

img_list = []

for f in files:
    img = Image.open(_path+f)
    w, h = img.size
    aspect_ratio = round(w/h, 3)
    img_list.append((f, aspect_ratio))
    print(f)

read_req = 0
write_req = 0
img_updated = 0

for img in img_list:
    cell = sheet.findall(img[0])
    read_req += 1
    print("read requests: ", read_req)
    for c in cell:
        sheet.update_cell(c.row, c.col+1, img[1])
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
        time.sleep(100)
        print("woke up")
    img_updated += 1
    print("number of images updated: ", img_updated)

print("Finished!")
