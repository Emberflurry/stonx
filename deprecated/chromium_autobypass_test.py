#FAILED
from playwright.sync_api import sync_playwright
import time

# Optional: set path for persistent session data (saves cookies, login, etc.)
user_data_dir = "./my-profile"

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(user_data_dir=user_data_dir, headless=False)
    page = browser.new_page()
    page.goto("https://www.investing.com/equities/capstar-financial-holdings-inc-historical-data")

    # Step 1: Pause to let you log in manually
    print("\n🟡 Please log in manually in the opened browser.")
    print("✅ Press ENTER here once you've finished logging in...")
    input("type Y to continue")

    # Step 2: Continue with script (e.g., click date picker, set range, download CSV)
    print("⏩ Continuing automation...")

    # Example: wait a bit and then take screenshot of the state
    page.wait_for_timeout(3000)
    page.screenshot(path="loggedin_check.png")

    # TODO: Continue with clicking calendar, selecting dates, etc.
    print("📸 Screenshot saved as loggedin_check.png")
