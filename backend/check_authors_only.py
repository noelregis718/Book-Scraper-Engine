import openpyxl

CATALOG_FILE = r"E:\Internship\PocketFM\Kensington_Fantasy_Fiction_Catalog.xlsx"
wb = openpyxl.load_workbook(CATALOG_FILE, data_only=True)
ws = wb.active

authors_to_check = [
    "Victor Konara",
    "Venessa Vida Kelley",
    "Karen Osborne",
    "Kalyn Josephson",
    "Mia Tsai",
    "Sarah Maslin Nir",
    "Sophia St. Germain",
    "Ariel Kaplan",
    "Bree Grenwich",
    "Parker Lennox",
    "Amber V. Nicole"
]

print("Author search in Kensington_Fantasy_Fiction_Catalog.xlsx:")
for auth in authors_to_check:
    matches = []
    for r in range(2, ws.max_row + 1):
        row_author = str(ws.cell(row=r, column=2).value or "").strip()
        row_title = str(ws.cell(row=r, column=1).value or "").strip()
        if auth.lower() in row_author.lower():
            matches.append((r, row_title, row_author))
    if matches:
        print(f"\n[FOUND] Author: {auth}")
        for m in matches:
            print(f"   Row {m[0]}: '{m[1]}' by {m[2]}")
    else:
        print(f"[NONE] Author: {auth} not in catalog")

wb.close()

