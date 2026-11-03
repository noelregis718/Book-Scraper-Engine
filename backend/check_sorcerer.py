import openpyxl

wb = openpyxl.load_workbook(r"E:\Internship\PocketFM\Kensington_Storefront_Fantasy_Catalog.xlsx", data_only=True)
ws = wb.active

for r in range(2, ws.max_row + 1):
    t = str(ws.cell(row=r, column=1).value or "").lower()
    a = str(ws.cell(row=r, column=2).value or "").lower()
    if any(k in t or k in a for k in ["sorcerer", "tail", "konara", "victor"]):
        print(f"Row {r}: '{ws.cell(row=r, column=1).value}' by '{ws.cell(row=r, column=2).value}'")

