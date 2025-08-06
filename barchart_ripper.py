import pyautogui
import pytesseract
from PIL import Image
import time
import pandas as pd
import cv2
import numpy as np
import keyboard
import re

# ---- CONFIG ---- #
# Set these manually for your setup
#FULLSCREEN WINDOW open, fullscreened

CHART_TOP_LEFT = (117, 338)   # x, y of chart's top-left corner
CHART_BOTTOM_RIGHT = (1816, 939)  # x, y of chart's bottom-right
TOOLTIP_REGION = (392, 164, 300, 25)
VOLUME_REGION = (270, 803, 100, 25)
DATE_REGION = (58, 164, 150, 28)  # example: x, y, w, h for date
HORIZONTAL_STEPS =CHART_BOTTOM_RIGHT[0]-CHART_TOP_LEFT[0] -5 #cushion
STEP_SIZE = 1 #pixel each 
#no formula needed lol^#int((CHART_BOTTOM_RIGHT[0] - CHART_TOP_LEFT[0]) / HORIZONTAL_STEPS)
DELAY = 0 #TODO change faster
initdelay = 3.5 #setup s
data = []
seen_dates = set()

print(f'starting, u have {initdelay}s')
time.sleep(initdelay)

for i in range(HORIZONTAL_STEPS):
    if keyboard.is_pressed('q'):
        print("Quit key pressed. Exiting loop.")
        break
    while keyboard.is_pressed('p'):
        print("Paused. Press 'r' to resume or 'q' to quit.")
        while not keyboard.is_pressed('r'):
            if keyboard.is_pressed('q'):
                print("Quit key pressed. Exiting loop.")
                exit()
            time.sleep(0.1)
        print("Resuming.")
        time.sleep(0.2)  # Avoid accidental double-trigger

    x = CHART_TOP_LEFT[0] + i * STEP_SIZE
    y = int((CHART_TOP_LEFT[1] + CHART_BOTTOM_RIGHT[1]) / 2)
    pyautogui.moveTo(x, y)
    time.sleep(DELAY)

    # ---- Date OCR ----
    date_img = pyautogui.screenshot(region=DATE_REGION)
    text = pytesseract.image_to_string(
    date_img.convert('L'), config='--psm 7 -c tessedit_char_whitelist=0123456789.,'
).strip()
    print(f"dateOCR: '{text}'")
    date = re.search(r'\d{8}',text)
    if date:
        date = date.group()
        date = f"{date[:2]}/{date[2:4]}/{date[4:]}"
    else:
        date = None  # or set to date_text for debugging

    # ---- Tooltip OCR (OHLC) ----
    tooltip_img = pyautogui.screenshot(region=TOOLTIP_REGION)
    text = pytesseract.image_to_string(
        tooltip_img.convert('L'),
        config='--psm 6 -c tessedit_char_whitelist=OHLC0123456789. '
    ).strip()
    print(f"OCR OHLC text: '{text}'")  # Debug

    # 1. Try to extract values by label
    matches = re.findall(r'([OHLC])\s*([0-9]*\.[0-9]+)', text)
    d = {k.lower(): v for k, v in matches}

    # 2. Fallback: If missing any of o/h/l/c, extract all numbers in order
    nums = re.findall(r'[0-9]*\.[0-9]+', text)
    if len(nums) == 4:
        # Always assign by standard order
        ohlc_keys = ['o', 'h', 'l', 'c']
        for k, v in zip(ohlc_keys, nums):
            d.setdefault(k, v)  # Don't overwrite existing matches
    elif len(nums) == 3:
        # Sometimes Open gets mangled, try best-effort mapping
        ohlc_keys = ['h', 'l', 'c'] if 'o' not in d else ['o', 'h', 'c']
        for k, v in zip(ohlc_keys, nums):
            d.setdefault(k, v)

    print(f"Extracted OHLC: {d}")

    # ---- Volume OCR ----
    vol_img = pyautogui.screenshot(region=VOLUME_REGION)
    vol_text = pytesseract.image_to_string(vol_img, config='--psm 7 -c tessedit_char_whitelist=0123456789,').strip()
    #print(f"OCR result: '{vol_text}'")

    vol_val = None
    for word in vol_text.split():
        if word.replace(',', '').isdigit():
            vol_val = word.replace(',', '')
            break
    #print(f"OCR volume region raw output: '{vol_text}'")
    #vol_img = pyautogui.screenshot(region=VOLUME_REGION)
    #vol_img.save(f'vol_test_{i}.png')#q

    if date and date not in seen_dates:
        outrow = {'date': date}
        outrow.update(d)
        outrow['volume'] = vol_val
        data.append(outrow)
        seen_dates.add(date)
        print(f"{i+1}/{HORIZONTAL_STEPS}|{date or 'No date'} | {outrow}")
    else:
        
        print(f"{i+1}/{HORIZONTAL_STEPS}|{date or 'No date'} | (duplicate or invalid, skipped)")
# ---- Output ----
df = pd.DataFrame(data)
df.to_csv('mics_chart_ohlcv.csv', index=False)
print("Saved to mics_chart_ohlcv.csv")