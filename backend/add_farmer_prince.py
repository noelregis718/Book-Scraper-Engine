import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

CATALOG_FILE = r"E:\Internship\PocketFM\Kensington_Fantasy_Fiction_Catalog.xlsx"

wb = openpyxl.load_workbook(CATALOG_FILE)
ws = wb.active

new_books = [
    ("The Farmer Prince", "G. A. Aiken", "Kensington"),
    ("The Blacksmith Queen", "G. A. Aiken", "Kensington"),
    ("The Heretic Royal", "G. A. Aiken", "Kensington"),
    ("How to Drive a Dragon Crazy", "G. A. Aiken", "Kensington"),
    ("Feel the Burn", "G. A. Aiken", "Kensington"),
    ("Bring the Heat", "G. A. Aiken", "Kensington")
]

# Check existing titles
existing_titles = set()
for r in range(2, ws.max_row + 1):
    val = ws.cell(row=r, column=1).value
    if val:
        existing_titles.add(str(val).strip().lower())

added_count = 0
for title, author, pub in new_books:
    if title.lower() not in existing_titles:
        next_row = ws.max_row + 1
        ws.cell(row=next_row, column=1, value=title)
        ws.cell(row=next_row, column=2, value=author)
        ws.cell(row=next_row, column=3, value=pub)
        ws.cell(row=next_row, column=4, value="N/A")
        ws.cell(row=next_row, column=5, value=1)
        ws.cell(row=next_row, column=6, value="N/A")
        ws.cell(row=next_row, column=7, value="N/A")
        ws.cell(row=next_row, column=8, value="N/A")
        ws.cell(row=next_row, column=9, value="No")
        ws.cell(row=next_row, column=10, value="N/A")
        ws.cell(row=next_row, column=11, value="N/A")
        existing_titles.add(title.lower())
        added_count += 1
        print(f"Added Row {next_row}: '{title}' by {author}")

# Re-apply styling
header_fill = PatternFill(start_color="006666", end_color="006666", fill_type="solid")
header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
data_font = Font(name="Segoe UI", size=10)
border_side = Side(border_style="thin", color="D3D3D3")
data_border = Border(left=border_side, right=border_side, top=border_side, bottom=border_side)

for row_idx in range(2, ws.max_row + 1):
    ws.row_dimensions[row_idx].height = 20
    for col_idx in range(1, 12):
        cell = ws.cell(row=row_idx, column=col_idx)
        cell.border = data_border
        cell.font = data_font
        if col_idx in [5, 6, 7]:
            cell.alignment = Alignment(horizontal="right", vertical="center")
        elif col_idx in [3, 9, 10]:
            cell.alignment = Alignment(horizontal="center", vertical="center")
        else:
            cell.alignment = Alignment(horizontal="left", vertical="center")

ws.auto_filter.ref = f"A1:K{ws.max_row}"
wb.save(CATALOG_FILE)
print(f"Successfully added {added_count} books. Total catalog rows: {ws.max_row}")

