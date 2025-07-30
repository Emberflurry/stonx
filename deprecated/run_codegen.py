#FAILED DNU

import subprocess
import sys
import os

# Manually build path to playwright CLI script
scripts_dir = os.path.expanduser(r"C:\\Users\\John DeForest\\AppData\\Roaming\\Python\\Python313\\Scripts")
playwright_path = os.path.join(scripts_dir, "playwright.cmd")

# Confirm the file exists
if not os.path.isfile(playwright_path):
    raise FileNotFoundError(f"Could not find playwright.cmd at {playwright_path}")

# Command to run codegen
cmd = [playwright_path, "codegen", "--user-data-dir=./my-profile", "https://www.investing.com"]

# Run it
subprocess.run(cmd, shell=True)
