import openpyxl
import re

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

files = [
    "Kensington_Unique_Fantasy_Fiction_Catalog.xlsx",
    "Kensington_Fantasy_Fiction_Catalog.xlsx",
    "Kensington Agency.xlsx",
    "Kensington Old List.xlsx"
]

def normalize(s):
    if not s:
        return ""
    s = str(s).lower()
    s = re.sub(r'[:\-—\(].*$', '', s) # Strip subtitles, e.g. ": Deluxe Limited Edition"
    s = re.sub(r'[^\w\s]', '', s)
    return re.sub(r'\s+', ' ', s).strip()

results = {}

for fname in files:
    try:
        wb = openpyxl.load_workbook(fname, read_only=True)
        ws = wb[wb.sheetnames[0]]
        print(f"\nScanning {fname} (Rows: {ws.max_row})...")
        
        file_matches = {}
        for r_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            if not row or not row[0]:
                continue
            r_title = str(row[0])
            r_author = str(row[1]) if len(row) > 1 and row[1] else ""
            
            norm_r_title = normalize(r_title)
            norm_r_author = normalize(r_author)
            
            for b in target_books:
                t_norm = normalize(b["title"])
                a_norm = normalize(b["author"])
                
                # Check match by title
                if t_norm in norm_r_title or norm_r_title in t_norm:
                    key = b["title"]
                    if key not in file_matches:
                        file_matches[key] = []
                    file_matches[key].append({
                        "row": r_idx,
                        "title": r_title,
                        "author": r_author
                    })
                # Check match by author keyword if title doesn't match
                elif a_norm and (a_norm in norm_r_author or any(part in norm_r_author for part in a_norm.split() if len(part) > 4)):
                    key = b["title"]
                    if key not in file_matches:
                        file_matches[key] = []
                    file_matches[key].append({
                        "row": r_idx,
                        "title": f"[Author Match Only] {r_title}",
                        "author": r_author
                    })
                    
        results[fname] = file_matches
        wb.close()
    except Exception as e:
        print(f"Error reading {fname}: {e}")

print("\n" + "=" * 80)
print("FINAL REPORT: PRESENCE OF THE 10 IMAGE BOOKS ACROSS KENSINGTON LISTS")
print("=" * 80)

for idx, b in enumerate(target_books, 1):
    print(f"\n{idx}. '{b['title']}' by {b['author']}:")
    for fname in files:
        matches = results.get(fname, {}).get(b["title"], [])
        if matches:
            # Filter exact or close title matches
            exact_m = [m for m in matches if not m['title'].startswith("[Author Match Only]")]
            if exact_m:
                m_str = ", ".join([f"Row {m['row']}: '{m['title']}' by {m['author']}" for m in exact_m])
                print(f"   [FOUND] in {fname} -> {m_str}")
            else:
                author_m = ", ".join([f"Row {m['row']}: '{m['title']}'" for m in matches[:2]])
                print(f"   [Author Match Only] in {fname} -> {author_m}")
        else:
            print(f"   [NOT FOUND] in {fname}")

