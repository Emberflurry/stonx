import time
import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
import pytesseract
from PIL import Image
import pyautogui
from datetime import datetime
from invcom_dload_fn import eacal
from ivcom_tess_helpers import find_icon_locations, find_blue_box#, click_day_correct_month
# Optional: Explicitly set the Tesseract path if needed
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# === CONFIG ===
td = .05  # general wait time between actions
initwait = 3.5  # initial buffer for final page load
initscrolldist = -480  # scroll amount MUST KEEP AT -480
# === DESIRED DATES ===
#TODO: convert to slick date parsing imports from openinsider/model needs
daynumber1 = 15
monthstr1 = "Jun"
monthnum1 = 6
yearstr1 = "2022"

daynumber2 = 29
monthstr2 = "Jul"
monthnum2 = 7
yearstr2 = "2023"

monthdayblusq = 'Apr1.png'
#might need to snip more and make dynamic, but might work just detecting blue

# === STEP 1: MANUAL PAGE SETUP ===
input("👉 Open Investing.com historical data page in regular Chrome. Log in manually. Press 'y' and Enter when ready: ")
print(f"Waiting {initwait}s for any final loading...")
time.sleep(initwait)
starttime = time.time()

# Focus Chrome window
for w in gw.getWindowsWithTitle("Investing.com"):
    if w.isActive:
        w.activate()
        break
time.sleep(td)

# === STEP 2: Initial DOOMScroll ===
pyautogui.scroll(initscrolldist)
time.sleep(td)

daterange_region = (930, 748, 248, 76) #carefully crafted
screenshot = pyautogui.screenshot(region=daterange_region)
#screenshot.save("daterange_box.png") #for manual checking if needed
ocr_text = pytesseract.image_to_string(screenshot)
print(f"OCR result: {ocr_text}")
dates = ocr_text.strip().split('-')
d1,d2 = dates[0].strip(),dates[1].strip()
date1,date2 = datetime.strptime(d1,"%m/%d/%Y"), datetime.strptime(d2,"%m/%d/%Y")
sameyear1 = str(date1.year) == yearstr1
sameyear2 = str(date2.year) == yearstr2
samemonth1 = str(date1.month) == str(monthnum1)
samemonth2 = str(date2.month) == str(monthnum2)
sameday1 = str(date1.day) == str(daynumber1)
sameday2 = str(date2.day) == str(daynumber2)
print(d1,d2)
print(date1,date2)
print(sameyear1,sameyear2)
print(samemonth1,samemonth2)
print(sameday1,sameday2)

#click daterange
pyautogui.moveTo(1060,780)
time.sleep(td)
pyautogui.click()
time.sleep(td)

#LEFT = 1, RIGHT = 2
dateloc1 = (935,850)
monloc1 = (895,510)
dateloc2 = (1113,850)
monloc2 =(1080,510)
# year region toplefx: region = (855,533,240,300)

Lcalgood = eacal(sameday1,samemonth1,sameyear1,
          dateloc1,monloc1,855,yearstr1,
          monthstr1,daynumber1,td=td)
if Lcalgood:
    print('start date all set')
    pass
time.sleep(.5)
Rcalgood = eacal(sameday2,samemonth2,sameyear2,
          dateloc2,monloc2,1040,yearstr2,
          monthstr2,daynumber2,td=td)
if Rcalgood:
    print('end date all set')
    pass
time.sleep(.3)
daterange_region = (930, 748, 248, 76) #carefully crafted
screenshot = pyautogui.screenshot(region=daterange_region)
#screenshot.save("daterange_box.png") #for manual checking if needed
ocr_text = pytesseract.image_to_string(screenshot)
print(f"OCRres: {ocr_text} should match {monthnum1}/{daynumber1}/{yearstr1} - {monthnum2}/{daynumber2}/{yearstr2}")

apply_btn = pyautogui.locateCenterOnScreen("Apply.png", confidence=0.85)
if apply_btn:
    pyautogui.moveTo(apply_btn)
    time.sleep(td)
    pyautogui.click()
    time.sleep(td)

download_btn = pyautogui.locateCenterOnScreen("download_button.png", confidence=0.85)
if download_btn:
    pyautogui.moveTo(download_btn)
    time.sleep(td)
    pyautogui.click()

print(f"✅ Download init'd. Totrtime:{round(time.time()-starttime,2)}s")
