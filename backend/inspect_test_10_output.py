import openpyxl

wb = openpyxl.load_workbook(r"E:\Internship\PocketFM\Kensington_Storefront_Fantasy_Catalog.xlsx", data_only=True)
ws = wb.active

headers = [cell.value for cell in ws[1]]
print("Headers:", headers)
print("\n--- Populated Rows 2 to 11 ---")

for r in range(2, 12):
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
    
    print(f"\n[Row {r}] '{t}' by {a}")
    print(f"  GR Link:     {gr_url}")
    print(f"  Rating/Cnt:  {r_val} / {r_cnt}")
    print(f"  Books/Pages: {books} books | {pages} pages | Approx Hrs: {hrs}")
    print(f"  Genres:      {str(genres)[:60]}...")
    print(f"  Checker:     {checker}")

wb.close()

