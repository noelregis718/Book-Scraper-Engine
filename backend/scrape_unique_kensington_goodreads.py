"""
================================================================================
KENSINGTON UNIQUE CATALOG: HIGH-SPEED GOODREADS ENRICHMENT SCRAPER
================================================================================
Target:  E:\\Internship\\PocketFM\\Kensington_Unique_Fantasy_Fiction_Catalog.xlsx
Input:   902 Unique Kensington Books
Output:  GoodReads Links, Primary Book Counts, Ratings (# and /5),
         Synopses, and Romantasy 12-Subgenre Classification.
Features:
  - Auto-resumable: skips already enriched rows
  - Multi-worker concurrency (Semaphore 6) for rapid processing
  - Saves checkpoint every 10 books
  - Unbuffered streaming console output
================================================================================
"""

import asyncio
import os
import sys
import re
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from playwright.async_api import async_playwright

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from goodreads_scraper import GoodreadsScraper
from romantasy_analyzer import identify_romantasy_subgenre

CATALOG_FILE = r"E:\Internship\PocketFM\Kensington_Unique_Fantasy_Fiction_Catalog.xlsx"

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

async def run_goodreads_enrichment():
    print("=" * 70, flush=True)
    print("   RESUMING KENSINGTON GOODREADS ENRICHMENT SCRAPER", flush=True)
    print("=" * 70, flush=True)
    print(f"Catalog File: {CATALOG_FILE}\n", flush=True)

    if not os.path.exists(CATALOG_FILE):
        print(f"[Error] Catalog file does not exist: {CATALOG_FILE}", flush=True)
        return

    wb = openpyxl.load_workbook(CATALOG_FILE)
    ws = wb.active

    # Identify pending rows (where GoodReads series link is missing / N/A)
    pending_rows = []
    already_done = 0
    for r_idx in range(2, ws.max_row + 1):
        title = ws.cell(row=r_idx, column=1).value
        author = ws.cell(row=r_idx, column=2).value
        gr_link = ws.cell(row=r_idx, column=4).value

        t_str = str(title or '').strip()
        a_str = str(author or '').strip()
        link_str = str(gr_link or '').strip().lower()

        if t_str and t_str.lower() not in ["n/a", "none", "nan"]:
            if link_str.startswith("http") or "not found" in link_str:
                already_done += 1
            else:
                pending_rows.append((r_idx, t_str, a_str))

    total_pending = len(pending_rows)
    total_books = ws.max_row - 1
    print(f"Total Books in Catalog:     {total_books}", flush=True)
    print(f"Already Enriched:           {already_done}", flush=True)
    print(f"Remaining Books to Enrich:  {total_pending}", flush=True)
    print(f"Current Progress:           {(already_done / total_books) * 100:.1f}%\n", flush=True)

    if total_pending == 0:
        print(">>> 100% Complete! All books in this catalog are already enriched.", flush=True)
        return

    write_lock = asyncio.Lock()
    processed_count = 0
    success_count = 0

    async def save_progress():
        async with write_lock:
            try:
                format_excel_sheet(ws)
                wb.save(CATALOG_FILE)
                print(f"    [Checkpoint Saved] Updated {CATALOG_FILE}", flush=True)
            except Exception as e:
                print(f"    [Save Warning] Could not save checkpoint: {e}", flush=True)

    async with async_playwright() as p:
        print("[System] Launching Playwright browser instance...", flush=True)
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )

        scraper = GoodreadsScraper(headless=True)
        semaphore = asyncio.Semaphore(6) # 6 concurrent workers for optimal throughput

        async def process_single_book(r_idx, title, author):
            nonlocal processed_count, success_count
            async with semaphore:
                cur_num = already_done + processed_count + 1
                print(f"[{cur_num}/{total_books}] [Row {r_idx}] Searching: '{title}' by '{author}'...", flush=True)
                try:
                    data = await scraper.scrape_goodreads_data(context, title, author)
                    
                    if data:
                        series_url = data.get("GoodReads_Series_URL", "N/A")
                        book_url = data.get("GoodReads_Book_URL", "N/A")
                        final_link = series_url if series_url and series_url != "N/A" else (book_url or "N/A")
                        
                        rating = data.get("Book1_Rating") or data.get("GoodReads_Rating") or "N/A"
                        rating_count = data.get("Book1_Num_Ratings") or data.get("GoodReads_Rating_Count") or "N/A"
                        synopsis = data.get("Description", "N/A")
                        num_books = data.get("Num_Primary_Books", 1) if final_link != "N/A" else 1

                        rom_sub = "N/A"
                        if synopsis and synopsis != "N/A":
                            rom_sub = identify_romantasy_subgenre(synopsis, data.get("Genre", ""))

                        async with write_lock:
                            ws.cell(row=r_idx, column=4, value=final_link)
                            ws.cell(row=r_idx, column=5, value=num_books)
                            ws.cell(row=r_idx, column=6, value=rating)
                            ws.cell(row=r_idx, column=7, value=rating_count)
                            ws.cell(row=r_idx, column=8, value=synopsis)
                            if rom_sub != "N/A":
                                ws.cell(row=r_idx, column=9, value="Yes")
                                ws.cell(row=r_idx, column=10, value=rom_sub)
                            
                        success_count += 1
                        print(f"    -> [SUCCESS] Row {r_idx}: Rating {rating} ({rating_count}) | Romantasy: {rom_sub}", flush=True)
                    else:
                        print(f"    -> [NOT FOUND] Row {r_idx}: No match for '{title}'", flush=True)
                        async with write_lock:
                            ws.cell(row=r_idx, column=4, value="N/A (Not Found)")
                            
                except Exception as err:
                    print(f"    -> [ERROR] Row {r_idx}: '{title}': {err}", flush=True)

                processed_count += 1
                if processed_count % 10 == 0:
                    await save_progress()

        # Batch in chunks of 24
        batch_size = 24
        for i in range(0, len(pending_rows), batch_size):
            batch = pending_rows[i:i + batch_size]
            tasks = [process_single_book(r_idx, t, a) for r_idx, t, a in batch]
            await asyncio.gather(*tasks)
            await save_progress()
            completed_overall = already_done + processed_count
            pct = (completed_overall / total_books) * 100
            print(f"\n>>> Milestone: {completed_overall}/{total_books} books completed ({pct:.1f}%)\n", flush=True)

        await browser.close()

    print("\n" + "=" * 70, flush=True)
    print("      SCRAPING 100% COMPLETE - SAVING FINAL CATALOG", flush=True)
    print("=" * 70, flush=True)
    format_excel_sheet(ws)
    wb.save(CATALOG_FILE)
    print(f"Catalog 100% enriched! Saved to: {CATALOG_FILE}\n", flush=True)

if __name__ == "__main__":
    asyncio.run(run_goodreads_enrichment())
