import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from bs4 import BeautifulSoup
import os

async def run_scraper():
    excel_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Standard_11_Column_Format_2.xlsx')
    
    print("Launching visible browser to bypass Cloudflare...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("Navigating to Bookouture Romance...")
        await page.goto("https://bookouture.com/books/?genre=romance")
        
        print("Waiting for Cloudflare and Javascript rendering to finish...")
        # Wait for the network to be idle so FacetWP/AJAX loads the books
        try:
            await page.wait_for_load_state("networkidle", timeout=60000)
        except Exception as e:
            print("Network idle timeout, proceeding...")

        # Specifically wait for book items (Bookouture uses .book-item, .product, or .facetwp-template)
        try:
            await page.wait_for_selector('.book, .product, .book-item, article.post, .facetwp-template article', timeout=30000)
            print("Books have loaded successfully.")
        except Exception as e:
            print("Could not find standard book container selectors. Will dump raw HTML.")

        print("Scrolling to load all books...")
        scroll_attempts = 0
        current_height = await page.evaluate("document.body.scrollHeight")
        
        while scroll_attempts < 100:
            # Click load more if it exists (FacetWP uses .facetwp-load-more)
            try:
                load_more = await page.query_selector(".facetwp-load-more, button:has-text('Load More'), a:has-text('Load More')")
                if load_more and await load_more.is_visible():
                    print("Clicking 'Load More' button...")
                    await load_more.click()
                    await asyncio.sleep(4)
                    continue
            except: pass
            
            # Scroll down
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            
            new_height = await page.evaluate("document.body.scrollHeight")
            if new_height == current_height:
                print("Reached the bottom.")
                break
            current_height = new_height
            scroll_attempts += 1

        print("Extraction phase...")
        books_data = []
        
        # We use Javascript evaluation directly in the browser to reliably get text
        # Bookouture books typically have a title in h2/h3 and author in a paragraph.
        # Let's extract all articles inside .facetwp-template
        
        elements = await page.query_selector_all(".facetwp-template article, .book, .product, .book-item, article.post")
        print(f"Found {len(elements)} book elements.")
        
        for el in elements:
            try:
                # Get the whole text
                text = await el.inner_text()
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                if not lines: continue
                
                # Title is usually the first non-empty line
                title = lines[0]
                
                # Author is usually "By <name>" or just the second line
                author = "Unknown"
                for line in lines[1:]:
                    if line.lower().startswith("by "):
                        author = line[3:].strip()
                        break
                    # If it's a name, we assume it's author
                    elif len(line) > 3 and "Read More" not in line and "Buy" not in line:
                        author = line
                        break
                
                books_data.append({"title": title, "author": author})
            except Exception as e:
                continue
                
        # Remove duplicates
        unique_books = []
        seen = set()
        for b in books_data:
            if b['title'] not in seen:
                seen.add(b['title'])
                unique_books.append(b)

        print(f"Extracted {len(unique_books)} unique books!")
        
        if len(unique_books) > 0:
            df = pd.read_excel(excel_path)
            new_rows = []
            for b in unique_books:
                new_rows.append({
                    'Name of Series': b['title'],
                    'Author Name': b['author'],
                    'Publisher': 'Bookouture',
                    'GoodReads series link': 'N/A',
                    'Number of PRIMARY books in the series': 'N/A',
                    'Rating (out of 5) of Primary Book 1': 'N/A',
                    'Ratings (#) of Primary Book 1': 'N/A',
                    'Synopsis (if available)': 'N/A',
                    'Romantasy = Yes or No?': 'N/A',
                    'Romantasy Sub-Genre of series': 'N/A',
                    'Name of agent': 'N/A'
                })
            df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
            df.to_excel(excel_path, index=False)
            print("Saved to Excel.")
        else:
            print("Failed to extract books. Check if the page loaded properly.")
            html = await page.content()
            with open("bookouture_romance.html", "w", encoding="utf-8") as f:
                f.write(html)
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())
