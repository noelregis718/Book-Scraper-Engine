import openpyxl
import re

target_books = [
    # Image 1
    {"title": "A Promise so Bold and Broken: Deluxe Limited Edition", "author": "Sophia St. Germain", "image": 1},
    {"title": "The Dreadfuls: Deluxe Stenciled Edges", "author": "A. Rae Dunlap", "image": 1},
    {"title": "Swamp Music", "author": "Emily Carpenter", "image": 1},
    {"title": "Still Rich and Rotten", "author": "Jahquel J", "image": 1},
    {"title": "In the Market for You", "author": "Nadia Chandinie", "image": 1},
    {"title": "Endless Summer: Deluxe Limited Edition", "author": "Lena Hendrix", "image": 1},
    {"title": "The Library of Amorlin: Deluxe Limited Edition", "author": "Kalyn Josephson", "image": 1},
    {"title": "Hush Hush: Deluxe Limited Edition", "author": "Shain Rose", "image": 1},
    {"title": "Teach the Torches to Burn", "author": "Christina Dodd", "image": 1},
    {"title": "The Getaway Inn", "author": "Lori Foster", "image": 1},
    
    # Image 2
    {"title": "The Determined", "author": "Rachel Rueckert", "image": 2},
    {"title": "Behind Closed Doors: Deluxe Limited Edition", "author": "Shain Rose", "image": 2},
    {"title": "In Her Spotlight", "author": "Amy Spalding", "image": 2},
    {"title": "Lonesome Ridge", "author": "Maisey Yates", "image": 2},
    {"title": "Dragon Magic", "author": "Alexandra Ivy", "image": 2},
    {"title": "Her Soul for Revenge: Deluxe Special Edition", "author": "Harley Laroux", "image": 2},
    {"title": "Lie for a Million", "author": "Janet Dailey", "image": 2},
    {"title": "No Safe Secret", "author": "Fern Michaels", "image": 2},
    {"title": "Big Name Fan", "author": "Annie Mare, Ruthie Knox", "image": 2},
    {"title": "Alcott Hall: Deluxe Limited Edition", "author": "Emily Rath", "image": 2}
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
    rows.append((r, t, a, cat))

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

results = []

for idx, b in enumerate(target_books, 1):
    t_clean = clean(b["title"])
    a_clean = clean(b["author"])
    authors = [clean(x) for x in b["author"].replace("&", ",").split(",")]
    
    matches = []
    author_matches = []
    
    for r, t, a, cat in rows:
        t_row_clean = clean(t)
        a_row_clean = clean(a)
        
        # Check title match
        if t_clean == t_row_clean or (len(t_clean) > 4 and (t_clean in t_row_clean or t_row_clean in t_clean)):
            matches.append((r, t, a, cat))
        elif any(part in a_row_clean for part in a_clean.split() if len(part) > 3):
            author_matches.append((r, t, a, cat))
            
    results.append({
        "num": idx,
        "image": b["image"],
        "target_title": b["title"],
        "target_author": b["author"],
        "matches": matches,
        "author_matches": author_matches
    })

print("=" * 80)
print("IMAGE 1 RESULTS:")
print("=" * 80)
for r in results[:10]:
    if r["matches"]:
        m_str = ", ".join([f"Row {m[0]}: '{m[1]}' by {m[2]} [{m[3]}]" for m in r["matches"]])
        print(f"{r['num']}. '{r['target_title']}' by {r['target_author']} -> [FOUND] {m_str}")
    else:
        a_info = f" (Author found at Row {r['author_matches'][0][0]} '{r['author_matches'][0][1]}')" if r['author_matches'] else ""
        print(f"{r['num']}. '{r['target_title']}' by {r['target_author']} -> [NOT FOUND]{a_info}")

print("\n" + "=" * 80)
print("IMAGE 2 RESULTS:")
print("=" * 80)
for r in results[10:]:
    if r["matches"]:
        m_str = ", ".join([f"Row {m[0]}: '{m[1]}' by {m[2]} [{m[3]}]" for m in r["matches"]])
        print(f"{r['num']}. '{r['target_title']}' by {r['target_author']} -> [FOUND] {m_str}")
    else:
        a_info = f" (Author found at Row {r['author_matches'][0][0]} '{r['author_matches'][0][1]}')" if r['author_matches'] else ""
        print(f"{r['num']}. '{r['target_title']}' by {r['target_author']} -> [NOT FOUND]{a_info}")

