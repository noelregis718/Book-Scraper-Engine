import openpyxl
import re

CATALOG_FILE = r"E:\Internship\PocketFM\Kensington_Fantasy_Fiction_Catalog.xlsx"

target_books = [
    {"title": "A Sorcerer's Tail", "author": "Victor Konara"},
    {"title": "When the Tides Held the Moon", "author": "Venessa Vida Kelley"},
    {"title": "The Hollow Crown of Heaven", "author": "Karen Osborne"},
    {"title": "A Sanctuary of Beasts", "author": "Kalyn Josephson"},
    {"title": "The Memory Hunters", "author": "Mia Tsai"},
    {"title": "The Lost Unicorn", "author": "Sarah Maslin Nir"},
    {"title": "A Tongue so Sweet and Deadly", "author": "Sophia St. Germain"},
    {"title": "The Kingdom of Almonds", "author": "Ariel Kaplan"},
    {"title": "Duskbound", "author": "Bree Grenwich"},
    {"title": "The Wrath of the Fallen", "author": "Amber V. Nicole"}
]

wb = openpyxl.load_workbook(CATALOG_FILE, data_only=True)
ws = wb.active

print(f"Checking Catalog: {CATALOG_FILE}")
print(f"Sheet Name: {ws.title}")
print(f"Total Rows: {ws.max_row}\n")

# Store all rows
catalog_rows = []
for r in range(2, ws.max_row + 1):
    t = str(ws.cell(row=r, column=1).value or "").strip()
    a = str(ws.cell(row=r, column=2).value or "").strip()
    catalog_rows.append((r, t, a))

def clean(s):
    s = s.lower()
    s = re.sub(r'[:\-—\(].*$', '', s)
    s = re.sub(r'[^\w\s]', '', s)
    return re.sub(r'\s+', ' ', s).strip()

for idx, b in enumerate(target_books, 1):
    t_clean = clean(b["title"])
    a_clean = clean(b["author"])
    
    found_matches = []
    author_matches = []
    
    for r, t, a in catalog_rows:
        t_row_clean = clean(t)
        a_row_clean = clean(a)
        
        # Exact or close title match
        if t_clean == t_row_clean or (len(t_clean) > 4 and t_clean in t_row_clean):
            found_matches.append((r, t, a))
        # Author match
        elif any(part in a_row_clean for part in a_clean.split() if len(part) > 4):
            author_matches.append((r, t, a))
            
    print(f"{idx}. '{b['title']}' by {b['author']}:")
    if found_matches:
        for m in found_matches:
            print(f"   >>> FOUND at Row {m[0]}: Title: '{m[1]}' | Author: '{m[2]}'")
    else:
        print("   >>> NOT FOUND in Kensington Fantasy Fiction Catalog")
        if author_matches:
            for am in author_matches[:2]:
                print(f"       (Note: Other book by author found at Row {am[0]}: '{am[1]}' by {am[2]})")
    print()

wb.close()

