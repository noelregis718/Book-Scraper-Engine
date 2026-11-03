import openpyxl

wb = openpyxl.load_workbook(r"E:\Internship\PocketFM\Kensington_Fantasy_Fiction_Catalog.xlsx")
ws = wb.active

print(f"Total Rows: {ws.max_row}")
print(f"Total Columns: {ws.max_column}")
print(f"Headers: {[c.value for c in ws[1]]}")

print("\nSample rows around the append boundary (Row 433 to 440):")
for r in range(433, 441):
    t = ws.cell(row=r, column=1).value
    a = ws.cell(row=r, column=2).value
    p = ws.cell(row=r, column=3).value
    rom = ws.cell(row=r, column=9).value
    print(f"  Row {r}: '{t}' by {a} | Pub: {p} | Romantasy: {rom}")

print("\nSample rows near the end of the catalog (Row 1225 to 1232):")
for r in range(1225, ws.max_row + 1):
    t = ws.cell(row=r, column=1).value
    a = ws.cell(row=r, column=2).value
    p = ws.cell(row=r, column=3).value
    rom = ws.cell(row=r, column=9).value
    print(f"  Row {r}: '{t}' by {a} | Pub: {p} | Romantasy: {rom}")

