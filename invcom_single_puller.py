import time
import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
import pytesseract
from PIL import Image
import pyautogui
from datetime import datetime
from ivcom_tess_helpers import find_icon_locations, find_blue_box#, click_day_correct_month
# Optional: Explicitly set the Tesseract path if needed
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# === CONFIG ===
td = .25  # general wait time between actions
initwait = 3.2  # initial buffer for final page load
initscrolldist = -480  # scroll amount MUST KEEP AT -480
# === DESIRED DATES ===
#TODO: convert to slick date parsing imports from openinsider/model needs
daynumber1 = 1
monthstr1 = "Apr"
monthnum1 = 4
yearstr1 = "2023"
daynumber2 = 30
monthstr2 = "May"
monthnum2 = 5
yearstr2 = "2023"

monthdayblusq = 'Apr1.png'
#might need to snip more and make dynamic, but might work just detecting blue

# === STEP 1: MANUAL PAGE SETUP ===
input("👉 Open Investing.com historical data page in regular Chrome. Log in manually. Press 'Y' and Enter when ready: ")
print(f"Waiting {initwait}s for any final loading...")
time.sleep(initwait)
starttime = time.time()

# Focus Chrome window
for w in gw.getWindowsWithTitle("Investing.com"):
    if w.isActive:
        w.activate()
        break
time.sleep(td)

# === STEP 2: Initial Scroll ===
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

#LEFT
dateloc1 = (935,850)
monloc1 = (895,510)
dateloc2 = (1113,850)
monloc2 =(1080,510)
# year region toplefx: region = (855,533,240,300)
def eacal(daymatch,monthmatch,yearmatch,
          dateloc,monloc,year_regiontopleftx,yearstr,
          monthstr,daynumber):
    
    if daymatch and monthmatch and yearmatch:
        return True
    else:
        pyautogui.moveTo(dateloc)
        time.sleep(td)
        pyautogui.click()
        time.sleep(td)
        pyautogui.moveTo(monloc)
        time.sleep(td)
        pyautogui.click()
        region = (year_regiontopleftx,533,240,300)
        loc = find_icon_locations(f"{yearstr}.png",region=region, confidence=0.96)
        LL,TL = loc.left+loc.width/2, loc.top+loc.height/2
        #print(LL,TL)
        pyautogui.moveTo(LL,TL)
        time.sleep(td)
        pyautogui.click() 
        time.sleep(td)   

        if monthmatch and yearmatch:
            print("m y match")
            center = find_blue_box(region)
            pyautogui.moveTo(center)
            time.sleep(td)
            pyautogui.click()
            #loc = find_icon_locations(monthdayblusq,region=region,confidence=.2,color=True)
            #print(loc)
            #LL,TL = loc.left+loc.width/2, loc.top+loc.height/2
            #print(LL,TL)
            #pyautogui.moveTo(LL,TL)
            # time.sleep(td)
            # pyautogui.click() 
            time.sleep(td)    
        else:
            print('no my mat')
            loc = find_icon_locations(f"{monthstr}.png",region=region,confidence=.85)
            LL,TL = loc.left+loc.width/2, loc.top+loc.height/2
            pyautogui.moveTo(LL,TL)
            time.sleep(td)
            pyautogui.click() 
            time.sleep(td)    

        region = (year_regiontopleftx,575,250,200)
        if sameday1:
            print('sameday')
            center = find_blue_box(region)
            pyautogui.moveTo(center)
            time.sleep(td)
            pyautogui.click()
            # loc = find_icon_locations(monthdayblusq,region=region,confidence=.2,color=True)
            # LL,TL = loc.left+loc.width/2, loc.top+loc.height/2
            # pyautogui.moveTo(LL,TL)
            # time.sleep(td)
            # pyautogui.click() 
            time.sleep(td)       
        else:
            print('not samed')
            if daynumber1 < 15:
                print('daynum<15')
                region = (year_regiontopleftx,575,250,140)
                loc = find_icon_locations(f"{str(daynumber)}.png",region=region,confidence=.85)
                LL,TL = loc.left+loc.width/2, loc.top+loc.height/2
                pyautogui.moveTo(LL,TL)
                time.sleep(td)
                pyautogui.click() 
                time.sleep(td)
            else: #if day >=15
                print('daynum>=15')
                region = (year_regiontopleftx,611,250,175)
                loc = find_icon_locations(f"{str(daynumber)}.png",region=region,confidence=.85)
                LL,TL = loc.left+loc.width/2, loc.top+loc.height/2
                pyautogui.moveTo(LL,TL)
                time.sleep(td)
                pyautogui.click() 
                time.sleep(td)
    return True

Lcalgood = eacal(sameday1,samemonth1,sameyear1,
          dateloc1,monloc1,855,yearstr1,
          monthstr1,daynumber1)
if Lcalgood:
    print('start date all set')
    pass

Rcalgood = eacal(sameday2,samemonth2,sameyear2,
          dateloc2,monloc2,1040,yearstr2,
          monthstr2,daynumber2)
if Rcalgood:
    print('end date all set')
    pass

# if sameday1 and samemonth1 and sameyear1:
#     pass
# else:
#     pyautogui.moveTo(Ldateloc)
#     time.sleep(td)
#     pyautogui.click()
#     time.sleep(td)
#     pyautogui.moveTo(Lmonloc)
#     time.sleep(td)
#     pyautogui.click()
#     region = (855,533,240,300)
#     loc = find_icon_locations(f"{yearstr1}.png",region=region, confidence=0.94)
#     LL,TL = loc.left+loc.width/2, loc.top+loc.height/2
#     print(LL,TL)
#     pyautogui.moveTo(LL,TL)
#     time.sleep(td)
#     pyautogui.click() 
#     time.sleep(td)   

