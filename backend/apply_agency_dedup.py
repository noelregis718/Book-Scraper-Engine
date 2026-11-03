import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import re

agency_file = r"E:\Internship\PocketFM\Kensington Agency.xlsx"
storefront_file = r"E:\Internship\PocketFM\Kensington_Storefront_Fantasy_Catalog.xlsx"

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

# 1. Load Agency Titles
wb_ag = openpyxl.load_workbook(agency_file, read_only=True)
ws_ag = wb_ag[wb_ag.sheetnames[0]]
agency_titles = set()
for row in ws_ag.iter_rows(min_row=2, values_only=True):
    if row and row[0]:
        norm = normalize_title(row[0])
        if norm:
            agency_titles.add(norm)
wb_ag.close()
print(f"Total Unique Normalized Titles in Kensington Agency: {len(agency_titles)}")

# 2. Load Storefront Catalog
wb_sf = openpyxl.load_workbook(storefront_file, data_only=True)
ws_sf = wb_sf.active

headers = [cell.value for cell in ws_sf[1]]
sf_rows = []
for r in range(2, ws_sf.max_row + 1):
    vals = [ws_sf.cell(row=r, column=c).value for c in range(1, len(headers) + 1)]
    if vals[0]:
        sf_rows.append(vals)
wb_sf.close()
print(f"Total Storefront Books before deduplication: {len(sf_rows)}")

# 3. Filter out overlapping titles
removed_books = []
unique_books = []

for r in sf_rows:
    norm = normalize_title(r[0])
    if norm in agency_titles:
        removed_books.append(r)
    else:
        unique_books.append(r)

print(f"Removed (Overlapping with Kensington Agency): {len(removed_books)}")
print(f"Retained (Unique to Storefront): {len(unique_books)}")

# 4. Save Cleaned Storefront Catalog
wb_out = openpyxl.Workbook()
ws_out = wb_out.active
ws_out.title = "Kensington Unique Storefront"
ws_out.views.sheetView[0].showGridLines = True

header_fill = PatternFill(start_color="006666", end_color="006666", fill_type="solid")
header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
data_font = Font(name="Segoe UI", size=10)
border_side = Side(border_style="thin", color="D3D3D3")
data_border = Border(left=border_side, right=border_side, top=border_side, bottom=border_side)

ws_out.row_dimensions[1].height = 28
for col_idx, h in enumerate(headers, 1):
    cell = ws_out.cell(row=1, column=col_idx, value=h)
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = data_border

for row_idx, r_vals in enumerate(unique_books, start=2):
    ws_out.row_dimensions[row_idx].height = 22
    for col_idx, val in enumerate(r_vals, 1):
        cell = ws_out.cell(row=row_idx, column=col_idx, value=val)
        cell.font = data_font
        cell.border = data_border
        if col_idx in [3, 4]:
            cell.alignment = Alignment(horizontal="center", vertical="center")
        else:
            cell.alignment = Alignment(horizontal="left", vertical="center")

for col in ws_out.columns:
    col_letter = get_column_letter(col[0].column)
    max_len = 0
    for cell in col:
        val_str = str(cell.value or '')
        if len(val_str) > 40:
            val_str = val_str[:40]
        max_len = max(max_len, len(val_str))
    ws_out.column_dimensions[col_letter].width = max(max_len + 4, 18)

ws_out.freeze_panes = "A2"
ws_out.auto_filter.ref = f"A1:{get_column_letter(len(headers))}{ws_out.max_row}"

wb_out.save(storefront_file)
print(f"Successfully updated: {storefront_file}")

