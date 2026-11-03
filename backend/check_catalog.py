import openpyxl

wb = openpyxl.load_workbook(r"E:\Internship\PocketFM\Kensington_Fantasy_Fiction_Catalog.xlsx")
ws = wb.active
print(f"Active Sheet: {ws.title}")
print(f"Total Rows: {ws.max_row}")
print(f"Headers: {[c.value for c in ws[1]]}")
print("\nFirst 12 books in catalog:")
for r in range(2, 14):
    title = ws.cell(row=r, column=1).value
    author = ws.cell(row=r, column=2).value
    pub = ws.cell(row=r, column=3).value
    gr_link = ws.cell(row=r, column=4).value
    print(f"  Row {r}: '{title}' by {author} | Pub: {pub} | Link: {gr_link}")

