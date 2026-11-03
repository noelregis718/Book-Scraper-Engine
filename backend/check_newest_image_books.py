import openpyxl
import re

target_books = [
    {"title": "Duskbound: Deluxe Limited Edition", "author": "Bree Grenwich, Parker Lennox"},
    {"title": "The Wrath of the Fallen: Deluxe Special Edition", "author": "Amber V. Nicole"},
    {"title": "The Wolf and His King: Deluxe Limited Edition", "author": "Finn Longman"},
    {"title": "Fallen Demon: Deluxe Limited Edition", "author": "Aurora Ascher"},
    {"title": "To the Rotting End: Deluxe Limited Edition", "author": "Sophia St. Germain"},
    {"title": "Keeper of the Grail: Deluxe Limited Edition", "author": "Paula Lafferty"},
    {"title": "Dawn of Chaos and Fury: Deluxe Special Edition", "author": "Melissa K. Roehrich"},
    {"title": "Riftborne: Deluxe Limited Edition", "author": "Bree Grenwich, Parker Lennox"},
    {"title": "The Fall of the Crowned King", "author": "Amber V. Nicole"},
    {"title": "The Once and Future Queen: Deluxe Limited Edition", "author": "Paula Lafferty"}
]

catalog_file = r"E:\Internship\PocketFM\Kensington_Storefront_Fantasy_Catalog.xlsx"
wb = openpyxl.load_workbook(catalog_file, data_only=True)
ws = wb.active

print(f"Catalog: {catalog_file}")
print(f"Total Rows: {ws.max_row} (Header + {ws.max_row - 1} data rows)\n")

rows = []
for r in range(2, ws.max_row + 1):
    t = str(ws.cell(row=r, column=1).value or "").strip()
    a = str(ws.cell(row=r, column=2).value or "").strip()
    cat = str(ws.cell(row=r, column=4).value or "").strip()
    url = str(ws.cell(row=r, column=5).value or "").strip()
    rows.append((r, t, a, cat, url))

def clean(s):
    if not s: return ""
    s = str(s).lower()
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r'[:\-—\(].*$', '', s)
    s = re.sub(r'[^\w\s]', '', s)
    for art in ['the ', 'a ', 'an ']:
        if s.startswith(art):
            s = s[len(art):]
            break
    return re.sub(r'\s+', ' ', s).strip()

print("=" * 80)
print("CHECKING 10 BOOKS FROM UPLOADED IMAGE:")
print("=" * 80)

found_count = 0
for idx, b in enumerate(target_books, 1):
    t_clean = clean(b["title"])
    a_clean = clean(b["author"])
    authors = [clean(x) for x in b["author"].replace("&", ",").split(",")]
    
    matches = []
    author_matches = []
    
    for r, t, a, cat, url in rows:
        t_row_clean = clean(t)
        a_row_clean = clean(a)
        
        # Check title match
        if t_clean == t_row_clean or (len(t_clean) > 4 and (t_clean in t_row_clean or t_row_clean in t_clean)):
            matches.append((r, t, a, cat, url))
        elif any(part in a_row_clean for part in a_clean.split() if len(part) > 3):
            author_matches.append((r, t, a, cat, url))
            
    if matches:
        found_count += 1
        m_str = ", ".join([f"Row {m[0]}: '{m[1]}' by {m[2]} [{m[3]}]" for m in matches])
        print(f"{idx}. '{b['title']}' by {b['author']} -> [FOUND] {m_str}")
    else:
        a_info = f" (Author found at Row {author_matches[0][0]} '{author_matches[0][1]}')" if author_matches else ""
        print(f"{idx}. '{b['title']}' by {b['author']} -> [NOT FOUND]{a_info}")

print(f"\nTotal Image Books Found: {found_count} / {len(target_books)}")

