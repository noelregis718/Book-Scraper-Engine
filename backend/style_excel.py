import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

file_path = 'Next_Agency.xlsx'

try:
    print("Loading workbook...")
    wb = openpyxl.load_workbook(file_path)
    ws = wb.active
    
    # 1. Define Styles
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")  # A nice professional blue
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    
    cell_alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
    
    thin_border = Border(left=Side(style='thin', color='D3D3D3'), 
                         right=Side(style='thin', color='D3D3D3'), 
                         top=Side(style='thin', color='D3D3D3'), 
                         bottom=Side(style='thin', color='D3D3D3'))

    print("Applying styles to cells...")
    # 2. Iterate through rows and apply formatting
    for row in ws.iter_rows():
        for cell in row:
            # Apply border to all cells
            cell.border = thin_border
            
            # Formatting for the header row
            if cell.row == 1:
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment
            # Formatting for data rows
            else:
                cell.alignment = cell_alignment

    # 3. Freeze the top row so it stays visible when scrolling
    ws.freeze_panes = 'A2'
    
    print("Adjusting column widths...")
    # 4. Auto-adjust column widths (with a maximum cap so the Synopsis column isn't insanely wide)
    for col_cells in ws.columns:
        max_length = 0
        col_letter = col_cells[0].column_letter
        
        # Sample the first 100 rows to find a good width (faster than checking all)
        for cell in col_cells[:100]:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))
                
        # Set a minimum width of 12 and maximum width of 60
        adjusted_width = min(max(max_length + 2, 12), 60)
        ws.column_dimensions[col_letter].width = adjusted_width

    # Save the updated file
    print("Saving workbook...")
    wb.save(file_path)
    print("Excel file successfully styled!")
    
except Exception as e:
    print(f"Error styling the Excel file: {e}")
