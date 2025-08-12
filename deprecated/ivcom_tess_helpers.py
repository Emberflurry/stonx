import time
import pyautogui
import pygetwindow as gw
import pytesseract
from PIL import Image
import pyautogui
from datetime import datetime
import numpy as np
import cv2
from collections import namedtuple
Box = namedtuple("Box", "left top width height") 

# === HELPERS ===
def find_icon_locations(icon_path,region, confidence=0.85,color=False):
    if not color:
        locations = list(pyautogui.locateAllOnScreen(icon_path, region=region, confidence=confidence))
        if not locations:
            return False
        return locations[0] if len(locations) == 1 else locations[0]  # crude fallback
    else:
        screen = pyautogui.screenshot(region=region)
        screen_rgb = np.array(screen)
        template = cv2.imread(icon_path, cv2.IMREAD_COLOR)

        result = cv2.matchTemplate(screen_rgb, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        print(f"[DEBUG] max_val: {max_val:.4f}, threshold: {confidence}")
        if max_val >= confidence:
            h, w = template.shape[:2]
            Box = namedtuple("Box", ["left", "top", "width", "height"])
            return Box(region[0] + max_loc[0], region[1] + max_loc[1], w, h)
        else:
            return False

import pyautogui
import numpy as np
import cv2

def find_blue_box(region, min_area=300):
    """
    Detects the largest blue region in the screen capture of the given region.
    
    Args:
        region (tuple): (left, top, width, height)
        min_area (int): minimum contour area to consider

    Returns:
        (x, y): center coordinates of the blue box
    """
    # Screenshot of region
    img = np.array(pyautogui.screenshot(region=region))
    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

    # Blue color range in HSV (adjust as needed)
    lower_blue = np.array([100, 120, 70])
    upper_blue = np.array([140, 255, 255])

    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        raise Exception("No blue regions found.")

    # Find largest blue contour
    largest = max(contours, key=cv2.contourArea)
    if cv2.contourArea(largest) < min_area:
        raise Exception("Blue area too small.")

    x, y, w, h = cv2.boundingRect(largest)
    center_x = region[0] + x + w // 2
    center_y = region[1] + y + h // 2

    return (center_x, center_y)


import pyautogui
import numpy as np
import cv2
import pytesseract
import time

def find_and_click_year(target_year: str, region, confidence=0.85):
    """
    Tries to find and click the specified year string in the given region.
    Falls back to OCR if template matching fails.
    """
    try:
        # First try template match using screenshot
        template = cv2.imread(f"{target_year}.png", cv2.IMREAD_GRAYSCALE)
        screenshot = pyautogui.screenshot(region=region)
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)

        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val >= confidence:
            x, y = max_loc
            h, w = template.shape
            click_x = region[0] + x + w // 2
            click_y = region[1] + y + h // 2
            pyautogui.moveTo(click_x, click_y)
            time.sleep(.15)
            pyautogui.click()
            return True
        else:
            raise Exception(f"Low confidence ({max_val:.2f}) on {target_year}.png")

    except Exception as e:
        print(f"[Template Fail] {e}")
        print("[Fallback] Using OCR to find year...")

        # Fallback: OCR
        screenshot = pyautogui.screenshot(region=region)
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        d = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

        for i, text in enumerate(d['text']):
            if text.strip() == target_year:
                x = d['left'][i]
                y = d['top'][i]
                w = d['width'][i]
                h = d['height'][i]
                cx = region[0] + x + w // 2
                cy = region[1] + y + h // 2
                pyautogui.moveTo(cx, cy)
                pyautogui.click()
                return True

        print(f"[OCR Fail] Could not find {target_year}")
        return False


