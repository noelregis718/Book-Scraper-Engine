import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright
from goodreads_scraper import GoodreadsScraper
from excel_utility import save_jabberwocky_excel

# Unicode Shield: Force UTF-8 for Windows Console to prevent crashes
try:
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
except AttributeError: pass

# --- CONFIGURATION ---
INPUT_FILE = r"E:\Internship\PocketFM\awful agents.xlsx"
HEADLESS = False  # User wants to see it

async def repair_mission():
    print(f"Starting Metadata Repair Mission for {os.path.basename(INPUT_FILE)}...")
    
    if not os.path.exists(INPUT_FILE):
        print("Error: File not found.")
        return

    df = pd.read_excel(INPUT_FILE)
    
    # Identify missing rows
    mask = df["GoodReads series link"].astype(str).str.lower().isin(["nan", "n/a", "", "none"])
    to_repair = df[mask]
    total_to_repair = len(to_repair)
    
    if total_to_repair == 0:
        print("No missing links found. Mission complete!")
        return
        
    print(f"Found {total_to_repair} titles missing Goodreads links. Starting Tech-Sync repair...")

    gr_scraper = GoodreadsScraper(headless=HEADLESS)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        context = await browser.new_context()
        # Login Gate (Amazon-Style Pattern)
        login_page = await context.new_page()
        print("[Goodreads] Navigating to sign-in page...")
        await login_page.goto("https://www.goodreads.com/user/sign_in", wait_until="domcontentloaded")
        
        try:
            # Handle "Sign in with email" if needed
            email_btn = login_page.locator('a:has-text("Sign in with email")')
            if await email_btn.is_visible():
                await email_btn.click()
                await login_page.wait_for_load_state("networkidle")
            
            # Fill credentials (from .env/stored)
            if await login_page.locator("#ap_email").is_visible():
                await login_page.fill("#ap_email", "noel.regis04@gmail.com")
                await login_page.fill("#ap_password", "Noel@1024")
                await login_page.click("#signInSubmit")
                print("  [Auto-Login] Credentials submitted. Waiting for manual approval...")
        except Exception as e:
            print(f"  [Auto-Login] Step skipped: {e}")

        # Detection Loop (Fast-Response: 15 seconds)
        print("\n[ACTION REQUIRED] Solve CAPTCHA if shown. Searching will start in 15 seconds...\n")
        login_selectors = ['a[href*="sign_out"]', '.Header_userProfile', '.headerPersonalNav', '[data-testid="notificationsIcon"]', 'a[href="/"]']
        logged_in = False
        for _ in range(15):
            for sel in login_selectors:
                try:
                    if await login_page.locator(sel).is_visible():
                        logged_in = True
                        break
                except: pass
            if logged_in: break
            await asyncio.sleep(1)
            
        if logged_in:
            print("  [OK] Login detected! Starting Turbo-Repair mission...")
        else:
            print("  [Notice] Continuing to repair phase. (Login may still be completing in background)")

        # Parallel Repair: TURBO BATCH MODE (10 Tabs at a go)
        total_to_repair = len(to_repair)
        
        REPAIR_BATCH_SIZE = 10
        rows_to_process = list(to_repair.iterrows())
        
        for i in range(0, len(rows_to_process), REPAIR_BATCH_SIZE):
            batch = rows_to_process[i:i+REPAIR_BATCH_SIZE]
            tasks = []
            
            for index, row in batch:
                title = row["Name of Series"]
                author = row["Author Name"]
                print(f"[{i + len(tasks) + 1}/{total_to_repair}] Repairing: {title} by {author}...")
                tasks.append(gr_scraper.scrape_goodreads_data(context, title, author))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # In-Place Update: Find the exact row index and update it
            for (index, row), gr_data in zip(batch, results):
                if isinstance(gr_data, Exception) or not gr_data:
                    print(f"  -> FAILED: {row['Name of Series']}")
                    continue
                    
                # Update the main DataFrame at the specific index
                gr_url = gr_data.get("GoodReads_Series_URL", "N/A")
                if gr_url == "N/A":
                    gr_url = gr_data.get("GoodReads_Book_URL", "N/A")
                    
                df.at[index, "GoodReads series link"] = str(gr_url)
                df.at[index, "Rating (out of 5) of Primary Book 1"] = str(gr_data.get("Book1_Rating", "N/A"))
                df.at[index, "Ratings (#) of Primary Book 1"] = str(gr_data.get("Book1_Num_Ratings", "N/A"))
                df.at[index, "Synopsis (if available)"] = str(gr_data.get("Description", "N/A"))
                df.at[index, "Number of PRIMARY books in the series"] = str(gr_data.get("Num_Primary_Books", "1"))
                
                # Update series name if it was 'Unknown'
                if str(df.at[index, "Name of Series"]).lower() == "unknown":
                    df.at[index, "Name of Series"] = str(gr_data.get("Book_Title", row["Name of Series"]))
                
                if str(df.at[index, "Author Name"]).lower() == "unknown" and gr_data.get("Author_Found"):
                    df.at[index, "Author Name"] = gr_data["Author_Found"]
                
                print(f"  -> SUCCESS: Recovered {row['Name of Series']}")

            # Professional Save: Update the whole file in-place with formatting
            save_jabberwocky_excel(df.to_dict('records'), INPUT_FILE)
            print(f"  [System] In-Place Checkpoint saved. Progress: {i + len(batch)}/{total_to_repair}")

        print(f"Repair Mission Complete! All recovered data saved.")
        await browser.close()
        
        # Auto-open the file for user review
        if os.path.exists(INPUT_FILE):
            os.startfile(INPUT_FILE)

if __name__ == "__main__":
    asyncio.run(repair_mission())
