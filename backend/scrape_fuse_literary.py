import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

EXCEL_FILE = r"E:\Internship\PocketFM\Fuse_Literary_Books.xlsx"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()
        print("Visiting Fuse Literary Romance Books page...")
        await page.goto('https://www.fuseliterary.com/our-books/?_book_genre=romance', wait_until='domcontentloaded', timeout=60000)
        
        # Wait a bit for initial load
        await page.wait_for_timeout(3000)
        
        # Click "Load More" until it's gone
        click_count = 0
        while True:
            try:
                # Try to find a load more button, either by class or text
                load_more_btn = page.locator(".wpgb-load-more").first
                
                if not await load_more_btn.is_visible():
                    # fallback to text search
                    load_more_btn = page.get_by_text("Load More", exact=False).first
                    
                if await load_more_btn.is_visible():
                    print(f"Clicking 'Load More' (Click #{click_count + 1})...")
                    await load_more_btn.click()
                    await page.wait_for_timeout(3000)  # Wait for new items to load
                    click_count += 1
                else:
                    print("No 'Load More' button visible. All books loaded.")
                    break
            except Exception as e:
                print("Finished loading all pages or encountered an error clicking:", e)
                break
                
        # Extract books
        print("Extracting book details...")
        books_data = await page.evaluate('''() => {
            let results = [];
            // Books are usually in a grid or list. Let's find all common containers.
            // A good generic approach is finding all image links, then grabbing the text near them.
            // Or looking for article tags, or divs with class containing 'book' or 'post'
            
            let items = Array.from(document.querySelectorAll('.fwpl-item, article, .book, .post, .fusion-post-grid'));
            
            // If none found with those classes, just grab all headings
            if (items.length === 0) {
                let headings = Array.from(document.querySelectorAll('h2, h3'));
                for (let h of headings) {
                    let title = h.innerText.trim();
                    if (!title) continue;
                    
                    let author = '';
                    let sibling = h.nextElementSibling;
                    if (sibling) {
                        author = sibling.innerText.trim();
                        // Sometimes author has "by " prefix
                        if (author.toLowerCase().startsWith('by ')) {
                            author = author.substring(3).trim();
                        }
                    }
                    results.push({title: title, author: author});
                }
                return results;
            }
            
            // If items found, extract from them
            for (let item of items) {
                let text = item.innerText.trim();
                if (!text) continue;
                
                let lines = text.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
                if (lines.length >= 1) {
                    let title = lines[0];
                    let author = lines.length > 1 ? lines[1] : '';
                    
                    if (author.toLowerCase().startsWith('by ')) {
                        author = author.substring(3).trim();
                    }
                    
                    results.push({title: title, author: author});
                }
            }
            return results;
        }''')
        
        # Deduplicate
        unique_books = []
        seen = set()
        for b in books_data:
            key = f"{b['title']}_{b['author']}"
            if key not in seen and b['title'].lower() != 'load more' and len(b['title']) > 2:
                seen.add(key)
                unique_books.append(b)
                
        print(f"Extracted {len(unique_books)} unique books.")
        
        # Save to Excel
        rows = []
        for b in unique_books:
            rows.append({
                "Name of Series": b['title'],
                "Author Name": b['author'],
                "Publisher": "Fuse Literary",
                "GoodReads series link": "",
                "Number of PRIMARY books in the series": "",
                "Rating (out of 5) of Primary Book 1": "",
                "Ratings (#) of Primary Book 1": "",
                "Synopsis (if available)": "",
                "Romantasy = Yes or No?": "",
                "Romantasy Sub-Genre of series": "",
                "Name of agent": ""
            })
            
        df = pd.DataFrame(rows)
        # Ensure 11 columns
        from merge_new_leaf import ELEVEN_COLUMN_HEADERS
        df = df.reindex(columns=ELEVEN_COLUMN_HEADERS)
        df.fillna("", inplace=True)
        
        print(f"Saving Excel to {EXCEL_FILE}...")
        df.to_excel(EXCEL_FILE, index=False)
        
        try:
            from apply_jra_style import apply_styling
            apply_styling(EXCEL_FILE)
            print("--- Applied styling ---")
        except Exception as e:
            print(f"Could not apply styling: {e}")
            
        await browser.close()
        
    print("Opening Excel file...")
    import subprocess
    subprocess.Popen(["start", EXCEL_FILE], shell=True)
    print("ALL DONE!")

if __name__ == '__main__':
    asyncio.run(main())
