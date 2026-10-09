import pandas as pd
import re
import os
import time
from playwright.sync_api import sync_playwright

def run_scraper():
    metrics_file = 'e:/Internship/PocketFM/GenAI_Metrics.xlsx'
    download_folder = 'e:/Internship/PocketFM/Final_Upload_Docs'
    
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    df = pd.read_excel(metrics_file)
    
    with sync_playwright() as p:
        # Launch Chrome with a persistent profile so you stay logged in!
        browser = p.chromium.launch_persistent_context(
            user_data_dir='e:/Internship/PocketFM/browser_profile_master',
            headless=False,
            accept_downloads=True,
            args=["--start-maximized"]
        )
        page = browser.new_page()
        
        print("Opening Google Drive...")
        page.goto('https://drive.google.com')
        print("=========================================================")
        print("ACTION REQUIRED: Please ensure you are logged into Google")
        print("using your office email: ext-noel.regis@pocketfm.com")
        print("You have 30 seconds to sign in if you aren't already...")
        print("=========================================================")
        time.sleep(30)
        
        downloaded_count = 0
        
        for idx, row in df.iterrows():
            link = str(row['Drive Link'])
            title = str(row['Show / Title'])
            
            if 'http' not in link: 
                continue
                
            print(f"\n[{idx+1}/{len(df)}] Processing: {title}")
            
            doc_id_match = re.search(r'/document/d/([a-zA-Z0-9_-]+)', link)
            file_id_match = re.search(r'/file/d/([a-zA-Z0-9_-]+)', link)
            folder_id_match = re.search(r'/(?:folders|drive/folders)/([a-zA-Z0-9_-]+)', link)
            
            download_url = None
            file_id = None
            
            if doc_id_match:
                file_id = doc_id_match.group(1)
                download_url = f"https://docs.google.com/document/d/{file_id}/export?format=docx"
            elif file_id_match:
                file_id = file_id_match.group(1)
                download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            elif folder_id_match:
                print(f"Navigating to folder to locate file ID...")
                try:
                    page.goto(link, wait_until='networkidle')
                    time.sleep(4) # Wait for Drive UI to fully render
                    
                    # Extract the ID of the first file inside the folder
                    first_file = page.locator('div[data-id]').nth(1)
                    if first_file.is_visible():
                        file_id = first_file.get_attribute('data-id')
                        download_url = f"https://docs.google.com/document/d/{file_id}/export?format=docx"
                    else:
                        print("Could not find a file inside this folder.")
                except Exception as e:
                    print(f"Error reading folder: {e}")
            
            if download_url:
                try:
                    save_path = os.path.join(download_folder, f"{title.replace('/', '_')}.docx")
                    
                    # Skip if we already downloaded it
                    if os.path.exists(save_path):
                        print("Already exists. Skipping.")
                        continue
                        
                    print("Initiating download...")
                    with page.expect_download(timeout=15000) as download_info:
                        page.evaluate(f"window.location.href = '{download_url}'")
                        
                    download = download_info.value
                    download.save_as(save_path)
                    print(f"SUCCESS: Saved to {save_path}")
                    downloaded_count += 1
                    time.sleep(2) # Brief pause between downloads to avoid rate limits
                    
                except Exception as e:
                    print(f"FAILED to download {title}. Might require different permissions. Error: {e}")
            else:
                print("Could not generate a valid download URL.")
                
        print(f"\nFinished! Successfully downloaded {downloaded_count} new files via the scraper.")
        browser.close()

if __name__ == "__main__":
    run_scraper()
