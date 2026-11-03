import openpyxl

catalog_file = r"E:\Internship\PocketFM\Kensington_Storefront_Fantasy_Catalog.xlsx"
wb = openpyxl.load_workbook(catalog_file, data_only=True)
ws = wb.active

print(f"Sheet Name: {ws.title}")
print(f"Total Rows: {ws.max_row} (Header + {ws.max_row - 1} data rows)")
print(f"Total Columns: {ws.max_column}")

print("\n--- Current All 16 Headers ---")
for idx, cell in enumerate(ws[1], 1):
    print(f"Col {idx}: {cell.value}")

print("\n--- Sample Row 2 (First book) ---")
for idx in range(1, ws.max_column + 1):
    print(f"  Col {idx} ({ws.cell(row=1, column=idx).value}): {ws.cell(row=2, column=idx).value}")

wb.close()

