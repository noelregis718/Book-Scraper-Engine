import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import os

file_path = r'e:\Internship\PocketFM\romantasy_authors.xlsx'

if not os.path.exists(file_path):
    print("File not found.")
    exit(1)

wb = load_workbook(file_path)
ws = wb.active

# Define styles
header_font = Font(bold=True, color="FFFFFF")
header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
center_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
left_wrap_alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
thin_border = Border(left=Side(style='thin'), right=Side(style='thin'),
                     top=Side(style='thin'), bottom=Side(style='thin'))

# Apply styles to header
for cell in ws[1]:
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = center_alignment
    cell.border = thin_border

# Apply styles to data rows
for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
    for cell in row:
        cell.border = thin_border
        
        # Determine alignment based on column
        col_letter = get_column_letter(cell.column)
        if col_letter in ['A', 'D', 'H']: # Series name, Link, Synopsis are often long
            cell.alignment = left_wrap_alignment
        else:
            cell.alignment = center_alignment

# Set column widths
ws.column_dimensions['A'].width = 35 # Series
ws.column_dimensions['B'].width = 20 # Author
ws.column_dimensions['C'].width = 25 # Publisher
ws.column_dimensions['D'].width = 40 # Goodreads link
ws.column_dimensions['E'].width = 15 # Primary books
ws.column_dimensions['F'].width = 15 # Rating
ws.column_dimensions['G'].width = 15 # Ratings #
ws.column_dimensions['H'].width = 75 # Synopsis
ws.column_dimensions['I'].width = 15 # Romantasy Yes/No
ws.column_dimensions['J'].width = 30 # Sub-genre
ws.column_dimensions['K'].width = 20 # Agent

# Freeze top row
ws.freeze_panes = 'A2'

wb.save(file_path)
print("Styling applied successfully")
