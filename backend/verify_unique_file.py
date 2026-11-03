import openpyxl

wb = openpyxl.load_workbook(r"E:\Internship\PocketFM\Kensington_Unique_Fantasy_Fiction_Catalog.xlsx")
ws = wb.active

print(f"Sheet Name: {ws.title}")
print(f"Total Rows: {ws.max_row}")
print(f"Headers: {[c.value for c in ws[1]]}")

print("\nSample rows (Row 2 to 10):")
for r in range(2, 11):
    t = ws.cell(row=r, column=1).value
    a = ws.cell(row=r, column=2).value
    p = ws.cell(row=r, column=3).value
    rom = ws.cell(row=r, column=9).value
    print(f"  Row {r}: '{t}' by {a} | Pub: {p} | Romantasy: {rom}")

print("\nSample rows from the end (Row 895 to 903):")
for r in range(895, ws.max_row + 1):
    t = ws.cell(row=r, column=1).value
    a = ws.cell(row=r, column=2).value
    p = ws.cell(row=r, column=3).value
    rom = ws.cell(row=r, column=9).value
    print(f"  Row {r}: '{t}' by {a} | Pub: {p} | Romantasy: {rom}")

