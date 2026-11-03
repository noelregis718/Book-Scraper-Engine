"""
================================================================================
KENSINGTON BOOKS: FANTASY FICTION SCRAPER & GOODREADS ENRICHMENT
================================================================================
Target Category: https://www.kensingtonbooks.com/shop/product-category/fiction/fantasy-fiction/
Catalog Output:  E:\\Internship\\PocketFM\\Kensington_Fantasy_Fiction_Catalog.xlsx

Usage:
  Step 1 (Extract Kensington Books Only):
    python backend/scrape_kensington_fantasy.py --no-enrich

  Step 2 (Enrich Existing Catalog with Goodreads & Romantasy):
    python backend/scrape_kensington_fantasy.py --enrich-only

  Full Run (Step 1 + Step 2 Together):
    python backend/scrape_kensington_fantasy.py
================================================================================
"""

import asyncio
import os
import sys
import re
from copy import copy
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from playwright.async_api import async_playwright

# Include backend directory in path for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

try:
    from goodreads_scraper import GoodreadsScraper
    from romantasy_analyzer import identify_romantasy_subgenre
except ImportError:
    GoodreadsScraper = None
    identify_romantasy_subgenre = None

CATALOG_FILE = r"E:\Internship\PocketFM\Kensington_Fantasy_Fiction_Catalog.xlsx"
BASE_CATEGORY_URL = "https://www.kensingtonbooks.com/shop/product-category/fiction/fantasy-fiction/"

HEADERS = [
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
    "Name of agent"
]

def format_excel_sheet(ws):
    """Applies premium Kensington deep-teal styling to the worksheet in-place."""
    ws.views.sheetView[0].showGridLines = True
    header_fill = PatternFill(start_color="006666", end_color="006666", fill_type="solid")
    header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    data_font = Font(name="Segoe UI", size=10)
    border_side = Side(border_style="thin", color="D3D3D3")
    data_border = Border(left=border_side, right=border_side, top=border_side, bottom=border_side)
    
    ws.row_dimensions[1].height = 28
    for col_idx, header in enumerate(HEADERS, 1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = data_border
        
    for row_idx in range(2, ws.max_row + 1):
        ws.row_dimensions[row_idx].height = 20
        for col_idx in range(1, len(HEADERS) + 1):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.border = data_border
            cell.font = data_font
            
            # Alignments matching kensington standard
            if col_idx in [5, 6, 7]:
                cell.alignment = Alignment(horizontal="right", vertical="center")
            elif col_idx in [3, 9, 10]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")
                
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or '')
            if len(val_str) > 40:
                val_str = val_str[:40]
            max_len = max(max_len, len(val_str))
        ws.column_dimensions[col_letter].width = max(max_len + 4, 16)
        
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(HEADERS))}{ws.max_row}"

