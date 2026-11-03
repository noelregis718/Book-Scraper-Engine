import asyncio
import subprocess
import time
import os
import sys
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from playwright.async_api import async_playwright

CHROME_PATH = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
USER_DATA = r"E:\Internship\PocketFM\backend\chrome_live_profile"
BASE_URL = "https://www.kensingtonbooks.com/shop/product-category/fiction/fantasy-fiction/"
OUTPUT_FILE = r"E:\Internship\PocketFM\Kensington_Storefront_Fantasy_Catalog.xlsx"

HEADERS = [
    "Book Title",
    "Author Name",
    "Publisher",
    "Category",
    "Storefront URL",
    "Synopsis (Card Summary)",
    "Cover Image URL"
]

def format_excel_catalog(filepath, rows_data):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Kensington Fantasy Storefront"
    ws.views.sheetView[0].showGridLines = True
    
    # Header styling
    header_fill = PatternFill(start_color="006666", end_color="006666", fill_type="solid")
    header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    data_font = Font(name="Segoe UI", size=10)
    border_side = Side(border_style="thin", color="D3D3D3")
    data_border = Border(left=border_side, right=border_side, top=border_side, bottom=border_side)
    
    # Write Headers
    ws.row_dimensions[1].height = 28
    for col_idx, header in enumerate(HEADERS, 1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = data_border
        
    # Write Data
    for row_idx, item in enumerate(rows_data, start=2):
        ws.row_dimensions[row_idx].height = 22
        
        row_vals = [
            item.get("title", ""),
            item.get("author", ""),
            item.get("publisher", "Kensington"),
            item.get("category", "Fantasy Fiction"),
            item.get("url", ""),
            item.get("synopsis", ""),
            item.get("image", "")
        ]
        
        for col_idx, val in enumerate(row_vals, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=val)
            cell.font = data_font
            cell.border = data_border
            
            if col_idx in [3, 4]: # Publisher, Category
                cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")

    # Column dimensions
    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = 0
        for cell in col:
            val_str = str(cell.value or '')
            if len(val_str) > 40:
                val_str = val_str[:40]
            max_len = max(max_len, len(val_str))
        ws.column_dimensions[col_letter].width = max(max_len + 4, 18)
        
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(HEADERS))}{ws.max_row}"
    
    wb.save(filepath)
    print(f"\n[Saved] Excel workbook written successfully to: {filepath}")

async def scrape_kensington_storefront():
    print("=" * 75)
    print("      KENSINGTON BOOKS: FANTASY FICTION STOREFRONT SCRAPER")
    print("=" * 75)
    print(f"Target URL:  {BASE_URL}")
    print(f"Output File: {OUTPUT_FILE}\n")
    
    print("[1/4] Launching Native Chrome with Remote Debugging...")
    proc = subprocess.Popen([
        CHROME_PATH,
        "--remote-debugging-port=9222",
        f"--user-data-dir={USER_DATA}",
        "--no-first-run",
        "--no-default-browser-check",
        BASE_URL
    ])
    
    await asyncio.sleep(4)
    all_books = []
    seen_titles = set()
    
    async with async_playwright() as p:
        try:
            print("[2/4] Connecting Playwright over CDP (http://127.0.0.1:9222)...")
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else await context.new_page()
            
            # Wait for Cloudflare clearance
            print("Checking Cloudflare security clearance...")
            for i in range(20):
                try:
                    title = await page.title()
                    if "Fantasy Archives" in title:
                        print(f"  -> Clearance verified in {i+1}s: '{title}'")
                        break
                except Exception:
                    pass
                await asyncio.sleep(1)
                
            print("\n[3/4] Scraping Catalog Across All Pages (1 to 6)...")
            for page_num in range(1, 7):
                page_url = BASE_URL if page_num == 1 else f"{BASE_URL}page/{page_num}/"
                print(f"\n--- Loading Page {page_num}/6: {page_url} ---")
                
                try:
                    await page.goto(page_url, wait_until="domcontentloaded", timeout=45000)
                    await asyncio.sleep(2.5)
                except Exception as e:
                    print(f"  [Warning] Navigation note on page {page_num}: {e}")
                    
                # Extract all cards
                cards = await page.query_selector_all("li.product")
                print(f"  Found {len(cards)} books on Page {page_num}")
                
                page_extracted = 0
                for c in cards:
                    try:
                        # Title
                        t_el = await c.query_selector(".woocommerce-loop-product__title, h2, h3")
                        title = (await t_el.inner_text()).strip() if t_el else ""
                        if not title:
                            continue
                            
                        # Author
                        a_el = await c.query_selector(".single-author, span[class*='author']")
                        author = (await a_el.inner_text()).strip() if a_el else ""
                        
                        # Link
                        link_el = await c.query_selector("a.woocommerce-LoopProduct-link, a")
                        link = (await link_el.get_attribute("href")).strip() if link_el else ""
                        
                        # Image
                        img_el = await c.query_selector("img.wp-post-image, img")
                        img = (await img_el.get_attribute("src")).strip() if img_el else ""
                        
                        # Synopsis
                        p_el = await c.query_selector("p")
                        synopsis = (await p_el.inner_text()).strip() if p_el else ""
                        
                        book_entry = {
                            "title": title,
                            "author": author,
                            "publisher": "Kensington",
                            "category": "Fantasy Fiction",
                            "url": link,
                            "synopsis": synopsis,
                            "image": img
                        }
                        
                        all_books.append(book_entry)
                        seen_titles.add(title.lower())
                        page_extracted += 1
                    except Exception as err:
                        print(f"    Error reading card: {err}")
                        
                print(f"  Successfully extracted {page_extracted} books from Page {page_num} (Total so far: {len(all_books)})")
                
            await browser.close()
        except Exception as e:
            print(f"[Error in Scraper]: {e}")
        finally:
            proc.terminate()
            
    print(f"\n[4/4] Writing {len(all_books)} scraped books to Excel...")
    format_excel_catalog(OUTPUT_FILE, all_books)
    
    print("\n" + "=" * 75)
    print("                  SCRAPING RUN COMPLETE!")
    print(f"  Total Books Scraped: {len(all_books)}")
    print(f"  Unique Book Titles:  {len(seen_titles)}")
    print(f"  Catalog Saved to:    {OUTPUT_FILE}")
    print("=" * 75)

if __name__ == "__main__":
    asyncio.run(scrape_kensington_storefront())

