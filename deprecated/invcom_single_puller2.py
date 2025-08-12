import argparse
import time
import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
import pytesseract
from PIL import Image
from datetime import datetime
import pandas as pd  # Used for business day date math

from invcom_dload_fn import eacal
from ivcom_tess_helpers import find_icon_locations, find_blue_box  #, click_day_correct_month

# Optional: Explicitly set the Tesseract path if needed
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# === CONFIG ===
td = .05  # general wait time between actions
initwait = 3.5  # initial buffer for final page load
initscrolldist = -480  # scroll amount MUST KEEP AT -480
monthdayblusq = 'Apr1.png'

def get_trading_day_range(center_date, before_days=252, after_days=252):
    """
    Returns two dates:
    center_date should be trade_date from OIP pull
    - before: 'before_days' business days before 'center_date'
    - after:  'after_days' business days after 'center_date'
    """
    # Use pandas bdate_range for business days (Mon-Fri, no market holidays)
    before = pd.bdate_range(end=center_date, periods=before_days + 1)[0]
    after = pd.bdate_range(start=center_date, periods=after_days + 1)[-1]
    return before, after

def run_invcom_puller(trade_date):
    # --- Parse trade_date ---
    if isinstance(trade_date, str):
        trade_date = pd.to_datetime(trade_date)
    else:
        trade_date = pd.to_datetime(str(trade_date))

    # --- Calculate business day window ---
    date1, date2 = get_trading_day_range(trade_date)
    # For use in eacal and the rest of the script
    daynumber1 = date1.day
    monthstr1 = date1.strftime("%b")
    monthnum1 = date1.month
    yearstr1 = str(date1.year)

    daynumber2 = date2.day
    monthstr2 = date2.strftime("%b")
    monthnum2 = date2.month
    yearstr2 = str(date2.year)

    # === MANUAL PAGE SETUP ===
    input("👉 Open Investing.com historical data page in regular Chrome. Log in manually. Press 'y' and Enter when ready: ")
    print(f"Waiting {initwait}s for any final loading...")
    time.sleep(initwait)
    starttime = time.time()

    # Focus Chrome window (by window title)
    for w in gw.getWindowsWithTitle("Investing.com"):
        if w.isActive:
            w.activate()
            break
    time.sleep(td)

    # === STEP 2: Initial DOOMScroll ===
    pyautogui.scroll(initscrolldist)
    time.sleep(td)

    daterange_region = (930, 748, 248, 76)  # carefully crafted
    screenshot = pyautogui.screenshot(region=daterange_region)
    ocr_text = pytesseract.image_to_string(screenshot)
    print(f"OCR result: {ocr_text}")
    dates = ocr_text.strip().split('-')
    if len(dates) != 2:
        print("OCR did not detect two dates as expected! Please check region or page layout.")
        return
    d1, d2 = dates[0].strip(), dates[1].strip()
    date1_screen, date2_screen = datetime.strptime(d1, "%m/%d/%Y"), datetime.strptime(d2, "%m/%d/%Y")

    sameyear1 = str(date1_screen.year) == yearstr1
    sameyear2 = str(date2_screen.year) == yearstr2
    samemonth1 = str(date1_screen.month) == str(monthnum1)
    samemonth2 = str(date2_screen.month) == str(monthnum2)
    sameday1 = str(date1_screen.day) == str(daynumber1)
    sameday2 = str(date2_screen.day) == str(daynumber2)
    print('d',d1, d2)
    print('full',date1_screen, date2_screen)
    print('y',sameyear1, sameyear2)
    print('m',samemonth1, samemonth2)
    print('day',sameday1, sameday2)

    # click daterange
    pyautogui.moveTo(1060, 780)
    time.sleep(td)
    pyautogui.click()
    time.sleep(td)

    # LEFT = 1, RIGHT = 2
    dateloc1 = (935, 850)
    monloc1 = (895, 510)
    dateloc2 = (1113, 850)
    monloc2 = (1080, 510)
    # year region toplefx: region = (855,533,240,300)

    Lcalgood = eacal(sameday1, samemonth1, sameyear1,
                     dateloc1, monloc1, 855, yearstr1,
                     monthstr1, daynumber1, td=td)
    if Lcalgood:
        print('start date all set')
    time.sleep(.5)
    Rcalgood = eacal(sameday2, samemonth2, sameyear2,
                     dateloc2, monloc2, 1040, yearstr2,
                     monthstr2, daynumber2, td=td)
    if Rcalgood:
        print('end date all set')
    time.sleep(.3)
    # Confirm new date range
    daterange_region = (930, 748, 248, 76)  # carefully crafted
    screenshot = pyautogui.screenshot(region=daterange_region)
    ocr_text = pytesseract.image_to_string(screenshot)
    print(f"OCRres: {ocr_text} should match {monthnum1}/{daynumber1}/{yearstr1} - {monthnum2}/{daynumber2}/{yearstr2}")

    # Click "Apply"
    apply_btn = pyautogui.locateCenterOnScreen("Apply.png", confidence=0.85)
    if apply_btn:
        pyautogui.moveTo(apply_btn)
        time.sleep(td)
        pyautogui.click()
        time.sleep(td)

    # Click "Download"
    download_btn = pyautogui.locateCenterOnScreen("download_button.png", confidence=0.85)
    if download_btn:
        pyautogui.moveTo(download_btn)
        time.sleep(td)
        pyautogui.click()

    print(f"✅ Download init'd. Totrtime:{round(time.time()-starttime,2)}s")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("trade_date", type=str, help="Trade date in YYYY-MM-DD format")
    args = parser.parse_args()
    run_invcom_puller(args.trade_date)
