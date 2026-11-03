with open(r"backend/mega_goodreads_scraper.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update target file and defaults
old_config = '''EXCEL_FILE = r"e:\\Internship\\PocketFM\\KF Literary Scouts Series .xlsx"
SHEET_NAME = "GR data populated sheet"
START_ROW = 33
TARGET_ROWS = 48
CONCURRENCY = 2
BATCH_SIZE = 30'''

new_config = '''import argparse
import sys

EXCEL_FILE = r"E:\\Internship\\PocketFM\\Kensington_Storefront_Fantasy_Catalog.xlsx"
SHEET_NAME = "Kensington Unique Storefront"
START_ROW = 0
TARGET_ROWS = 10
CONCURRENCY = 2
BATCH_SIZE = 10'''

content = content.replace(old_config.replace('\n', '\r\n'), new_config.replace('\n', '\r\n'))
if new_config not in content and old_config in content:
    content = content.replace(old_config, new_config)

# 2. Support 'Book Title'
old_book_name = 'book_name = str(row.get("Book Name", row.get("Series Name", ""))).strip()'
new_book_name = 'book_name = str(row.get("Book Title", row.get("Book Name", row.get("Series Name", "")))).strip()'
content = content.replace(old_book_name, new_book_name)

# 3. Support 'Goodreads Synopsis'
old_syn = 'df.at[index, "Synopsis"] = (await desc_el.inner_text()).strip()'
new_syn = '''syn_text = (await desc_el.inner_text()).strip()
            if "Goodreads Synopsis" in df.columns:
                df.at[index, "Goodreads Synopsis"] = syn_text
            elif "Synopsis" in df.columns:
                df.at[index, "Synopsis"] = syn_text'''
content = content.replace(old_syn, new_syn)

# 4. Support CLI args and Kensington styling
old_run = '''async def run_scraper():
    print(f"Loading {EXCEL_FILE}...")'''

new_run = '''def apply_kensington_styling(filepath, sheet_name):
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    try:
        wb = openpyxl.load_workbook(filepath)
        ws = wb[sheet_name] if sheet_name in wb.sheetnames else wb.active
        ws.views.sheetView[0].showGridLines = True
        
        header_fill = PatternFill(start_color="006666", end_color="006666", fill_type="solid")
        header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
        data_font = Font(name="Segoe UI", size=10)
        border_side = Side(border_style="thin", color="D3D3D3")
        data_border = Border(left=border_side, right=border_side, top=border_side, bottom=border_side)
        
        ws.row_dimensions[1].height = 28
        for col_idx in range(1, ws.max_column + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = data_border
            
        for row_idx in range(2, ws.max_row + 1):
            ws.row_dimensions[row_idx].height = 22
            for col_idx in range(1, ws.max_column + 1):
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.font = data_font
                cell.border = data_border
                header_name = str(ws.cell(row=1, column=col_idx).value or "")
                if header_name in ["Publisher", "Category", "Romantasy Checker"]:
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                elif header_name in ["Book1_Rating", "Book1_Num_Ratings", "Num_Primary_Books_in_Series", "Total_Page_Count_of_Primary_Books", "Approx Length (Hrs)"]:
                    cell.alignment = Alignment(horizontal="right", vertical="center")
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
        ws.auto_filter.ref = f"A1:{get_column_letter(ws.max_column)}{ws.max_row}"
        wb.save(filepath)
        wb.close()
        print(f"Applied Kensington styling to {filepath}")
    except Exception as e:
        print(f"Styling note: {e}")

async def run_scraper():
    global START_ROW, TARGET_ROWS
    parser = argparse.ArgumentParser(description="Mega Goodreads Scraper")
    parser.add_argument("--start", type=int, default=START_ROW, help="Start row index (0-based)")
    parser.add_argument("--target", type=int, default=TARGET_ROWS, help="Target end row index")
    args, unknown = parser.parse_known_args()
    START_ROW = args.start
    TARGET_ROWS = args.target

    print(f"Loading {EXCEL_FILE} (Rows {START_ROW} to {TARGET_ROWS})...")'''

content = content.replace(old_run, new_run)

# Also update the final styling call
content = content.replace('format_excel.apply_styling(EXCEL_FILE)', 'apply_kensington_styling(EXCEL_FILE, SHEET_NAME)')

with open(r"backend/mega_goodreads_scraper.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated backend/mega_goodreads_scraper.py successfully!")