async def scrape_kensington_fantasy_books(enrich_goodreads=True):
    print("=" * 70)
    print("      KENSINGTON BOOKS: FANTASY FICTION CATALOG SCRAPER")
    print("=" * 70)
    print(f"Target Category: {BASE_CATEGORY_URL}")
    print(f"Output File:     {CATALOG_FILE}\n")

    extracted_books = []

    async with async_playwright() as p:
        print("[System] Launching browser in visible mode (headless=False) to pass Cloudflare...")
        try:
            browser = await p.chromium.launch(
                headless=False,
                channel="chrome",
                args=["--disable-blink-features=AutomationControlled"]
            )
        except Exception as e:
            print(f"[System] Chrome launch failed ({e}), using default Chromium...")
            browser = await p.chromium.launch(
                headless=False,
                args=["--disable-blink-features=AutomationControlled"]
            )

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 850}
        )

        page = await context.new_page()
        await page.add_init_script("delete navigator.__proto__.webdriver;")

        print(f"\n[Navigation] Opening: {BASE_CATEGORY_URL}")
        try:
            await page.goto(BASE_CATEGORY_URL, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"[Navigation Note] {e}")

        # Human verification pause - proven in scrape_kensington_authors.py
        print("\n" + "!" * 70)
        print("  CLOUD FLARE BYPASS REQUIRED!")
        print("  Please look at the browser window that just popped up on your screen.")
        print("  1. Solve/verify any Turnstile human challenge checkbox if prompted.")
        print("  2. Wait until the Kensington Fantasy Fiction books page has fully loaded.")
        print("!" * 70 + "\n")

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            input,
            ">>> Press [Enter] in this terminal ONLY when the Kensington Fantasy page has fully loaded on your screen..."
        )

        print("\n[System] User confirmed page load! Extracting books across all pages...")

        current_page_num = 1
        has_next = True

        while has_next:
            print(f"\n>>> Parsing Fantasy Fiction Page {current_page_num}...")
            
            # Wait for content to settle
            try:
                await page.wait_for_load_state("domcontentloaded", timeout=10000)
            except Exception:
                pass
            await asyncio.sleep(2)

            # Robust DOM extraction with multiple fallback strategies
            page_books = await page.evaluate("""() => {
                const books = [];
                const seenTitles = new Set();

                // Strategy 1: WooCommerce standard product elements
                const items = document.querySelectorAll('li.product, .type-product, .product, article.product, .book-item, .entry');
                
                items.forEach(item => {
                    let title = '';
                    const titleEl = item.querySelector('.woocommerce-loop-product__title, .product-title, h2, h3, .entry-title, a.title');
                    if (titleEl) {
                        title = titleEl.innerText.trim();
                    }
                    
                    let author = '';
                    const authorEl = item.querySelector('.author, .book-author, .byline, p.author, .posted_in, .artist, a[href*="/author/"], a[href*="/authors/"]');
                    if (authorEl) {
                        author = authorEl.innerText.trim();
                        author = author.replace(/^[Bb]y\\s+/, '').trim();
                    } else {
                        // Look for 'By ' pattern in item text
                        const allP = item.querySelectorAll('p, span, div');
                        for (const el of allP) {
                            const t = el.innerText.trim();
                            if (/^by\\s+[a-z\\s\\.\\-]+$/i.test(t) && t.length < 50) {
                                author = t.replace(/^by\\s+/i, '').trim();
                                break;
                            }
                        }
                    }
                    
                    let link = '';
                    const linkEl = item.querySelector('a.woocommerce-LoopProduct-link, a[href*="/product/"], a[href*="/book/"], a');
                    if (linkEl) {
                        link = linkEl.href;
                    }
                    
                    // Clean title: remove price strings, 'Sale!', etc.
                    title = title.replace(/\\n.*$/, '').trim();
                    
                    if (title && title.length > 1 && !seenTitles.has(title.toLowerCase())) {
                        const tLower = title.toLowerCase();
                        const blacklist = ['filter', 'search', 'sort', 'cart', 'checkout', 'home', 'shop', 'kensington', 'menu', 'account'];
                        if (!blacklist.some(b => tLower === b)) {
                            seenTitles.add(title.toLowerCase());
                            books.push({
                                title: title,
                                author: author || 'N/A',
                                link: link
                            });
                        }
                    }
                });

                // Strategy 2: If items is 0, scan all links pointing to product / book
                if (books.length === 0) {
                    const links = document.querySelectorAll('a[href*="/shop/product/"], a[href*="/book/"], a[href*="/product/"]');
                    links.forEach(a => {
                        const text = a.innerText.trim();
                        if (text && text.length > 2 && text.length < 80 && !seenTitles.has(text.toLowerCase())) {
                            const tLower = text.toLowerCase();
                            const blacklist = ['read more', 'view', 'details', 'buy', 'add to cart', 'shop'];
                            if (!blacklist.some(b => tLower.includes(b))) {
                                seenTitles.add(text.toLowerCase());
                                books.push({
                                    title: text,
                                    author: 'N/A',
                                    link: a.href
                                });
                            }
                        }
                    });
                }
                
                return books;
            }""")

            print(f"    Found {len(page_books)} books on page {current_page_num}.")
            
            if len(page_books) == 0:
                print("    [Notice] 0 books detected on this page. Saving debug snapshot...")
                try:
                    debug_html = await page.content()
                    debug_path = os.path.join(SCRIPT_DIR, "kensington_page_debug.html")
                    with open(debug_path, "w", encoding="utf-8") as f:
                        f.write(debug_html)
                    print(f"    [Notice] Saved HTML to {debug_path}")
                except Exception:
                    pass

            for b in page_books:
                if not any(x['title'].lower() == b['title'].lower() for x in extracted_books):
                    extracted_books.append(b)
                    print(f"    + '{b['title']}' by {b['author']}")

            # Check for next page
            next_btn = await page.query_selector('.woocommerce-pagination a.next, a.next.page-numbers, .pagination .next, a.next')
            if next_btn:
                next_url = await next_btn.get_attribute('href')
                if next_url and next_url != "#" and next_url != page.url:
                    print(f"    [Pagination] Navigating to next page: {next_url}")
                    current_page_num += 1
                    try:
                        await page.goto(next_url, wait_until="domcontentloaded", timeout=60000)
                        await asyncio.sleep(2)
                    except Exception as e:
                        print(f"    [Pagination Error] {e}")
                        has_next = False
                else:
                    has_next = False
            else:
                print("    [Pagination] Reached last page. No next page link found.")
                has_next = False

        print(f"\n" + "=" * 70)
        print(f"  TOTAL KENSINGTON FANTASY BOOKS EXTRACTED: {len(extracted_books)}")
        print("=" * 70)

        if not extracted_books:
            print("\n[Warning] No books were extracted. Please check kensington_page_debug.html to inspect the DOM structure.")
            await browser.close()
            return

        # Write extracted books to Excel
        if not os.path.exists(CATALOG_FILE):
            wb = Workbook()
            ws = wb.active
            ws.title = "Kensington Fantasy"
        else:
            wb = load_workbook(CATALOG_FILE)
            ws = wb.active

        # Preserve header, clear existing data rows
        if ws.max_row > 1:
            ws.delete_rows(2, ws.max_row)

        for idx, book in enumerate(extracted_books, 2):
            ws.cell(row=idx, column=1, value=book['title'])     # Name of Series / Book Title
            ws.cell(row=idx, column=2, value=book['author'])    # Author Name
            ws.cell(row=idx, column=3, value="Kensington")      # Publisher
            ws.cell(row=idx, column=4, value="N/A")             # GoodReads series link
            ws.cell(row=idx, column=5, value=1)                 # Number of PRIMARY books
            ws.cell(row=idx, column=6, value="N/A")             # Rating (out of 5)
            ws.cell(row=idx, column=7, value="N/A")             # Ratings (#)
            ws.cell(row=idx, column=8, value="N/A")             # Synopsis
            ws.cell(row=idx, column=9, value="No")              # Romantasy Yes/No
            ws.cell(row=idx, column=10, value="N/A")            # Romantasy Subgenre
            ws.cell(row=idx, column=11, value="N/A")            # Name of agent

        format_excel_sheet(ws)
        wb.save(CATALOG_FILE)
        print(f"\n>>> Step 1 Complete: Successfully saved {len(extracted_books)} books to:")
        print(f"    {CATALOG_FILE}")

        # Optional Step 2 if requested
        if enrich_goodreads:
            await enrich_existing_catalog(context=context)

        await browser.close()
        print("\n[Done] Kensington scraping completed successfully.")

