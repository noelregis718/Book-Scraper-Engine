import openpyxl

wb = openpyxl.load_workbook(r"E:\Internship\PocketFM\Kensington_Fantasy_Fiction_Catalog.xlsx")
ws = wb.active

farmer_matches = []
aiken_matches = []

for r in range(2, ws.max_row + 1):
    title = str(ws.cell(row=r, column=1).value or "").strip()
    author = str(ws.cell(row=r, column=2).value or "").strip()
    
    if "farmer" in title.lower():
        farmer_matches.append((r, title, author))
    if "aiken" in author.lower():
        aiken_matches.append((r, title, author))

print(f"=== 'Farmer' in Title Matches ({len(farmer_matches)}) ===")
for m in farmer_matches:
    print(f"  Row {m[0]}: '{m[1]}' by {m[2]}")

print(f"\n=== 'G. A. Aiken' Matches ({len(aiken_matches)}) ===")
for m in aiken_matches:
    print(f"  Row {m[0]}: '{m[1]}' by {m[2]}")

