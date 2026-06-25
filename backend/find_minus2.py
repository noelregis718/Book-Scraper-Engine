import openpyxl

wb = openpyxl.load_workbook('e:/Internship/PocketFM/template.xlsx')
ws = wb.active

for row in ws.iter_rows():
    for cell in row:
        if cell.value and isinstance(cell.value, str) and '-' in cell.value:
            print(f"Cell {cell.coordinate} has minus sign: {repr(cell.value)}")
