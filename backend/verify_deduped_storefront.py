import openpyxl

wb = openpyxl.load_workbook(r"E:\Internship\PocketFM\Kensington_Storefront_Fantasy_Catalog.xlsx", data_only=True)
ws = wb.active

print(f"Sheet Name: {ws.title}")
print(f"Total Rows: {ws.max_row} (Header + {ws.max_row - 1} data rows)")

cats = {}
for r in range(2, ws.max_row + 1):
    c = str(ws.cell(row=r, column=4).value or "Unknown")
    cats[c] = cats.get(c, 0) + 1

print("\n--- Remaining Unique Category Breakdown ---")
for cat, count in cats.items():
    print(f"  {cat}: {count} books")

wb.close()

