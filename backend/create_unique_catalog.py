import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import re

OUTPUT_FILE = r"E:\Internship\PocketFM\Kensington_Unique_Fantasy_Fiction_Catalog.xlsx"

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

def normalize_title(t):
    if not t:
        return ""
    t = str(t).strip().lower()
    t = re.sub(r'^[\'"“‘\s]+|[\'"”’\s]+$', '', t)
    t = re.sub(r'\s+', ' ', t)
    return t

def format_excel_sheet(ws):
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

def create_unique_catalog():
    # 1. Load Agency and Old List titles
    wb_agency = openpyxl.load_workbook("Kensington Agency.xlsx", read_only=True)
    agency_titles = {normalize_title(r[0]) for r in wb_agency[wb_agency.sheetnames[0]].iter_rows(min_row=2, values_only=True) if r and r[0]}
    wb_agency.close()

    wb_old = openpyxl.load_workbook("Kensington Old List.xlsx", read_only=True)
    old_titles = {normalize_title(r[0]) for r in wb_old[wb_old.sheetnames[0]].iter_rows(min_row=2, values_only=True) if r and r[0]}
    wb_old.close()

    existing_titles = agency_titles | old_titles
    print(f"Total existing titles to exclude: {len(existing_titles)}")

    # 2. Filter new catalog for unique ones
    wb_new = openpyxl.load_workbook("Kensington_Fantasy_Fiction_Catalog.xlsx", data_only=True)
    ws_new = wb_new[wb_new.sheetnames[0]]

    unique_books = []
    seen_unique = set()
    doubles_found = []

    for r_idx, row in enumerate(ws_new.iter_rows(min_row=2, values_only=True), start=2):
        if not row or not row[0]:
            continue
        title = str(row[0]).strip()
        norm = normalize_title(title)

        if norm in existing_titles:
            doubles_found.append((r_idx, title, str(row[1])))
        else:
            if norm not in seen_unique:
                seen_unique.add(norm)
                unique_books.append(row)

    wb_new.close()

    print(f"Total doubles found (already in Old List / Agency): {len(doubles_found)}")
    print(f"Total unique books to write: {len(unique_books)}")

    # 3. Create New Workbook
    wb_out = openpyxl.Workbook()
    ws_out = wb_out.active
    ws_out.title = "Unique Kensington Catalog"

    for r_idx, row_data in enumerate(unique_books, start=2):
        for c_idx in range(len(HEADERS)):
            val = row_data[c_idx] if c_idx < len(row_data) else "N/A"
            ws_out.cell(row=r_idx, column=c_idx + 1, value=val)

    format_excel_sheet(ws_out)
    wb_out.save(OUTPUT_FILE)
    print(f"\n>>> Successfully created: {OUTPUT_FILE}")
    print(f"    Rows: {ws_out.max_row} (Header + {len(unique_books)} unique titles)")

if __name__ == "__main__":
    create_unique_catalog()

