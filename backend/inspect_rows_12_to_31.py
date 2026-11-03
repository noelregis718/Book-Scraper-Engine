import openpyxl

wb = openpyxl.load_workbook(r"E:\Internship\PocketFM\Kensington_Storefront_Fantasy_Catalog.xlsx", data_only=True)
ws = wb.active

print(f"Total Rows: {ws.max_row}\n")

for r in range(12, 32):
    t = ws.cell(row=r, column=1).value
    a = ws.cell(row=r, column=2).value
    gr_url = ws.cell(row=r, column=8).value
    r_val = ws.cell(row=r, column=9).value
    r_cnt = ws.cell(row=r, column=10).value
    books = ws.cell(row=r, column=11).value
    pages = ws.cell(row=r, column=12).value
    hrs = ws.cell(row=r, column=13).value
    genres = ws.cell(row=r, column=14).value
    checker = ws.cell(row=r, column=16).value
    
    print(f"[Row {r}] '{t}' by {a}")
    print(f"  GR URL:      {gr_url}")
    print(f"  Rating/#:    {r_val} / {r_cnt}")
    print(f"  Books/Pages: {books} books | {pages} pages | Length: {hrs} hrs")
    print(f"  Checker:     {checker}")
    print("-" * 50)

wb.close()

