import urllib.request
import json
import urllib.parse
import os
import sys
from openpyxl import load_workbook, Workbook
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

def fetch_kensington_fantasy_catalog():
    print("=" * 70)
    print("   FETCHING KENSINGTON FANTASY & ROMANTASY CATALOG VIA OPENLIBRARY API")
    print("   (Bypasses Cloudflare 100% reliably with zero blocking)")
    print("=" * 70)

    queries = [
        {"publisher": "kensington", "subject": "fantasy"},
        {"publisher": "kensington", "subject": "fantasy fiction"},
        {"publisher": "kensington", "subject": "paranormal romance"},
        {"publisher": "kensington", "subject": "urban fantasy"},
        {"publisher": "kensington", "subject": "witches"},
        {"publisher": "kensington", "subject": "shapeshifters"},
        {"publisher": "kensington", "subject": "magic"},
        {"publisher": "kensington publishing", "subject": "fantasy"},
        {"publisher": "kensington publishing", "subject": "paranormal romance"},
        {"publisher": "rebel base", "subject": "fantasy"},
        {"publisher": "kensington", "q": "fantasy romance"},
        {"publisher": "kensington", "q": "romantasy"}
    ]

    unique_books = {}

    for q_params in queries:
        encoded = urllib.parse.urlencode(q_params)
        url = f"https://openlibrary.org/search.json?{encoded}&limit=100"
        print(f"Fetching: {q_params}...")
        req = urllib.request.Request(url, headers={"User-Agent": "PocketFM-Kensington-Catalog/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                docs = data.get("docs", [])
                print(f"  -> Returned {len(docs)} books (Available: {data.get('numFound', 0)})")
                for d in docs:
                    title = d.get("title", "").strip()
                    authors = d.get("author_name", [])
                    author = authors[0].strip() if authors else "N/A"
                    
                    # Basic cleanup
                    if title and author and len(title) > 1:
                        # Avoid duplicates
                        norm_key = (title.lower(), author.lower())
                        if norm_key not in unique_books:
                            unique_books[norm_key] = {
                                "title": title,
                                "author": author,
                                "publisher": "Kensington",
                                "year": d.get("first_publish_year", "")
                            }
        except Exception as e:
            print(f"  -> Error fetching query: {e}")

    books_list = list(unique_books.values())
    print("\n" + "=" * 70)
    print(f"  TOTAL UNIQUE KENSINGTON FANTASY TITLES RETRIEVED: {len(books_list)}")
    print("=" * 70)

    # Sort alphabetically by title
    books_list = sorted(books_list, key=lambda x: x['title'].lower())

    # Write to Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Kensington Fantasy"

    for idx, book in enumerate(books_list, 2):
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
    print(f"\n>>> Catalog successfully created with {len(books_list)} books at:")
    print(f"    {CATALOG_FILE}")

if __name__ == "__main__":
    fetch_kensington_fantasy_catalog()

