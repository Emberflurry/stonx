import pytesseract
from PIL import Image
import pyautogui
from datetime import datetime


daynumber1 = 1
monthstr1 = "Apr"
yearstr1 = "2023"

daynumber2 = 30
monthstr2 = "May"
yearstr2 = "2023"

# Optional: Explicitly set the Tesseract path if needed
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Load an image and extract text
img = Image.open("daterange_example.png")
text = pytesseract.image_to_string(img)

print("Detected text:")
print(text)

daterange_region = (930, 748, 248, 76) #carefully crafted
screenshot = pyautogui.screenshot(region=daterange_region)
screenshot.save("daterange_box.png")

ocr_text = pytesseract.image_to_string(screenshot)
print(f"OCR result: {ocr_text}")

# Parse dates
try:
    parts = ocr_text.strip().split('-')
    if len(parts) != 2:
        raise ValueError("Could not split start and end dates")
    
    start_str = parts[0].strip()
    end_str = parts[1].strip()

    start_date = datetime.strptime(start_str, "%m/%d/%Y")
    end_date = datetime.strptime(end_str, "%m/%d/%Y")

    # Compare
    same_year_left = str(start_date.year) == yearstr1
    same_month_left = start_date.strftime("%b") == monthstr1
    same_day_left = start_date.day == daynumber1

    same_year_right = str(end_date.year) == yearstr2
    same_month_right = end_date.strftime("%b") == monthstr2
    same_day_right = end_date.day == daynumber2

    print(f"Left: {same_year_left=}, {same_month_left=}, {same_day_left=}")
    print(f"Right: {same_year_right=}, {same_month_right=}, {same_day_right=}")

except Exception as e:
    print(f"❌ Failed to parse or compare dates: {e}")
