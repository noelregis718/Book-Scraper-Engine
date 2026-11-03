import openpyxl

wb = openpyxl.load_workbook(r"E:\Internship\PocketFM\Kensington_Storefront_Fantasy_Catalog.xlsx", data_only=True)
ws = wb.active

print(f"Sheet Name: {ws.title}")
print(f"Total Rows: {ws.max_row} (Header + {ws.max_row - 1} books)")

books_to_check = [
    "A Sorcerer's Tail",
    "When the Tides Held the Moon",
    "The Hollow Crown of Heaven",
    "A Sanctuary of Beasts",
    "The Memory Hunters",
    "The Lost Unicorn",
    "A Tongue so Sweet and Deadly",
    "The Kingdom of Almonds",
    "Duskbound",
    "The Wrath of the Fallen"
]

all_rows = []
for r in range(2, ws.max_row + 1):
    title = str(ws.cell(row=r, column=1).value or "").strip()
    author = str(ws.cell(row=r, column=2).value or "").strip()
    all_rows.append((r, title, author))

print("\n--- Checking the 10 Image Books in the Newly Scraped Catalog ---")
found_count = 0
for b in books_to_check:
    clean_b = b.lower().replace("the ", "").replace("a ", "").replace("'", "")
    matches = [m for m in all_rows if clean_b in m[1].lower().replace("the ", "").replace("a ", "").replace("'", "")]
    if matches:
        found_count += 1
        for m in matches:
            print(f"[FOUND] '{b}' -> Row {m[0]}: '{m[1]}' by {m[2]}")
    else:
        print(f"[NOT FOUND] '{b}'")

print(f"\nTotal Image Books Found: {found_count} / {len(books_to_check)}")

print("\n--- First 5 rows in the new catalog ---")
for r in range(2, 7):
    row_vals = [ws.cell(row=r, column=c).value for c in range(1, 8)]
    print(f"Row {r}: '{row_vals[0]}' by {row_vals[1]} | {row_vals[2]} | {row_vals[4][:45]}...")

