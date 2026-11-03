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
BASE_URL = "https://www.kensingtonbooks.com/shop/product-category/fiction/fantasy-fiction/?yith_wcan=1&product_cat=fantasy-fiction+romance"
TOTAL_PAGES = 4

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
    t = re.sub(r'[:\-—\(].*$', '', t)
    t = re.sub(r'[^\w\s]', '', t)
    for art in ['the ', 'a ', 'an ']:
        if t.startswith(art):
            t = t[len(art):]
            break
    return re.sub(r'\s+', ' ', t).strip()

def load_existing_catalog():
    existing_items = []
    seen_titles = {}
    
    if os.path.exists(TARGET_FILE):
        wb = openpyxl.load_workbook(TARGET_FILE, data_only=True)
        ws = wb.active
        for r in range(2, ws.max_row + 1):
            title = str(ws.cell(row=r, column=1).value or "").strip()
            author = str(ws.cell(row=r, column=2).value or "").strip()
            pub = str(ws.cell(row=r, column=3).value or "Kensington").strip()
            cat = str(ws.cell(row=r, column=4).value or "").strip()
            url = str(ws.cell(row=r, column=5).value or "").strip()
            syn = str(ws.cell(row=r, column=6).value or "").strip()
            img = str(ws.cell(row=r, column=7).value or "").strip()
            
            if title:
                item = {
                    "title": title,
                    "author": author,
                    "publisher": pub,
                    "category": cat,
                    "url": url,
                    "synopsis": syn,
                    "image": img
                }
                norm = normalize_title(title)
                seen_titles[norm] = len(existing_items) # store index
                existing_items.append(item)
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
            item.get("category", ""),
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

async def scrape_romantasy_filter():
    print("=" * 80)
    print("      KENSINGTON STOREFRONT: FANTASY + ROMANCE FILTER SCRAPER")
    print("=" * 80)
    print(f"Target URL: {BASE_URL}")
    print(f"Total Pages: {TOTAL_PAGES} (219 books)\n")
    
    existing_items, seen_titles = load_existing_catalog()
    print(f"Loaded {len(existing_items)} existing books from catalog.")
    
    print("[1/3] Launching Native Chrome...")
    proc = subprocess.Popen([
        CHROME_PATH,
        "--remote-debugging-port=9222",
        f"--user-data-dir={USER_DATA}",
        "--no-first-run",
        "--no-default-browser-check",
        BASE_URL
    ])
    await asyncio.sleep(4)
    
    new_items = []
    already_present_count = 0
    
    async with async_playwright() as p:
        try:
            print("[2/3] Connecting to Chrome over CDP...")
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            page = browser.contexts[0].pages[0]
            
            for _ in range(15):
                t = await page.title()
                if "Fantasy Archives" in t:
                    print(f"Clearance active: '{t}'")
                    break
                await asyncio.sleep(1)
                
            print(f"\n[3/3] Scraping All {TOTAL_PAGES} Pages...")
            for page_num in range(1, TOTAL_PAGES + 1):
                if page_num == 1:
                    url = BASE_URL
                else:
                    url = f"https://www.kensingtonbooks.com/shop/product-category/fiction/fantasy-fiction/page/{page_num}/?yith_wcan=1&product_cat=fantasy-fiction+romance"
                    
                print(f"Loading Page {page_num}/{TOTAL_PAGES}...", end="", flush=True)
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=40000)
                    await asyncio.sleep(2)
                except Exception as ex:
                    print(f" [Retrying on error: {ex}] ", end="")
                    await asyncio.sleep(3)
                    await page.goto(url, wait_until="domcontentloaded", timeout=40000)
                    
                cards = await page.query_selector_all("li.product")
                page_added = 0
                page_already_present = 0
                
                for c in cards:
                    try:
                        t_el = await c.query_selector(".woocommerce-loop-product__title, h2, h3")
                        title = (await t_el.inner_text()).strip() if t_el else ""
                        if not title: continue
                        
                        norm = normalize_title(title)
                        
                        if norm in seen_titles:
                            # Already in catalog: Update its category to note Romantasy if currently just Fantasy or Romance
                            idx = seen_titles[norm]
                            cur_cat = existing_items[idx]["category"]
                            if "Romance" in cur_cat and "Fantasy" in cur_cat:
                                pass
                            elif "Fantasy" in cur_cat:
                                existing_items[idx]["category"] = "Fantasy Fiction / Romantasy"
                            elif "Romance" in cur_cat:
                                existing_items[idx]["category"] = "Romance / Romantasy"
                            page_already_present += 1
                            already_present_count += 1
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
                            "category": "Romantasy",
                            "url": link,
                            "synopsis": synopsis,
                            "image": img
                        }
                        
                        seen_titles[norm] = len(existing_items) + len(new_items)
                        new_items.append(new_item)
                        page_added += 1
                    except Exception:
                        pass
                        
                print(f" -> Found {len(cards)} books: +{page_added} new unique added, {page_already_present} already present in catalog. (Total New: {len(new_items)})")
                
            await browser.close()
        except Exception as e:
            print(f"[Error in Scraper]: {e}")
        finally:
            proc.terminate()
            
    # Save combined catalog
    final_combined = existing_items + new_items
    save_catalog(TARGET_FILE, final_combined)
    
    print("\n" + "=" * 80)
    print("               ROMANTASY FILTER HARVEST COMPLETE!")
    print(f"  Total Books Evaluated from Filter: 219")
    print(f"  Already Present & Tagged in Catalog: {already_present_count}")
    print(f"  Brand-New Unique Books Added: {len(new_items)}")
    print(f"  Final Total Books in Catalog: {len(final_combined)}")
    print(f"  Saved to: {TARGET_FILE}")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(scrape_romantasy_filter())

