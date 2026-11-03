import openpyxl

wb = openpyxl.load_workbook(r"E:\Internship\PocketFM\Kensington_Unique_Fantasy_Fiction_Catalog.xlsx", data_only=True)
ws = wb.active

enriched = 0
for r in range(2, ws.max_row + 1):
    link = ws.cell(row=r, column=4).value
    if link and str(link).strip() and str(link).strip().lower() not in ["n/a", "none", "nan"]:
        enriched += 1
        if enriched <= 5:
            print(f"Row {r}: '{ws.cell(row=r, column=1).value}' -> {link}")

print(f"Total enriched so far: {enriched} / {ws.max_row - 1}")
wb.close()

