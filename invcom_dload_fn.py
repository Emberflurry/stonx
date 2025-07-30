import time
import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
import pytesseract
from PIL import Image
import pyautogui
from datetime import datetime
from ivcom_tess_helpers import find_icon_locations, find_blue_box, find_and_click_year#, click_day_correct_month


def eacal(daymatch,monthmatch,yearmatch,
          dateloc,monloc,year_regiontopleftx,yearstr,
          monthstr,daynumber,td=.15):
    
    if daymatch and monthmatch and yearmatch:
        return True
    
    else:
        time.sleep(.2)
        pyautogui.moveTo(dateloc)
        time.sleep(td)
        pyautogui.click()
        time.sleep(td)
        pyautogui.moveTo(monloc)
        time.sleep(td)
        pyautogui.click()
        region = (year_regiontopleftx,533,240,300)


        #TODO: make dynamic to scroll up to find year values out of sight initially

        find_and_click_year(yearstr,region=region, confidence=.7)
        #loc = find_icon_locations(f"{yearstr}.png",region=region, confidence=0.96)
        #LL,TL = loc.left+loc.width/2, loc.top+loc.height/2
        #print(LL,TL)
        #pyautogui.moveTo(LL,TL)
        #time.sleep(td)
        #pyautogui.click() 
        time.sleep(4*td)   

        if monthmatch and yearmatch:
            print("m y match")
            center = find_blue_box(region)
            pyautogui.moveTo(center)
            time.sleep(td)
            pyautogui.click()

            time.sleep(4*td)    
        else:
            print('no my mat')
            loc = find_icon_locations(f"{monthstr}.png",region=region,confidence=.85)
            LL,TL = loc.left+loc.width/2, loc.top+loc.height/2
            pyautogui.moveTo(LL,TL)
            time.sleep(td)
            pyautogui.click() 
            time.sleep(4*td)    

        region = (year_regiontopleftx,575,250,200)
        if daymatch:
            print('sameday')
            center = find_blue_box(region)
            pyautogui.moveTo(center)
            time.sleep(2*td)
            pyautogui.click()

            time.sleep(2*td)       
        else:
            print('not samed')
            if daynumber < 15:
                print('daynum<15')
                region = (year_regiontopleftx,575,250,140)
                loc = find_icon_locations(f"{str(daynumber)}.png",region=region,confidence=.94)
                LL,TL = loc.left+loc.width/2, loc.top+3+loc.height/2
                pyautogui.moveTo(LL,TL)
                time.sleep(td)
                pyautogui.click() 
                time.sleep(td)
            else: #if day >=15
                print('daynum>=15')
                region = (year_regiontopleftx,611,250,175)
                loc = find_icon_locations(f"{str(daynumber)}.png",region=region,confidence=.94)
                LL,TL = loc.left+loc.width/2, loc.top+3+loc.height/2
                pyautogui.moveTo(LL,TL)
                time.sleep(td)
                pyautogui.click() 
                time.sleep(td)
    return True