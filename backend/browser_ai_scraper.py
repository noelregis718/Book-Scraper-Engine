import asyncio
import pandas as pd
import os
import json
import re
import sys
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from apply_jra_style import apply_styling

async def init_chat(page):
    print("Navigating to DDG Chat...")
    await page.goto("https://duckduckgo.com/chat", wait_until="networkidle")
    
    # Click "Get Started"
    try:
        await page.click("text='Get Started'", timeout=3000)
        print("Clicked Get Started")
    except:
        pass
        
    # Click "I Agree"
    try:
        await page.click("text='I Agree'", timeout=3000)
        print("Clicked I Agree")
    except:
        pass
        
    print("Waiting for chat input...")
    await page.wait_for_selector("textarea", timeout=10000)
    print("Chat interface ready.")

def extract_json(text):
    # Try to find JSON within markdown blocks or raw text
    try:
        match = re.search(r'\{[^{}]*\}', text)
        if match:
            return json.loads(match.group(0))
    except:
        pass
    return None

async def run_scraper():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tracker_path = os.path.join(base_dir, 'Publishers_Tracker.xlsx')
    
    print("Loading Publishers_Tracker.xlsx...")
    df = pd.read_excel(tracker_path)
    
    rev_col = 'Revenue of these publishing houses'
    year_col = 'Year of establishment of these'
    
    # Find rows that need scraping (Revenue is blank/NaN)
    # Exclude those that are already "N/A" or filled
    indices_to_scrape = []
    for idx, row in df.iterrows():
        val = str(row.get(rev_col, '')).strip()
        if val == '' or val.lower() == 'nan':
            indices_to_scrape.append(idx)
            
    print(f"Found {len(indices_to_scrape)} publishers needing AI research.")
    
    if not indices_to_scrape:
        print("No publishers left to scrape!")
        return

    async with async_playwright() as p:
        # Headless=False so the user can see the automation working
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            for idx in indices_to_scrape:
                pub_name = str(df.at[idx, 'Publisher Name'])
                safe_pub_name = pub_name.encode('utf-8', 'replace').decode('utf-8')
                print(f"[{idx}] Researching: {safe_pub_name}")
                
                # Refresh page for every row to clear rate limit and disabled textarea
                await init_chat(page)
                
                prompt = (f"Research the publishing house '{pub_name}'. "
                          "What is their estimated Annual Revenue and Year Established? "
                          "Reply ONLY with a JSON object exactly in this format: {\"revenue\": \"<insert amount or Unknown>\", \"year\": \"<insert year or Unknown>\"}")
                          
                input_selector = "textarea"
                await page.fill(input_selector, prompt)
                await page.press(input_selector, "Enter")
                
                # Wait for response 
                print("Waiting 10 seconds for AI response...")
                await page.wait_for_timeout(10000) 
                
                # Try to get the text of the page and extract JSON globally
                page_text = await page.inner_text("body")
                safe_text = page_text.encode('utf-8', 'replace').decode('utf-8')
                
                # The response is usually the last JSON looking block on the page
                data = extract_json(safe_text)
                if data:
                    rev = data.get('revenue', 'Unknown')
                    yr = data.get('year', 'Unknown')
                    df.at[idx, rev_col] = rev
                    df.at[idx, year_col] = yr
                    print(f"Extracted -> Revenue: {rev}, Year: {yr}")
                else:
                    print("Failed to parse JSON.")
                    df.at[idx, rev_col] = "AI Error"
                    df.at[idx, year_col] = "AI Error"
                    
                # Save after each to be safe
                df.to_excel(tracker_path, index=False)
                
        except Exception as e:
            print("Error during scraping:", e)
        finally:
            await browser.close()
            
    # Apply styling at the end
    try:
        apply_styling(tracker_path)
        print("Styling applied.")
    except Exception as e:
        print("Styling error:", e)

if __name__ == "__main__":
    asyncio.run(run_scraper())
