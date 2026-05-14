import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import re
import os

EXCEL_FILE = r"E:\Internship\PocketFM\Knight Agency.xlsx"
URL = "https://knightagency.net/ourbooks/?product_cat=paranormalromance"

def clean_name(text):
    return re.sub(r'[\n\t]', ' ', text).strip()

async def main():
    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)
    
    # Track how many "Unknown" authors we have
    missing_authors = df[df['Author Name'].astype(str).str.lower().isin(['unknown', 'n/a', 'nan', ''])]
    print(f"Found {len(missing_authors)} rows with missing authors.")
    
    if len(missing_authors) == 0:
        print("No missing authors to fix!")
        return

    print("Launching browser to scrape correct authors...")
    title_to_author = {}
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            channel="chrome"
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            device_scale_factor=1,
            is_mobile=False,
            has_touch=False,
            locale="en-US",
            timezone_id="America/New_York"
        )
        page = await context.new_page()
        
        current_page = 1
        has_next = True
        
        while has_next:
            page_url = f"{URL}&paged={current_page}" if current_page > 1 else URL
            print(f"Scraping {page_url}...")
            
            try:
                print("Waiting for page to load... The browser should be visible now.")
                await page.goto(page_url, timeout=60000)
                print("Page loaded! Giving you 30 seconds to look at the browser...")
                await asyncio.sleep(30) # Keep browser open so user can see it!
            except Exception as e:
                print(f"Failed to load {page_url}: {e}")
                break
                
            books = await page.query_selector_all('.product')
            if not books:
                print("No books found on this page. Ending scrape.")
                break
                
            for book in books:
                title_el = await book.query_selector('.woocommerce-loop-product__title')
                if not title_el: continue
                title = clean_name(await title_el.inner_text())
                
                # Robust author extraction
                author_el = await book.query_selector('.mfn-woo-product-author, .author, .woocommerce-loop-product__author, .product-author')
                author_name = "Unknown"
                if author_el:
                    author_name = clean_name(await author_el.inner_text())
                else:
                    fallback_author = await book.query_selector('span.author, .desc-author')
                    if fallback_author:
                        author_name = clean_name(await fallback_author.inner_text())
                
                if author_name and author_name.lower() != "unknown":
                    title_to_author[title.lower()] = author_name
                    
            # Check pagination
            next_button = await page.query_selector('a.next.page-numbers')
            if next_button:
                current_page += 1
            else:
                has_next = False
                
        await browser.close()
        
    print(f"\nScraped {len(title_to_author)} title-author pairs from the agency website.")
    
    # Update DataFrame
    updated_count = 0
    for index, row in missing_authors.iterrows():
        title = str(row['Name of Series']).lower()
        if title in title_to_author:
            correct_author = title_to_author[title]
            df.at[index, 'Author Name'] = correct_author
            print(f"  [Fixed] {row['Name of Series']} -> {correct_author}")
            updated_count += 1
            
    if updated_count > 0:
        print(f"\nSuccessfully repaired {updated_count} authors. Saving to Excel...")
        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='w') as writer:
            df.to_excel(writer, index=False, sheet_name='Agency Catalog')
            from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
            worksheet = writer.sheets['Agency Catalog']
            worksheet.freeze_panes = "A2"
            header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
            header_font = Font(bold=True, color="FFFFFF", size=11)
            thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
            col_widths = {"A": 35, "B": 25, "C": 20, "D": 40, "E": 12, "F": 12, "G": 12, "H": 70, "I": 15, "J": 30, "K": 25}
            for col_idx, col_name in enumerate(df.columns):
                col_letter = chr(65 + col_idx) if col_idx < 26 else chr(64 + (col_idx // 26)) + chr(65 + (col_idx % 26))
                worksheet.column_dimensions[col_letter].width = col_widths.get(col_letter, 20)
                for cell in worksheet[col_letter]:
                    cell.alignment = Alignment(wrap_text=True, vertical='top')
                    cell.border = thin_border
                    if cell.row == 1:
                        cell.fill = header_fill
                        cell.font = header_font
                        cell.alignment = Alignment(horizontal='center', vertical='center')
        print("Save complete!")
    else:
        print("Could not match any of the missing titles to the scraped data.")

if __name__ == "__main__":
    asyncio.run(main())
