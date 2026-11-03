import openpyxl

wb = openpyxl.load_workbook(r"E:\Internship\PocketFM\Kensington_Storefront_Fantasy_Catalog.xlsx", data_only=True)
ws = wb.active

print(f"Sheet Name: {ws.title}")
print(f"Total Rows: {ws.max_row} (Header + {ws.max_row - 1} data rows)")
print(f"Headers: {[cell.value for cell in ws[1]]}")

cats = {}
for r in range(2, ws.max_row + 1):
    c = str(ws.cell(row=r, column=4).value or "Unknown")
    cats[c] = cats.get(c, 0) + 1

print("\n--- Category Breakdown ---")
for cat, count in cats.items():
    print(f"  {cat}: {count} books")

print("\n--- First 3 Fantasy Rows ---")
for r in range(2, 5):
    print(f"Row {r}: '{ws.cell(row=r, column=1).value}' by '{ws.cell(row=r, column=2).value}' | Cat: {ws.cell(row=r, column=4).value}")

print("\n--- First 3 Romance Rows (Starting Row 322) ---")
for r in range(322, 325):
    print(f"Row {r}: '{ws.cell(row=r, column=1).value}' by '{ws.cell(row=r, column=2).value}' | Cat: {ws.cell(row=r, column=4).value}")

print("\n--- Last 3 Romance Rows ---")
for r in range(ws.max_row - 2, ws.max_row + 1):
    print(f"Row {r}: '{ws.cell(row=r, column=1).value}' by '{ws.cell(row=r, column=2).value}' | Cat: {ws.cell(row=r, column=4).value}")

wb.close()

