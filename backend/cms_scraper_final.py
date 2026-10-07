import pandas as pd
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re
import time
import os
from dotenv import load_dotenv

def extract_metrics(html):
    soup = BeautifulSoup(html, 'html.parser')
    metrics = {
        'Show Name': '',
        'Plays ': '',
        'Durations': '',
        'Ratings': '',
        'Reviews': '',
        'Comments': ''
    }
    
    title_tag = soup.find('p', class_='sc-imWYAI')
    if title_tag: 
        metrics['Show Name'] = title_tag.get_text(strip=True)

    def get_metric(label_regex):
        label_divs = soup.find_all('div', string=re.compile(label_regex))
        for div in label_divs:
            # We check for the specific CSS class used for dashboard stat labels
            if 'sc-fmNzgT' in div.get('class', []):
                if div.parent:
                    val_div = div.parent.find('div')
                    if val_div: 
                        return val_div.get_text(strip=True), div.get_text(strip=True)
        return '', ''

    plays, _ = get_metric('Plays')
    metrics['Plays '] = plays

    durations, _ = get_metric('Hours')
    metrics['Durations'] = durations

    comments, _ = get_metric('Comments')
    metrics['Comments'] = comments

    ratings, reviews_label = get_metric('Reviews')
    metrics['Ratings'] = ratings
    metrics['Reviews'] = reviews_label.replace('Reviews', '').strip()

    return metrics


def main():
    load_dotenv()
    EMAIL = os.getenv("CMS_EMAIL")
    PASSWORD = os.getenv("CMS_PASSWORD")

    excel_path = "e:/Internship/PocketFM/Internal Copy of US_Licensing_Lifecycle_Tracker .xlsx"
    sheet_name = "Argus Show data - Noels Automat"
    
    print(f"Loading Excel file: {excel_path}")
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    
    auth_file = "e:/Internship/PocketFM/scratch/auth.json"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        
        if os.path.exists(auth_file):
            context = browser.new_context(storage_state=auth_file)
            print("Loaded saved login session!")
        else:
            context = browser.new_context()
            
        page = context.new_page()
        
        if not os.path.exists(auth_file):
            print("\nOpening PocketFM CMS...")
            page.goto("https://cms.pocketfm.com/")
            print("\nAutomating SSO Login...")
            try:
                login_button = page.locator('button:has-text("JumpCloud"), a:has-text("JumpCloud"), button:has-text("Login"), a:has-text("Login"), button:has-text("SSO")')
                if login_button.is_visible(timeout=5000):
                    login_button.first.click()
                
                page.wait_for_url("**/sso.jumpcloud.com/**", timeout=15000)
                
                email_input = page.locator('input[type="email"], input[name="email"], input[name="username"], input[placeholder*="email" i]')
                email_input.first.wait_for(state="visible", timeout=10000)
                email_input.first.fill(EMAIL)
                
                next_btn = page.locator('button:has-text("Next"), button:has-text("Continue")')
                if next_btn.is_visible():
                    next_btn.first.click()
                    page.wait_for_timeout(1000)
                
                pwd_input = page.locator('input[type="password"], input[name="password"]')
                pwd_input.first.wait_for(state="visible", timeout=5000)
                pwd_input.first.fill(PASSWORD)
                
                page.locator('button[type="submit"], button:has-text("Log In"), button:has-text("Sign In"), a:has-text("Log In")').first.click()
                
            except Exception as e:
                print(f"\nCould not auto-fill fields perfectly: {e}")
                
            print("\n" + "="*60)
            print(" ACTION REQUIRED: PLEASE ENTER AUTH CODE")
            print("="*60)
            input("The script has paused. Please enter your Auth Code in the browser.\nIMPORTANT: Wait until the dashboard is FULLY loaded and you stop seeing 'jumpcloud.com' redirects.\nOnce the dashboard is perfectly still, press ENTER here: ")
            
            time.sleep(3)
            context.storage_state(path=auth_file)
            print("Login session saved successfully! You won't have to log in next time.")
            
        print("\n" + "="*60)
        print(" STARTING THE SCRAPER LOOP")
        print("="*60)
        
        for index, row in df.iterrows():
            show_id = str(row['Show ID']).strip()
            if not show_id or show_id == 'nan':
                continue
                
            url = f"https://cms.pocketfm.com/shows/audiobooks?tab=published&id={show_id}"
            print(f"\nScraping Show ID: {show_id}")
            
            try:
                page.goto(url, wait_until="domcontentloaded")
                
                # Wait for at least one metric to be visible on the screen to confirm React finished loading
                page.locator('div.sc-fmNzgT:has-text("Plays")').first.wait_for(state="visible", timeout=15000)
                time.sleep(1) # Extra buffer for ratings to fetch
                
                html = page.content()
                metrics = extract_metrics(html)
                
                print(f"--> Found Name: {metrics['Show Name']}")
                print(f"--> Plays: {metrics['Plays ']} | Duration: {metrics['Durations']} | Ratings: {metrics['Ratings']} | Reviews: {metrics['Reviews']} | Comments: {metrics['Comments']}")
                
                # Update dataframe (cast to float if needed later, but strings are safer for formatting like 13.1K)
                df.at[index, 'Show Name'] = metrics['Show Name']
                df.at[index, 'Plays '] = metrics['Plays ']
                df.at[index, 'Durations'] = metrics['Durations']
                df.at[index, 'Ratings'] = metrics['Ratings']
                df.at[index, 'Reviews'] = metrics['Reviews']
                df.at[index, 'Comments'] = metrics['Comments']
                
            except Exception as e:
                print(f"--> Timeout or error loading {show_id} (It might be invalid or deleted)")
                
        print("\n" + "="*60)
        print("FINISHED SCRAPING! Saving all data back to the Excel file...")
        df.to_excel(excel_path, sheet_name=sheet_name, index=False)
        print(f"SUCCESS! {excel_path} has been updated!")
        
        browser.close()

if __name__ == "__main__":
    main()
