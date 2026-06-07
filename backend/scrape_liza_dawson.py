import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

EXCEL_FILE = r"E:\Internship\PocketFM\books_from_uploaded_images.xlsx"

async def scrape_liza():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Navigating to Liza Dawson...")
        await page.goto("https://www.lizadawsonassociates.com/adult-fiction", wait_until="networkidle")
        
        # Wait a bit for JS to render the grid
        await page.wait_for_timeout(3000)
        
        # Get the rendered HTML
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        # Typically on Squarespace, titles in a grid are in .portfolio-title, .summary-title, or figcaption
        authors = set()
        
        # Let's check common classes
        for element in soup.select('.portfolio-title, .summary-title, .image-title, .sqs-block-image .image-caption p, .sqs-block-image .image-caption-wrapper p, .blog-title, .blog-item-title'):
            text = element.get_text(strip=True)
            if text:
                authors.add(text)
                
        # If we didn't find any using common classes, let's look for h1, h2, h3 inside the main content
        if not authors:
            print("Trying h1, h2, h3 tags...")
            for tag in ['h1', 'h2', 'h3']:
                for e in soup.find_all(tag):
                    text = e.get_text(strip=True)
                    if text and len(text.split()) < 6: # Author names are usually short
                        authors.add(text)
        
        authors = list(authors)
        print(f"Found {len(authors)} potential authors.")
        for a in authors[:10]:
            print(f" - {a}")
            
        if authors:
            print("Appending to Excel...")
            # Append to Excel
            df = pd.read_excel(EXCEL_FILE)
            
            new_rows = []
            for author in authors:
                new_rows.append({
                    "Name of Series": "",
                    "Author Name": author,
                    "Publisher": "",
                    "GoodReads series link": "",
                    "Number of PRIMARY books in the series": "",
                    "Rating (out of 5) of Primary Book 1": "",
                    "Ratings (#) of Primary Book 1": "",
                    "Synopsis (if available)": "",
                    "Romantasy = Yes or No?": "",
                    "Romantasy Sub-Genre of series": "",
                    "Name of agent": "Liza Dawson Associates"
                })
            
            new_df = pd.DataFrame(new_rows)
            # Ensure columns match
            # "book name and name of series will be the same column" - The column is "Name of Series"
            df = pd.concat([df, new_df], ignore_index=True)
            df.to_excel(EXCEL_FILE, index=False)
            print(f"Successfully appended {len(authors)} authors to {EXCEL_FILE}")
            
            try:
                sys.path.append(r"E:\Internship\PocketFM")
                import format_excel_script
                print("Applied formatting.")
            except Exception as e:
                print(f"Formatting failed: {e}")
        else:
            print("No authors found!")
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(scrape_liza())
