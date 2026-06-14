import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

EXCEL_FILE = "e:/Internship/PocketFM/books_from_images.xlsx"

def style_excel():
    wb = load_workbook(EXCEL_FILE)
    ws = wb.active

    # Define styles
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
    center_aligned_text = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left_aligned_text = Alignment(horizontal="left", vertical="top", wrap_text=True)
    thin_border = Border(left=Side(style='thin'), 
                         right=Side(style='thin'), 
                         top=Side(style='thin'), 
                         bottom=Side(style='thin'))

    # Style the header row
    for cell in ws[1]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_aligned_text
        cell.border = thin_border

    # Style data rows and auto-adjust column widths
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter # Get the column name
        
        for cell in col:
            # Set alignment and borders for all cells
            if cell.row != 1:
                if col[0].value in ["Synopsis (if available)", "GoodReads series link"]:
                    cell.alignment = left_aligned_text
                else:
                    cell.alignment = center_aligned_text
                cell.border = thin_border
            
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        
        # Set a reasonable max width for columns
        adjusted_width = (max_length + 2)
        if adjusted_width > 50:
            adjusted_width = 50
        ws.column_dimensions[column].width = adjusted_width

    wb.save(EXCEL_FILE)
    print("Excel file styled successfully!")

if __name__ == "__main__":
    style_excel()
