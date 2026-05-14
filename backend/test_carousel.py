import asyncio
import json
import os
import pandas as pd
import sys
from playwright.async_api import async_playwright
from goodreads_scraper import GoodreadsScraper

# Configuration
TEST_AUTHOR_URL = "https://sbrmedia.com/authors/bella-di-corte/"
TEST_AUTHOR_NAME = "Bella Di Corte"
OUTPUT_FILE = "SBR_Media_Test.xlsx"

async def scrape_author_with_carousel(page, author_name):
    print(f"[SBR Media] Navigating to {author_name} page...", flush=True)
    await page.goto(TEST_AUTHOR_URL, wait_until="networkidle", timeout=60000)
    
    # 1. Scroll to the carousel area
    print("  Scrolling to find carousel...", flush=True)
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
    await asyncio.sleep(2)
    
    # 2. Click the "Next" arrow repeatedly to reveal all books
    # SBR often uses Elementor sliders or similar. We'll look for common 'Next' selectors.
    print("  Interacting with carousel to reveal all books...", flush=True)
    
    # Try multiple common selectors for the 'Next' arrow
    next_selectors = [
        ".elementor-swiper-button-next", 
        ".slick-next", 
        ".owl-next", 
        "i.fa-chevron-right", 
        "i.fa-angle-right",
        ".next.column-arrow"
    ]
    
    all_titles = set()
    
    # Initial capture
    current_titles = await get_visible_titles(page)
    all_titles.update(current_titles)
    
    # Click loop
    for attempt in range(10): # Maximum 10 clicks to prevent infinite loops
        clicked = False
        for selector in next_selectors:
            button = await page.query_selector(selector)
            if button and await button.is_visible():
                print(f"    Clicking 'Next' arrow ({selector})...", flush=True)
                await button.click()
                await asyncio.sleep(1.5) # Wait for slide transition
                clicked = True
                break
        
        if not clicked:
            print("    No more 'Next' arrows visible or reachable.", flush=True)
            break
            
        # Capture newly revealed titles
        new_titles = await get_visible_titles(page)
        all_titles.update(new_titles)
    
    print(f"  [Scrape Complete] Found {len(all_titles)} unique titles for {author_name}.", flush=True)
    return list(all_titles)

async def get_visible_titles(page):
    """Internal helper to grab image alts from the carousel area."""
    return await page.evaluate("""() => {
        const results = [];
        const images = document.querySelectorAll('img');
        images.forEach(img => {
            let alt = img.alt || '';
            // Filter out fluff
            if (alt.length > 3 && 
                !alt.includes('SBR') && 
                !alt.includes('Agent') && 
                !alt.includes('Designed') &&
                !alt.toLowerCase().includes('logo') &&
                !alt.toLowerCase().includes('literary') &&
                !alt.toLowerCase().includes('agency') &&
                !alt.toLowerCase().includes('placeholder')) {
                
                let clean = alt.split(' - ')[0].split(' – ')[0].trim();
                if (clean.length > 3 && !clean.toLowerCase().startsWith('image_')) {
                    results.push(clean);
                }
            }
        });
        return results;
    }""")

async def run_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) # Visible for testing
        context = await browser.new_context()
        page = await context.new_page()
        
        gr_scraper = GoodreadsScraper(headless=False)
        
        # 1. Scrape SBR Media with carousel interaction
        book_titles = await scrape_author_with_carousel(page, TEST_AUTHOR_NAME)
        
        # 2. Enrich via Goodreads
        print(f"\n[Goodreads] Processing {len(book_titles)} books...", flush=True)
        results = []
        for title in book_titles:
            print(f"  Searching: {title}...", flush=True)
            try:
                gr_data = await gr_scraper.scrape_goodreads_data(context, title, TEST_AUTHOR_NAME)
                if gr_data:
                    results.append({
                        'Name of Series': gr_data.get('Book_Title', title),
                        'Author Name': TEST_AUTHOR_NAME,
                        'Publisher': 'SBR Media',
                        'GoodReads series link': gr_data.get('GoodReads_Series_URL', 'N/A'),
                        'Rating (out of 5)': gr_data.get('Book1_Rating', 'N/A'),
                        'Synopsis': gr_data.get('Description', 'N/A')
                    })
            except Exception as e:
                print(f"    Error: {e}")
        
        # 3. Save to Test File
        if results:
            df = pd.DataFrame(results)
            df.to_excel(OUTPUT_FILE, index=False)
            print(f"\nTest Complete! Results saved to {OUTPUT_FILE}")
            os.startfile(OUTPUT_FILE)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
