import openpyxl
import re

new_books = [
    {"title": "Eden's Fire", "author": "Samantha Holt"},
    {"title": "Dark Promise", "author": "M. L. Guida"},
    {"title": "Night's Promise", "author": "Amanda Ashley"},
    {"title": "Blood Eternal", "author": "Toni Kelly"},
    {"title": "Sword's Blessing", "author": "Kaitlin R. Branch"},
    {"title": "Snow White and the Vampire", "author": "Marina Myles"},
    {"title": "The Beast In Him", "author": "Shelly Laurenston"},
    {"title": "Big Bad Beast", "author": "Shelly Laurenston"},
    {"title": "A Tale of Two Dragons", "author": "G.A. Aiken"},
    {"title": "Shadowed", "author": "Rebecca Zanetti"}
]

files = [
    ("New Storefront Catalog", r"E:\Internship\PocketFM\Kensington_Storefront_Fantasy_Catalog.xlsx"),
    ("Unique Catalog", r"E:\Internship\PocketFM\Kensington_Unique_Fantasy_Fiction_Catalog.xlsx"),
    ("Master Catalog", r"E:\Internship\PocketFM\Kensington_Fantasy_Fiction_Catalog.xlsx")
]

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

for fname_label, fpath in files:
    print(f"\n{'='*80}")
    print(f"CHECKING: {fname_label} ({fpath})")
    print(f"{'='*80}")
    
    wb = openpyxl.load_workbook(fpath, data_only=True)
    ws = wb.active
    
    rows = []
    for r in range(2, ws.max_row + 1):
        t = str(ws.cell(row=r, column=1).value or "").strip()
        a = str(ws.cell(row=r, column=2).value or "").strip()
        rows.append((r, t, a))
        
    for idx, b in enumerate(new_books, 1):
        t_clean = clean(b["title"])
        a_clean = clean(b["author"])
        authors = [clean(x) for x in b["author"].replace("&", ",").split(",")]
        
        matches = []
        author_matches = []
        
        for r, t, a in rows:
            t_row_clean = clean(t)
            a_row_clean = clean(a)
            
            # Title match
            if t_clean == t_row_clean or (len(t_clean) > 4 and (t_clean in t_row_clean or t_row_clean in t_clean)):
                matches.append((r, t, a))
            # Author match
            elif any(part in a_row_clean for part in a_clean.split() if len(part) > 3):
                author_matches.append((r, t, a))
                
        if matches:
            m_strs = [f"Row {m[0]}: '{m[1]}' by {m[2]}" for m in matches]
            print(f"{idx}. '{b['title']}' by {b['author']} -> [FOUND] {', '.join(m_strs)}")
        else:
            if author_matches:
                a_sample = f" (Author found: Row {author_matches[0][0]} '{author_matches[0][1]}' by {author_matches[0][2]})"
            else:
                a_sample = ""
            print(f"{idx}. '{b['title']}' by {b['author']} -> [NOT FOUND]{a_sample}")
            
    wb.close()