async def enrich_existing_catalog(context=None):
    """Enriches the existing Excel catalog with Goodreads links, ratings, synopsis, and Romantasy tags."""
    print("\n" + "=" * 70)
    print("      GOODREADS & ROMANTASY ENRICHMENT (STEP 2)")
    print("=" * 70)

    if not os.path.exists(CATALOG_FILE):
        print(f"[Error] Catalog file does not exist: {CATALOG_FILE}")
        return

    wb = load_workbook(CATALOG_FILE)
    ws = wb.active

    # Find rows that need Goodreads enrichment
    rows_to_enrich = []
    for r_idx in range(2, ws.max_row + 1):
        title = ws.cell(row=r_idx, column=1).value
        author = ws.cell(row=r_idx, column=2).value
        gr_link = ws.cell(row=r_idx, column=4).value

        if title and str(title).strip() and str(title).strip().lower() not in ["n/a", "none", "nan"]:
            if not gr_link or str(gr_link).strip().lower() in ["n/a", "none", "nan"]:
                rows_to_enrich.append((r_idx, str(title).strip(), str(author or '').strip()))

    print(f"Total books needing Goodreads enrichment: {len(rows_to_enrich)}")
    if not rows_to_enrich:
        print("All books in catalog are already enriched!")
        return

    async def run_enrichment_loop(active_context):
        gr_scraper = GoodreadsScraper(headless=False)
        sem = asyncio.Semaphore(3)

        async def enrich_single_book(row_idx, title, author):
            async with sem:
                print(f"  [Row {row_idx}] Searching Goodreads for: '{title}' by '{author}'...")
                try:
                    gr_data = await gr_scraper.scrape_goodreads_data(active_context, title, author)
                    if gr_data:
                        series_link = gr_data.get("GoodReads_Series_URL")
                        book_link = gr_data.get("GoodReads_Book_URL")
                        final_link = series_link if series_link and series_link != "N/A" else (book_link or "N/A")
                        synopsis = gr_data.get("Description", "N/A")
                        
                        rom_sub = "N/A"
                        if identify_romantasy_subgenre:
                            rom_sub = identify_romantasy_subgenre(synopsis, gr_data.get("Genre", ""))

                        ws.cell(row=row_idx, column=4, value=final_link)
                        ws.cell(row=row_idx, column=5, value=gr_data.get("Num_Primary_Books", 1) if final_link != "N/A" else 1)
                        ws.cell(row=row_idx, column=6, value=gr_data.get("GoodReads_Rating", "N/A"))
                        ws.cell(row=row_idx, column=7, value=gr_data.get("GoodReads_Rating_Count", "N/A"))
                        ws.cell(row=row_idx, column=8, value=synopsis)
                        ws.cell(row=row_idx, column=9, value="Yes" if rom_sub != "N/A" else "No")
                        ws.cell(row=row_idx, column=10, value=rom_sub)
                        print(f"    [Success] Mapped: {final_link} | Rating: {gr_data.get('GoodReads_Rating')} | Romantasy: {rom_sub}")
                    else:
                        print(f"    [Skip] No match on Goodreads for '{title}'.")
                except Exception as err:
                    print(f"    [Error] Failed to enrich '{title}': {err}")

        tasks = [enrich_single_book(r_idx, title, author) for r_idx, title, author in rows_to_enrich]
        await asyncio.gather(*tasks)

        format_excel_sheet(ws)
        wb.save(CATALOG_FILE)
        print(f"\n>>> Catalog enrichment complete! Saved to {CATALOG_FILE}")

    if context:
        await run_enrichment_loop(context)
    else:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            new_ctx = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            await run_enrichment_loop(new_ctx)
            await browser.close()

if __name__ == "__main__":
    if "--enrich-only" in sys.argv:
        asyncio.run(enrich_existing_catalog())
    elif "--no-enrich" in sys.argv:
        asyncio.run(scrape_kensington_fantasy_books(enrich_goodreads=False))
    else:
        asyncio.run(scrape_kensington_fantasy_books(enrich_goodreads=True))
