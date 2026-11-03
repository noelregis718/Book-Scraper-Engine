import asyncio
import subprocess
import time
import os
import re
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from playwright.async_api import async_playwright

CHROME_PATH = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
USER_DATA = r"E:\Internship\PocketFM\backend\chrome_live_profile"
TARGET_FILE = r"E:\Internship\PocketFM\Kensington_Storefront_Fantasy_Catalog.xlsx"
BASE_ROMANCE_URL = "https://www.kensingtonbooks.com/shop/product-category/fiction/romance/"
TOTAL_PAGES = 46

HEADERS = [
    "Book Title",
    "Author Name",
    "Publisher",
    "Category",
    "Storefront URL",
    "Synopsis (Card Summary)",
    "Cover Image URL"
]

def normalize_title(t):
    if not t: return ""
    t = str(t).strip().lower()
    t = t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    t = re.sub(r'[:\-—\(].*$', '', t) # Strip subtitles like ": Deluxe Limited Edition"
    t = re.sub(r'[^\w\s]', '', t)
    for art in ['the ', 'a ', 'an ']:
        if t.startswith(art):
            t = t[len(art):]
            break
    return re.sub(r'\s+', ' ', t).strip()

def load_existing_catalog():
    existing_items = []
    seen_titles = set()
    
    if os.path.exists(TARGET_FILE):
        wb = openpyxl.load_workbook(TARGET_FILE, data_only=True)
        ws = wb.active
        for r in range(2, ws.max_row + 1):
            title = str(ws.cell(row=r, column=1).value or "").strip()
            author = str(ws.cell(row=r, column=2).value or "").strip()
            pub = str(ws.cell(row=r, column=3).value or "Kensington").strip()
            cat = str(ws.cell(row=r, column=4).value or "Fantasy Fiction").strip()
            url = str(ws.cell(row=r, column=5).value or "").strip()
            syn = str(ws.cell(row=r, column=6).value or "").strip()
            img = str(ws.cell(row=r, column=7).value or "").strip()
            
            if title:
                norm = normalize_title(title)
                seen_titles.add(norm)
                existing_items.append({
                    "title": title,
                    "author": author,
                    "publisher": pub,
                    "category": cat,
                    "url": url,
                    "synopsis": syn,
                    "image": img
                })
        wb.close()
    return existing_items, seen_titles

def save_catalog(filepath, all_items):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Kensington Storefront Catalog"
    ws.views.sheetView[0].showGridLines = True
    
    header_fill = PatternFill(start_color="006666", end_color="006666", fill_type="solid")
    header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    data_font = Font(name="Segoe UI", size=10)
    border_side = Side(border_style="thin", color="D3D3D3")
    data_border = Border(left=border_side, right=border_side, top=border_side, bottom=border_side)
    
    # Headers
    ws.row_dimensions[1].height = 28
    for col_idx, h in enumerate(HEADERS, 1):
        cell = ws.cell(row=1, column=col_idx, value=h)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = data_border
        
    # Rows
    for row_idx, item in enumerate(all_items, start=2):
        ws.row_dimensions[row_idx].height = 22
        vals = [
            item.get("title", ""),
            item.get("author", ""),
            item.get("publisher", "Kensington"),
            item.get("category", "Romance"),
            item.get("url", ""),
            item.get("synopsis", ""),
            item.get("image", "")
        ]
        for col_idx, val in enumerate(vals, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=val)
            cell.font = data_font
            cell.border = data_border
            if col_idx in [3, 4]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")
                
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
    print(f"[Workbook Saved] {filepath} with {len(all_items)} total unique books.")

async def scrape_all_romance_pages():
    print("=" * 80)
    print("      KENSINGTON STOREFRONT: ROMANCE HARVEST & DEDUPLICATION")
    print("=" * 80)
    
    existing_items, seen_titles = load_existing_catalog()
    print(f"Loaded {len(existing_items)} existing books from Fantasy Catalog.")
    print(f"Tracking {len(seen_titles)} unique normalized titles to prevent duplicates.\n")
    
    print("[1/3] Launching Native Chrome...")
    proc = subprocess.Popen([
        CHROME_PATH,
        "--remote-debugging-port=9222",
        f"--user-data-dir={USER_DATA}",
        "--no-first-run",
        "--no-default-browser-check",
        BASE_ROMANCE_URL
    ])
    await asyncio.sleep(4)
    
    new_romance_books = []
    skipped_count = 0
    
    async with async_playwright() as p:
        try:
            print("[2/3] Connecting to Chrome over CDP...")
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else await context.new_page()
            
            # Verify clearance
            print("Verifying Cloudflare clearance...")
            for _ in range(15):
                t = await page.title()
                if "Romance" in t or "Archives" in t:
                    print(f"  Clearance active: '{t}'")
                    break
                await asyncio.sleep(1)
                
            print(f"\n[3/3] Scraping All {TOTAL_PAGES} Romance Pages...")
            for page_num in range(1, TOTAL_PAGES + 1):
                url = BASE_ROMANCE_URL if page_num == 1 else f"{BASE_ROMANCE_URL}page/{page_num}/"
                print(f"Loading Page {page_num}/{TOTAL_PAGES}...", end="", flush=True)
                
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=40000)
                    await asyncio.sleep(1.8) # lightweight pause to ensure rendering
                except Exception as ex:
                    print(f" [Retrying on error: {ex}] ", end="")
                    await asyncio.sleep(3)
                    await page.goto(url, wait_until="domcontentloaded", timeout=40000)
                    
                cards = await page.query_selector_all("li.product")
                page_added = 0
                page_skipped = 0
                
                for c in cards:
                    try:
                        t_el = await c.query_selector(".woocommerce-loop-product__title, h2, h3")
                        title = (await t_el.inner_text()).strip() if t_el else ""
                        if not title: continue
                        
                        norm = normalize_title(title)
                        if norm in seen_titles:
                            page_skipped += 1
                            skipped_count += 1
                            continue
                            
                        # Extract author
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
                        
                        new_item = {
                            "title": title,
                            "author": author,
                            "publisher": "Kensington",
                            "category": "Romance",
                            "url": link,
                            "synopsis": synopsis,
                            "image": img
                        }
                        
                        new_romance_books.append(new_item)
                        seen_titles.add(norm)
                        page_added += 1
                    except Exception:
                        pass
                        
                print(f" -> Found {len(cards)} books: +{page_added} unique added, {page_skipped} skipped duplicates. (Total New Unique: {len(new_romance_books)})")
                
                # Checkpoint save every 10 pages so no progress is ever lost
                if page_num % 10 == 0 or page_num == TOTAL_PAGES:
                    combined = existing_items + new_romance_books
                    save_catalog(TARGET_FILE, combined)
                    print(f"  [Checkpoint] Saved {len(combined)} total books to Excel at page {page_num}.\n")
                    
            await browser.close()
        except Exception as e:
            print(f"[Error in Scraper]: {e}")
        finally:
            proc.terminate()
            
    # Final Write
    final_combined = existing_items + new_romance_books
    save_catalog(TARGET_FILE, final_combined)
    
    print("\n" + "=" * 80)
    print("                  ROMANCE HARVEST COMPLETE!")
    print(f"  Existing Fantasy Books: {len(existing_items)}")
    print(f"  New Unique Romance Books Added: {len(new_romance_books)}")
    print(f"  Total Duplicates Skipped: {skipped_count}")
    print(f"  Final Combined Excel Rows: {len(final_combined)}")
    print(f"  Saved to: {TARGET_FILE}")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(scrape_all_romance_pages())

