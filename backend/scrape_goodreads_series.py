import asyncio
import pandas as pd
import os
import json
import re
import sys
from playwright.async_api import async_playwright

async def init_chat(page):
    print("Navigating to DDG Chat...")
    await page.goto("https://duckduckgo.com/chat", wait_until="networkidle")
    
    # Click "Get Started"
    try:
        await page.click("text='Get Started'", timeout=3000)
    except:
        pass
        
    # Click "I Agree"
    try:
        await page.click("text='I Agree'", timeout=3000)
    except:
        pass
        
    await page.wait_for_selector("textarea", timeout=10000)
    print("Chat interface ready.")

def extract_json(text):
    try:
        match = re.search(r'\{[^{}]*\}', text)
        if match:
            return json.loads(match.group(0))
    except:
        pass
    return None

async def run_scraper():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_path = os.path.join(base_dir, 'CT_Series_Base_Part_5_of_6.xlsx')
    
    print(f"Loading {target_path}...")
    df = pd.read_excel(target_path)
    
    col_url = 'GoodReads_Series_URL'
    col_num_books = 'Num_Primary_Books'
    col_pages = 'Total_Pages_Primary_Books'
    col_b1_rate = 'Book1_Rating'
    col_b1_num = 'Book1_Num_Ratings'
    
    # Ensure columns exist (and cast them to object so we can put anything)
    for c in [col_url, col_num_books, col_pages, col_b1_rate, col_b1_num]:
        if c not in df.columns:
            df[c] = ''
        df[c] = df[c].astype(object)
    
    indices_to_scrape = []
    for idx, row in df.iterrows():
        val = str(row.get(col_url, '')).strip()
        if val == '' or val.lower() == 'nan':
            indices_to_scrape.append(idx)
            
    print(f"Found {len(indices_to_scrape)} series needing Goodreads AI research.")
    
    if not indices_to_scrape:
        print("No rows left to scrape!")
        return

    # TEST LIMIT FOR VERIFICATION
    TEST_LIMIT = 3
    test_indices = indices_to_scrape[:TEST_LIMIT]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            for idx in test_indices:
                series_name = str(df.at[idx, 'Series Name'])
                author_name = str(df.at[idx, 'Author Name'])
                print(f"[{idx}] Researching Series: {series_name} by {author_name}")
                
                await init_chat(page)
                
                prompt = (f"Research the book series '{series_name}' by '{author_name}' on Goodreads. "
                          "Provide the Goodreads Series URL, Number of Primary Books, total number of pages across primary books (estimate if needed), Book 1 Rating, and Book 1 Number of Ratings. "
                          "Reply ONLY with a JSON object using the exact keys below, but replace the values with the actual real data you found (use 'Unknown' if you cannot find a value): "
                          "{\"url\": \"https://www.goodreads.com/series/12345\", \"num_books\": 5, \"pages\": 1500, \"b1_rating\": 4.2, \"b1_num_ratings\": 1000}")
                          
                input_selector = "textarea"
                await page.fill(input_selector, prompt)
                await page.press(input_selector, "Enter")
                
                print("Waiting 12 seconds for AI response...")
                await page.wait_for_timeout(12000) 
                
                page_text = await page.inner_text("body")
                safe_text = page_text.encode('utf-8', 'replace').decode('utf-8')
                
                data = extract_json(safe_text)
                if data:
                    df.at[idx, col_url] = data.get('url', 'Unknown')
                    df.at[idx, col_num_books] = data.get('num_books', 'Unknown')
                    df.at[idx, col_pages] = data.get('pages', 'Unknown')
                    df.at[idx, col_b1_rate] = data.get('b1_rating', 'Unknown')
                    df.at[idx, col_b1_num] = data.get('b1_num_ratings', 'Unknown')
                    print(f"Extracted -> {data}")
                else:
                    print("Failed to parse JSON.")
                    df.at[idx, col_url] = "AI Error"
                    
                df.to_excel(target_path, index=False)
                
        except Exception as e:
            print("Error during scraping:", e)
        finally:
            await browser.close()
            
if __name__ == "__main__":
    asyncio.run(run_scraper())
