import subprocess
import time
import urllib.request
import json
import os

CHROME_PATH = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
USER_DATA = r"E:\Internship\PocketFM\backend\chrome_live_profile"
TARGET_URL = "https://www.kensingtonbooks.com/shop/product-category/fiction/fantasy-fiction/"

print("Testing Native Chrome + Remote Debugging Port...")

cmd = [
    CHROME_PATH,
    f"--remote-debugging-port=9222",
    f"--user-data-dir={USER_DATA}",
    "--no-first-run",
    "--no-default-browser-check",
    TARGET_URL
]

proc = subprocess.Popen(cmd)
print(f"Chrome launched with PID: {proc.pid}")

time.sleep(5)

try:
    with urllib.request.urlopen("http://127.0.0.1:9222/json", timeout=5) as resp:
        tabs = json.loads(resp.read().decode())
        print(f"Tabs open in Chrome ({len(tabs)}):")
        for t in tabs:
            print(f"  - Title: {t.get('title')} | URL: {t.get('url')}")
except Exception as e:
    print(f"CDP connection error: {e}")

# Kill test process
proc.terminate()
print("Test completed.")

