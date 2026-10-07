import pandas as pd
from playwright.sync_api import sync_playwright
import time
import os

def main():
    excel_path = "e:/Internship/PocketFM/Internal Copy of US_Licensing_Lifecycle_Tracker  (1).xlsx"
    sheet_name = "Argus Show data"
    
    print(f"Loading Excel file: {excel_path}")
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    EMAIL = os.getenv("CMS_EMAIL")
    PASSWORD = os.getenv("CMS_PASSWORD")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        
        # Load saved authentication if it exists
        auth_file = "e:/Internship/PocketFM/scratch/auth.json"
        if os.path.exists(auth_file):
            context = browser.new_context(storage_state=auth_file)
            print("Loaded saved login session!")
        else:
            context = browser.new_context()
            
        page = context.new_page()
        
        print("\nOpening PocketFM CMS...")
        page.goto("https://cms.pocketfm.com/")
        
        if not os.path.exists(auth_file):
            print("\nAutomating SSO Login...")
            try:
                # 1. Click the initial login button on the PocketFM page
                print("Clicking the initial 'JumpCloud / Login' button...")
                login_button = page.locator('button:has-text("JumpCloud"), a:has-text("JumpCloud"), button:has-text("Login"), a:has-text("Login"), button:has-text("SSO")')
                if login_button.is_visible(timeout=5000):
                    login_button.first.click()
                
                # 2. Wait for JumpCloud to load
                page.wait_for_url("**/sso.jumpcloud.com/**", timeout=15000)
                
                # 3. Attempt to fill email
                print(f"Typing email: {EMAIL}")
                email_input = page.locator('input[type="email"], input[name="email"], input[name="username"], input[placeholder*="email" i]')
                email_input.first.wait_for(state="visible", timeout=10000)
                email_input.first.fill(EMAIL)
                
                # Some SSO flows require clicking 'Next' before password
                next_btn = page.locator('button:has-text("Next"), button:has-text("Continue")')
                if next_btn.is_visible():
                    next_btn.first.click()
                    page.wait_for_timeout(1000)
                
                # 4. Attempt to fill password
                print("Typing password...")
                pwd_input = page.locator('input[type="password"], input[name="password"]')
                pwd_input.first.wait_for(state="visible", timeout=5000)
                pwd_input.first.fill(PASSWORD)
                
                # 5. Click Login/Submit
                print("Clicking Log In...")
                page.locator('button[type="submit"], button:has-text("Log In"), button:has-text("Sign In"), a:has-text("Log In")').first.click()
                
            except Exception as e:
                print(f"\nCould not auto-fill fields perfectly: {e}")
                print("Please fill any remaining fields manually on the browser window.")
                
            print("\n" + "="*60)
            print(" ACTION REQUIRED: PLEASE ENTER AUTH CODE")
            print("="*60)
            input("The script has paused. Please enter your Auth Code in the browser.\nIMPORTANT: Wait until the dashboard is FULLY loaded and you stop seeing 'jumpcloud.com' redirects.\nOnce the dashboard is perfectly still, press ENTER here: ")
            
            # Wait a few seconds to ensure SSO redirects are completely finished
            time.sleep(3)
            
            # Save the session so you never have to log in again!
            context.storage_state(path=auth_file)
            print("Login session saved successfully! You won't have to log in next time.")

        
        # Grab the first valid Show ID from the sheet
        first_id = df['Show ID'].dropna().iloc[0]
        test_url = f"https://cms.pocketfm.com/shows/audiobooks?tab=published&id={first_id}"
        
        print(f"\nNavigating to the first show: {test_url}")
        
        # Try to navigate, handling any lingering SSO redirects
        try:
            page.goto(test_url, wait_until="domcontentloaded")
        except Exception as e:
            print("SSO interrupted us, trying one more time...")
            time.sleep(3)
            page.goto(test_url, wait_until="domcontentloaded")
        
        print("Waiting 10 seconds for the React dashboard to populate...")
        page.wait_for_timeout(10000) 
        
        # We save the HTML structure of the page
        html_content = page.content()
        os.makedirs("e:/Internship/PocketFM/scratch", exist_ok=True)
        dump_path = "e:/Internship/PocketFM/scratch/cms_sample.html"
        with open(dump_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print(f"\nSUCCESS! I have captured the page structure and saved it to {dump_path}.")
        print("You can close this terminal now. Tell Antigravity in the chat that the sample is ready!")
        
        browser.close()

if __name__ == "__main__":
    main()
