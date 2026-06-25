import openpyxl

wb = openpyxl.load_workbook('e:/Internship/PocketFM/template.xlsx')
ws = wb.active

for row in ws.iter_rows():
    for cell in row:
        if str(cell.value) == '-242' or '242' in str(cell.value):
            print(f"Cell {cell.coordinate} has value: {repr(cell.value)}, type: {type(cell.value)}")
        if 'not reached' in str(cell.value).lower() and '-' in str(cell.value):
            print(f"Cell {cell.coordinate} has value: {repr(cell.value)}, type: {type(cell.value)}")