#     if samemonth1 and sameyear1:
#         loc = find_icon_locations(monthdayblusq,region=region,confidence=.85)
#         LL,TL = loc.left+loc.width/2, loc.top+loc.height/2
#         pyautogui.moveTo(LL,TL)
#         time.sleep(td)
#         pyautogui.click() 
#         time.sleep(td)    
#     else:
#         loc = find_icon_locations(f"{monthstr1}.png",region=region,confidence=.85)
#         LL,TL = loc.left+loc.width/2, loc.top+loc.height/2
#         pyautogui.moveTo(LL,TL)
#         time.sleep(td)
#         pyautogui.click() 
#         time.sleep(td)    

#     region = (855,575,250,200)
#     if sameday1:
#         loc = find_icon_locations(monthdayblusq,region=region,confidence=.85)
#         LL,TL = loc.left+loc.width/2, loc.top+loc.height/2
#         pyautogui.moveTo(LL,TL)
#         time.sleep(td)
#         pyautogui.click() 
#         time.sleep(td)       
#     else:
#         if daynumber1 < 15:
#             region = (855,575,250,140)
#             loc = find_icon_locations(f"{str(daynumber1)}.png",region=region,confidence=.85)
#             LL,TL = loc.left+loc.width/2, loc.top+loc.height/2
#             pyautogui.moveTo(LL,TL)
#             time.sleep(td)
#             pyautogui.click() 
#             time.sleep(td)
#         else: #if day >=15
#             region = (855,611,250,175)
#             loc = find_icon_locations(f"{str(daynumber1)}.png",region=region,confidence=.85)
#             LL,TL = loc.left+loc.width/2, loc.top+loc.height/2
#             pyautogui.moveTo(LL,TL)
#             time.sleep(td)
#             pyautogui.click() 
#             time.sleep(td)



        



quit()




# # === STEP 3: Click Calendar ===
# click_icon = find_icon_locations("calendar_icon.png")
# pyautogui.moveTo(click_icon)
# time.sleep(td)
# pyautogui.click()
# time.sleep(td)


# # === STEP 4: LEFT calendar date entry ===
# leftcal_icon = find_icon_locations("calendar_icon.png")
# pyautogui.moveTo(leftcal_icon)
# time.sleep(td)
# pyautogui.click()
# time.sleep(td)

# # Year dropdown
# arrow_icon = find_icon_locations("cal_downarrow.png", confidence=0.94)[0]
# adj_arrow_icon = pyautogui.Point(arrow_icon.x-200,arrow_icon.y)
# pyautogui.moveTo(adj_arrow_icon)
# time.sleep(td)
# pyautogui.click()
# time.sleep(td)
# # Year
# yr_icon = find_icon_locations(f"{yearstr1}.png", confidence=0.94)[0]
# pyautogui.moveTo(yr_icon)
# time.sleep(td)
# pyautogui.click()
# time.sleep(td)
# # Month
# month_icon = find_icon_locations(f"{monthstr1}.png",confidence=.8)[0]
# pyautogui.moveTo(month_icon)
# time.sleep(td)
# pyautogui.click()
# time.sleep(td)

# # Find and click day
# anchor_pos = pyautogui.locateOnScreen("cal_downarrow.png", confidence=0.9)
# anchor_x, anchor_y = anchor_pos.left, anchor_pos.top
# region = (int(anchor_x - 225), int(anchor_y + 40), 285, 250)
# click_day_correct_month(f"{daynumber1}.png", region, daynumber1, confidence=0.9)
# time.sleep(td)


# # === STEP 5: RIGHT calendar ===
# rightcal_icon = find_icon_locations("calendar_icon.png")[1]
# pyautogui.moveTo(rightcal_icon)
# time.sleep(td)
# pyautogui.click()
# time.sleep(td)
# # Year
# arrow_icon2 = find_icon_locations("cal_downarrow.png", confidence=0.9)[0]
# adj_arrow_icon2 = pyautogui.Point(arrow_icon2.x-200,arrow_icon2.y)
# pyautogui.moveTo(adj_arrow_icon2)
# time.sleep(td)
# pyautogui.click()
# time.sleep(td)
# yr_icon2 = find_icon_locations(f"{yearstr2}.png", confidence=0.94)[0]
# pyautogui.moveTo(yr_icon2)
# time.sleep(td)
# pyautogui.click()
# time.sleep(td)
# # Month
# month_icon2 = find_icon_locations(f"{monthstr2}.png",confidence=.7)[0]
# pyautogui.moveTo(month_icon2)
# time.sleep(td)
# pyautogui.click()
# time.sleep(td)

# # Region for day grid
# anchor_pos2 = pyautogui.locateOnScreen("cal_downarrow.png", confidence=0.9)
# anchor_x2, anchor_y2 = anchor_pos2.left, anchor_pos2.top
# region2 = (int(anchor_x2 - 225), int(anchor_y2 + 40), 285, 250)
# click_day_correct_month(f"{daynumber2}.png", region2, daynumber2, confidence=0.85)
# time.sleep(td)
# === FINAL: Click Apply + Download ===
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

print(f"✅ Download initiated. Totrtime:{time.time()-starttime}s")
