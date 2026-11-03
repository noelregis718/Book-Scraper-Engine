import urllib.request
import json
import urllib.parse
import os
import sys
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

CATALOG_FILE = r"E:\Internship\PocketFM\Kensington_Fantasy_Fiction_Catalog.xlsx"

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

def fetch_and_append_romance():
    print("=" * 70)
    print("   FETCHING & APPENDING KENSINGTON ROMANCE CATALOG")
    print("   Category: https://www.kensingtonbooks.com/shop/product-category/fiction/romance/?yith_wcan=1&product_cat=romance")
    print(f"   Target Catalog: {CATALOG_FILE}")
    print("=" * 70)

    # 1. Load existing titles to avoid duplicates
    wb = openpyxl.load_workbook(CATALOG_FILE)
    ws = wb.active
    existing_keys = set()
    for r in range(2, ws.max_row + 1):
        t = str(ws.cell(row=r, column=1).value or "").strip().lower()
        a = str(ws.cell(row=r, column=2).value or "").strip().lower()
        if t:
            existing_keys.add((t, a))
            existing_keys.add(t)

    initial_row_count = ws.max_row
    print(f"Existing rows in catalog: {initial_row_count}")

    # 2. Targeted Kensington Romance Queries
    queries = [
        {"publisher": "kensington", "subject": "romance"},
        {"publisher": "kensington", "subject": "contemporary romance"},
        {"publisher": "kensington", "subject": "historical romance"},
        {"publisher": "kensington", "subject": "romantic suspense"},
        {"publisher": "kensington", "subject": "regency romance"},
        {"publisher": "kensington", "subject": "western romance"},
        {"publisher": "kensington", "subject": "holiday romance"},
        {"publisher": "kensington publishing", "subject": "romance"},
        {"publisher": "kensington publishing", "subject": "historical romance"},
        {"publisher": "zebra", "subject": "romance"},
        {"publisher": "dafina", "subject": "romance"},
        # Top Kensington Romance Bestsellers & Imprints
        {"publisher": "kensington", "author": "Fern Michaels"},
        {"publisher": "kensington", "author": "Janet Dailey"},
        {"publisher": "kensington", "author": "Lisa Jackson"},
        {"publisher": "kensington", "author": "Kat Martin"},
        {"publisher": "kensington", "author": "Jo Goodman"},
        {"publisher": "kensington", "author": "Mary Jo Putney"},
        {"publisher": "kensington", "author": "Donna Grant"},
        {"publisher": "kensington", "author": "Beverly Jenkins"},
        {"publisher": "kensington", "author": "Lori Foster"},
        {"publisher": "kensington", "author": "Shannon Drake"},
        {"publisher": "kensington", "author": "Rosalyn Eves"}
    ]

    new_books = []
    seen_new = set()

    for q_params in queries:
        encoded = urllib.parse.urlencode(q_params)
        url = f"https://openlibrary.org/search.json?{encoded}&limit=100"
        print(f"Querying: {q_params}...")
        req = urllib.request.Request(url, headers={"User-Agent": "PocketFM-Kensington-Romance/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                docs = data.get("docs", [])
                added_this_query = 0
                for d in docs:
                    title = d.get("title", "").strip()
                    authors = d.get("author_name", [])
                    author = authors[0].strip() if authors else "N/A"
                    
                    if title and author and len(title) > 1:
                        t_norm = title.lower()
                        a_norm = author.lower()
                        
                        # Filter non-fiction
                        blacklist = ["dictionary", "handbook", "grammar", "how to", "cookbook", "almanac"]
                        if any(b in t_norm for b in blacklist):
                            continue

                        if (t_norm, a_norm) not in existing_keys and t_norm not in existing_keys and t_norm not in seen_new:
                            seen_new.add(t_norm)
                            new_books.append({
                                "title": title,
                                "author": author,
                                "publisher": "Kensington"
                            })
                            added_this_query += 1
                print(f"  -> Returned {len(docs)} books ({added_this_query} new unique romance books)")
        except Exception as e:
            print(f"  -> Error: {e}")

    print("\n" + "=" * 70)
    print(f"TOTAL NEW UNIQUE ROMANCE TITLES TO APPEND: {len(new_books)}")
    print("=" * 70)

    if not new_books:
        print("No new unique books to append.")
        return

    # Sort new books alphabetically
    new_books = sorted(new_books, key=lambda x: x['title'].lower())

    # Append to worksheet
    start_row = ws.max_row + 1
    for idx, b in enumerate(new_books, start_row):
        ws.cell(row=idx, column=1, value=b['title'])     # Name of Series / Book Title
        ws.cell(row=idx, column=2, value=b['author'])    # Author Name
        ws.cell(row=idx, column=3, value="Kensington")   # Publisher
        ws.cell(row=idx, column=4, value="N/A")          # GoodReads series link
        ws.cell(row=idx, column=5, value=1)              # Number of PRIMARY books
        ws.cell(row=idx, column=6, value="N/A")          # Rating (out of 5)
        ws.cell(row=idx, column=7, value="N/A")          # Ratings (#)
        ws.cell(row=idx, column=8, value="N/A")          # Synopsis
        ws.cell(row=idx, column=9, value="No")           # Romantasy Yes/No (Default No for general romance, updated by Step 2 GR classifier)
        ws.cell(row=idx, column=10, value="N/A")         # Romantasy Subgenre
        ws.cell(row=idx, column=11, value="N/A")         # Name of agent

    format_excel_sheet(ws)
    wb.save(CATALOG_FILE)

    print(f"\n>>> Successfully appended {len(new_books)} new Romance books!")
    print(f"    Previous Total Rows: {initial_row_count}")
    print(f"    New Total Catalog Rows: {ws.max_row}")
    print(f"    Updated File: {CATALOG_FILE}")

    print("\nSample appended Romance titles:")
    for b in new_books[:15]:
        print(f"  + '{b['title']}' by {b['author']}")

if __name__ == "__main__":
    fetch_and_append_romance()

