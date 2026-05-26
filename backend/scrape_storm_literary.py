import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

EXCEL_FILE = r"E:\Internship\PocketFM\storm_literary_agency_scraped.xlsx"
BASE_URL = "https://www.stormliteraryagency.com"
MAX_CONCURRENT = 5

ELEVEN_COLUMN_HEADERS = [
    "Name of Series",
    "Author Name",
    "Publisher",
    "GoodReads series link",
    "Number of PRIMARY books in the series",
    "Rating (out of 5) of Primary Book 1",
    "Ratings (#) of Primary Book 1",
    "Synopsis (if available)",
    "Romantasy = Yes or No?",
    "Romantasy Sub-Genre of series",
    "Name of agent",
]

async def scrape_author_page(context, author_name, author_url, semaphore):
    async with semaphore:
        page = await context.new_page()
        books = []
        try:
            print(f"  [Scraping Author] {author_name} -> {author_url}")
            await page.goto(author_url, wait_until="domcontentloaded", timeout=45000)
            
            # Extract italics elements (em, i tags)
            raw_books = await page.evaluate('''() => {
                let tags = document.querySelectorAll('em, i');
                return Array.from(tags).map(t => t.innerText.trim());
            }''')
            
            # Clean up raw books
            for b in raw_books:
                # Remove empty strings, standalone numbers, trailing punctuation
                cleaned = str(b).strip(',. ')
                if len(cleaned) > 2 and not cleaned.isdigit():
                    if cleaned not in books:
                        books.append(cleaned)
                        
            print(f"  [Found {len(books)} Books] for {author_name}")
            
        except Exception as e:
            print(f"  [Error] Failed to scrape {author_name}: {e}")
        finally:
            await page.close()
            
        rows = []
        if not books:
            # Add an empty row for the author
            rows.append({
                "Name of Series": "",
                "Author Name": author_name,
                "Publisher": "Storm Literary Agency",
                "GoodReads series link": "",
                "Number of PRIMARY books in the series": "",
                "Rating (out of 5) of Primary Book 1": "",
                "Ratings (#) of Primary Book 1": "",
                "Synopsis (if available)": "",
                "Romantasy = Yes or No?": "",
                "Romantasy Sub-Genre of series": "",
                "Name of agent": "",
            })
        else:
            for book in books:
                rows.append({
                    "Name of Series": book,
                    "Author Name": author_name,
                    "Publisher": "Storm Literary Agency",
                    "GoodReads series link": "",
                    "Number of PRIMARY books in the series": "",
                    "Rating (out of 5) of Primary Book 1": "",
                    "Ratings (#) of Primary Book 1": "",
                    "Synopsis (if available)": "",
                    "Romantasy = Yes or No?": "",
                    "Romantasy Sub-Genre of series": "",
                    "Name of agent": "",
                })
        
        return rows


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()
        print("Visiting Authors page...")
        await page.goto(f"{BASE_URL}/authors.html", wait_until="domcontentloaded", timeout=45000)
        
        # We know authors are in div with font-size:90% and previous a href
        authors_raw = await page.evaluate('''() => {
            let divs = document.querySelectorAll('div');
            let results = [];
            for (let div of divs) {
                if ((div.getAttribute('style') || '').includes('font-size:90%') || (div.getAttribute('style') || '').includes('font-size: 90%')) {
                    let name = div.innerText.trim();
                    if (name) {
                        let a_tag = div.previousElementSibling;
                        while(a_tag && a_tag.tagName !== 'A') {
                            a_tag = a_tag.previousElementSibling;
                        }
                        // Or if a tag wraps the div, search parent
                        if (!a_tag && div.parentElement && div.parentElement.tagName === 'A') {
                            a_tag = div.parentElement;
                        }
                        
                        let href = "";
                        if (a_tag) {
                            href = a_tag.href;
                        } else {
                            // Try finding any a tag nearby
                            let container = div.parentElement;
                            if (container) {
                                let local_a = container.querySelector('a');
                                if (local_a) href = local_a.href;
                            }
                        }
                        results.push({name: name, href: href});
                    }
                }
            }
            return results;
        }''')
        
        # Deduplicate and filter
        author_dict = {}
        for a in authors_raw:
            name = a['name']
            href = a['href']
            # Only keep valid hrefs that are part of storm literary and not empty
            if href and 'stormliteraryagency.com' in href and not href.endswith('authors.html'):
                if name not in author_dict:
                    author_dict[name] = href
                    
        print(f"Extracted {len(author_dict)} unique authors.")
        await page.close()
        
        if not author_dict:
            print("Failed to find authors.")
            await browser.close()
            return
            
        print("--- Scraping individual author profiles ---")
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        tasks = []
        
        for author_name, author_url in author_dict.items():
            tasks.append(scrape_author_page(context, author_name, author_url, semaphore))
            
        results = await asyncio.gather(*tasks)
        
        all_rows = []
        for res in results:
            all_rows.extend(res)
            
        df = pd.DataFrame(all_rows)
        # Reorder/ensure all 11 columns
        df = df.reindex(columns=ELEVEN_COLUMN_HEADERS)
        
        # Clean any remaining nans
        df.fillna("", inplace=True)
        
        print("--- Saving Excel ---")
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
