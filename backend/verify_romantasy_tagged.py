import openpyxl

wb = openpyxl.load_workbook(r"E:\Internship\PocketFM\Kensington_Storefront_Fantasy_Catalog.xlsx", data_only=True)
ws = wb.active

cats = {}
for r in range(2, ws.max_row + 1):
    c = str(ws.cell(row=r, column=4).value or "Unknown")
    cats[c] = cats.get(c, 0) + 1

print(f"Total Rows: {ws.max_row} (Header + {ws.max_row - 1} books)")
print("\n--- Category Breakdown ---")
for cat, count in cats.items():
    print(f"  {cat}: {count} books")

print("\n--- First 5 Romantasy-Tagged Books ---")
found = 0
for r in range(2, ws.max_row + 1):
    c = str(ws.cell(row=r, column=4).value or "")
    if "Romantasy" in c:
        found += 1
        print(f"Row {r}: '{ws.cell(row=r, column=1).value}' by '{ws.cell(row=r, column=2).value}' | Tag: {c}")
        if found >= 5:
            break

wb.close()

