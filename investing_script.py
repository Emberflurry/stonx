import time
import pyautogui
import pygetwindow as gw

# === CONFIG ===
td = 0.75  # general wait time between actions
initwait = 7  # initial buffer for final page load
initscrolldist = -480  # scroll amount

# === DESIRED DATES ===
daynumber1 = 1
monthstr1 = "Apr"
yearstr1 = "2023"

daynumber2 = 30
monthstr2 = "May"
yearstr2 = "2023"

# === HELPERS ===
def find_icon_locations(icon_path, confidence=0.85):
    locations = list(pyautogui.locateAllOnScreen(icon_path, confidence=confidence))
    if not locations:
        raise Exception(f"No instances of icon found: {icon_path}")
    centers = [pyautogui.center(loc) for loc in locations]
    centers_sorted = sorted(centers, key=lambda pt: pt.x)
    return centers_sorted

def click_day_correct_month(day_icon_path, region, day, confidence=0.95):
    matches = list(pyautogui.locateAllOnScreen(day_icon_path, region=region, confidence=confidence))
    if not matches:
        raise Exception(f"No matches found for {day_icon_path} in region {region}")
    matches_sorted = sorted(matches, key=lambda r: r.top)
    index = 0 if day <= 15 else 1
    if len(matches) >2:
        raise Exception(f"Expected at most 2 matches, not {len(matches)}.sorted: {matches_sorted}")
    pyautogui.moveTo(pyautogui.center(matches_sorted[index]))
    time.sleep(td)
    pyautogui.click()

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
# === STEP 3: Click Calendar ===
click_icon = find_icon_locations("calendar_icon.png")[0]
pyautogui.moveTo(click_icon)
time.sleep(td)
pyautogui.click()
time.sleep(td)


# === STEP 4: LEFT calendar date entry ===
leftcal_icon = find_icon_locations("calendar_icon.png")[0]
pyautogui.moveTo(leftcal_icon)
time.sleep(td)
pyautogui.click()
time.sleep(td)

# Year dropdown
arrow_icon = find_icon_locations("cal_downarrow.png", confidence=0.94)[0]
adj_arrow_icon = pyautogui.Point(arrow_icon.x-200,arrow_icon.y)
pyautogui.moveTo(adj_arrow_icon)
time.sleep(td)
pyautogui.click()
time.sleep(td)
# Year
yr_icon = find_icon_locations(f"{yearstr1}.png", confidence=0.94)[0]
pyautogui.moveTo(yr_icon)
time.sleep(td)
pyautogui.click()
time.sleep(td)
# Month
month_icon = find_icon_locations(f"{monthstr1}.png",confidence=.8)[0]
pyautogui.moveTo(month_icon)
time.sleep(td)
pyautogui.click()
time.sleep(td)

# Find and click day
anchor_pos = pyautogui.locateOnScreen("cal_downarrow.png", confidence=0.9)
anchor_x, anchor_y = anchor_pos.left, anchor_pos.top
region = (int(anchor_x - 225), int(anchor_y + 40), 285, 250)
click_day_correct_month(f"{daynumber1}.png", region, daynumber1, confidence=0.9)
time.sleep(td)


# === STEP 5: RIGHT calendar ===
rightcal_icon = find_icon_locations("calendar_icon.png")[1]
pyautogui.moveTo(rightcal_icon)
time.sleep(td)
pyautogui.click()
time.sleep(td)
# Year
arrow_icon2 = find_icon_locations("cal_downarrow.png", confidence=0.9)[0]
adj_arrow_icon2 = pyautogui.Point(arrow_icon2.x-200,arrow_icon2.y)
pyautogui.moveTo(adj_arrow_icon2)
time.sleep(td)
pyautogui.click()
time.sleep(td)
yr_icon2 = find_icon_locations(f"{yearstr2}.png", confidence=0.94)[0]
pyautogui.moveTo(yr_icon2)
time.sleep(td)
pyautogui.click()
time.sleep(td)
# Month
month_icon2 = find_icon_locations(f"{monthstr2}.png",confidence=.7)[0]
pyautogui.moveTo(month_icon2)
time.sleep(td)
pyautogui.click()
time.sleep(td)

# Region for day grid
anchor_pos2 = pyautogui.locateOnScreen("cal_downarrow.png", confidence=0.9)
anchor_x2, anchor_y2 = anchor_pos2.left, anchor_pos2.top
region2 = (int(anchor_x2 - 225), int(anchor_y2 + 40), 285, 250)
click_day_correct_month(f"{daynumber2}.png", region2, daynumber2, confidence=0.85)
time.sleep(td)
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
