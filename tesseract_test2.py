import pytesseract
from PIL import Image
import pyautogui
from datetime import datetime
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

#early testing only on known png: Load an image and extract text
img = Image.open("daychart_full_test29.png")
text = pytesseract.image_to_string(img)
print("Detected text:")
print(text)

img = Image.open("monthchart_fulltest_2023apr.png")
text = pytesseract.image_to_string(img)
print("Detected text:")
print(text)