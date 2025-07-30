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


