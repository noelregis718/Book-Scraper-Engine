import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

catalog_file = r"E:\Internship\PocketFM\Kensington_Storefront_Fantasy_Catalog.xlsx"

print(f"Loading {catalog_file}...")
wb = openpyxl.load_workbook(catalog_file)
ws = wb.active

current_headers = [cell.value for cell in ws[1] if cell.value]
print(f"Current Headers ({len(current_headers)}): {current_headers}")

new_columns = [
    "GoodReads_Series_URL",
    "Book1_Rating",
    "Book1_Num_Ratings",
    "Num_Primary_Books_in_Series",
    "Total_Page_Count_of_Primary_Books",
    "Approx Length (Hrs)",
    "Genre Tags",
    "Goodreads Synopsis",
    "Romantasy Checker"
]

# Check which ones are missing
columns_to_add = [c for c in new_columns if c not in current_headers]
print(f"Columns to Add ({len(columns_to_add)}): {columns_to_add}")

if not columns_to_add:
    print("All columns already present!")
else:
    header_fill = PatternFill(start_color="006666", end_color="006666", fill_type="solid")
    header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    data_font = Font(name="Segoe UI", size=10)
    border_side = Side(border_style="thin", color="D3D3D3")
    data_border = Border(left=border_side, right=border_side, top=border_side, bottom=border_side)
    
    start_col = len(current_headers) + 1
    
    # Add new column headers
    ws.row_dimensions[1].height = 28
    for idx, col_name in enumerate(columns_to_add):
        col_num = start_col + idx
        cell = ws.cell(row=1, column=col_num, value=col_name)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = data_border
        
    # Format all data rows for the new columns
    for row_idx in range(2, ws.max_row + 1):
        ws.row_dimensions[row_idx].height = 22
        for idx in range(len(columns_to_add)):
            col_num = start_col + idx
            cell = ws.cell(row=row_idx, column=col_num)
            cell.font = data_font
            cell.border = data_border
            
            # Numeric alignment for ratings, books, pages, hours
            col_name = columns_to_add[idx]
            if col_name in ["Book1_Rating", "Book1_Num_Ratings", "Num_Primary_Books_in_Series", "Total_Page_Count_of_Primary_Books", "Approx Length (Hrs)"]:
                cell.alignment = Alignment(horizontal="right", vertical="center")
            elif col_name in ["Romantasy Checker"]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")

    total_cols = len(current_headers) + len(columns_to_add)
    
    # Auto-adjust column widths
    for col_idx in range(1, total_cols + 1):
        col_letter = get_column_letter(col_idx)
        max_len = 0
        for cell in ws[col_letter]:
            val_str = str(cell.value or '')
            if len(val_str) > 40:
                val_str = val_str[:40]
            max_len = max(max_len, len(val_str))
        ws.column_dimensions[col_letter].width = max(max_len + 4, 18)
        
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{get_column_letter(total_cols)}{ws.max_row}"
    ws.views.sheetView[0].showGridLines = True
    
    wb.save(catalog_file)
    print(f"Successfully added {len(columns_to_add)} columns to {catalog_file}!")

wb.close()

