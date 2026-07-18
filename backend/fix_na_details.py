import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright
import re
import json

def clean_text(text):
    if not text: return ""
    text = re.sub(r'\s+', ' ', text).strip()
    return text

async def process_missing_row(index, row, df, context, excel_path, lock):
    book_url = str(row.get("Book goodreads link", "")).strip()
    if not book_url or not book_url.startswith('http'):
        return

    # Check if this row actually needs fixing
    rating = str(row.get("Rating (out of 5) of Primary Book 1", "")).strip()
    synopsis = str(row.get("Synopsis (if available)", "")).strip()
    
    needs_rating = (rating == 'N/A' or rating == 'nan' or rating == '')
    needs_synopsis = (synopsis == 'N/A' or synopsis == 'nan' or synopsis == '')
    
    if not needs_rating and not needs_synopsis:
        return

    print(f"[{index+1}] Fixing missing data for Book URL: {book_url}", flush=True)
    page = await context.new_page()
    try:
        await page.goto(book_url, wait_until="domcontentloaded", timeout=90000)
        await asyncio.sleep(2)
        
        avg_rating = "N/A"
        rating_count = "N/A"
        
        # 1. Try JSON-LD first
        try:
            ld_el = await page.query_selector('script[type="application/ld+json"]')
            if ld_el:
                ld_data = json.loads(await ld_el.inner_text())
                if isinstance(ld_data, list): ld_data = ld_data[0]
                avg_rating = str(ld_data.get('aggregateRating', {}).get('ratingValue', 'N/A'))
                rating_count = str(ld_data.get('aggregateRating', {}).get('ratingCount', 'N/A'))
        except: pass
        
        # 2. Try DOM Fallback for Rating
        if avg_rating == "N/A":
            rating_el = await page.query_selector('.RatingStatistics__rating')
            if rating_el:
                avg_rating = clean_text(await rating_el.inner_text())
                
        # 3. Try DOM Fallback for Rating Count
        if rating_count == "N/A":
            count_el = await page.query_selector('[data-testid="ratingsCount"]')
            if count_el:
                r_text = clean_text(await count_el.inner_text())
                r_match = re.search(r'([\d,]+)\s*ratings', r_text, re.IGNORECASE)
                if r_match:
                    rating_count = r_match.group(1).replace(',', '')

        description = "N/A"
        # Try different description selectors
        desc_el = await page.query_selector('[data-testid="description"] .Formatted, .readable, #description')
        if desc_el:
            # Click "Show more" if present to expand full description
            try:
                more_btn = await desc_el.query_selector('text="Show more"')
                if more_btn:
                    await more_btn.click()
                    await asyncio.sleep(0.5)
            except: pass
            description = clean_text(await desc_el.inner_text())

        async with lock:
            if needs_rating and avg_rating != "N/A":
                df.at[index, "Rating (out of 5) of Primary Book 1"] = avg_rating
                df.at[index, "Ratings (#) of Primary Book 1"] = rating_count
                
            if needs_synopsis and description != "N/A":
                df.at[index, "Synopsis (if available)"] = description
                
            df.to_excel(excel_path, index=False)
            
        print(f"  [{index+1}] Fixed! Rating: {avg_rating}, Count: {rating_count}, Synopsis length: {len(description)} chars.", flush=True)

    except Exception as e:
        print(f"  [{index+1}] Error: {e}", flush=True)
    finally:
        await page.close()

async def run_fixer():
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_path = os.path.join(workspace_dir, "Selected_Titles_Blank_Template.xlsx")
    
    df = pd.read_excel(input_path)
    
    lock = asyncio.Lock()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        tasks = []
        for index, row in df.iterrows():
            tasks.append(process_missing_row(index, row, df, context, input_path, lock))
            
        print(f"\nStarting fix for missing details...", flush=True)
        await asyncio.gather(*tasks)
        await browser.close()
        
    try:
        from apply_premium_style_crime import apply_premium_fixed_style
        apply_premium_fixed_style(input_path)
    except: pass
    print("Done fixing missing details.")

if __name__ == "__main__":
    asyncio.run(run_fixer())
