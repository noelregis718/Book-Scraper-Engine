import openpyxl

wb = openpyxl.load_workbook(r"E:\Internship\PocketFM\Kensington_Fantasy_Fiction_Catalog.xlsx")
ws = wb.active

print(f"Total Rows: {ws.max_row}")
print("\nSample rows from appended section (Row 274 to 282):")
for r in range(274, 283):
    t = ws.cell(row=r, column=1).value
    a = ws.cell(row=r, column=2).value
    p = ws.cell(row=r, column=3).value
    rom = ws.cell(row=r, column=9).value
    print(f"  Row {r}: '{t}' by {a} | Pub: {p} | Romantasy: {rom}")

print("\nSample rows from the end of the catalog (Row 426 to 434):")
for r in range(426, ws.max_row + 1):
    t = ws.cell(row=r, column=1).value
    a = ws.cell(row=r, column=2).value
    p = ws.cell(row=r, column=3).value
    rom = ws.cell(row=r, column=9).value
    print(f"  Row {r}: '{t}' by {a} | Pub: {p} | Romantasy: {rom}")

