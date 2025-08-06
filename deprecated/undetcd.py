import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time

# Path to your Chrome user data directory (not just 'Default' but the parent)
chrome_user_data_dir = r"C:\Users\John DeForest\AppData\Local\Google\Chrome\User Data"

# Profile directory - likely "Default", or check in Chrome's settings if you use multiples
profile_dir = "Default"

options = uc.ChromeOptions()
options.user_data_dir = chrome_user_data_dir
options.add_argument(f'--profile-directory={profile_dir}')
options.add_argument('--start-maximized')

driver = uc.Chrome(options=options)

# Go to investing.com (you should be logged in automatically)
driver.get("https://www.investing.com/")
time.sleep(5)  # Let it fully load

# Example: Loop through URLs (replace summary.iterrows() with your own code)
for idx, row in summary.iterrows():
    icom_url = row['icom_url']
    trade_date = str(row['trade_date'])

    driver.get(icom_url)
    # Wait for a key element, or just sleep longer if needed
    time.sleep(7)  # Increase if slow! Or use WebDriverWait for a specific element

    # ...do your scraping, downloading, etc...

    # Optionally call your puller script
    # subprocess.run(['python', 'invcom_single_puller2.py', trade_date])
    print(f'Processed: {icom_url}')

driver.quit()
