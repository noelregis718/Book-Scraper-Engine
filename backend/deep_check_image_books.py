import openpyxl
import re
from difflib import SequenceMatcher

CATALOG_FILE = r"E:\Internship\PocketFM\Kensington_Unique_Fantasy_Fiction_Catalog.xlsx"

books_to_check = [
    {
        "title": "A Sorcerer's Tail",
        "clean_title": "sorcerer's tail",
        "author": "Victor Konara",
        "keywords": ["sorcerer", "tail", "konara"],
        "series_known": ["sorcerer's tail", "konara"]
    },
    {
        "title": "When the Tides Held the Moon",
        "clean_title": "when the tides held the moon",
        "author": "Venessa Vida Kelley",
        "keywords": ["tides", "held", "moon", "venessa", "kelley"],
        "series_known": ["tides held the moon", "venessa vida kelley"]
    },
    {
        "title": "The Hollow Crown of Heaven",
        "clean_title": "hollow crown of heaven",
        "author": "Karen Osborne",
        "keywords": ["hollow crown", "crown of heaven", "osborne"],
        "series_known": ["sun-surfer", "into the rush", "osborne"]
    },
    {
        "title": "A Sanctuary of Beasts",
        "clean_title": "sanctuary of beasts",
        "author": "Kalyn Josephson",
        "keywords": ["sanctuary", "beasts", "josephson", "kalyn"],
        "series_known": ["storm crow", "iron widow", "sanctuary of beasts", "beasts"]
    },
    {
        "title": "The Memory Hunters",
        "clean_title": "memory hunters",
        "author": "Mia Tsai",
        "keywords": ["memory hunters", "tsai", "mia"],
        "series_known": ["bitter medicine", "memory hunters", "freaks and familiars"]
    },
    {
        "title": "The Lost Unicorn",
        "clean_title": "lost unicorn",
        "author": "Sarah Maslin Nir",
        "keywords": ["lost unicorn", "maslin", "nir"],
        "series_known": ["lost unicorn", "horse crazy"]
    },
    {
        "title": "A Tongue so Sweet and Deadly",
        "clean_title": "tongue so sweet and deadly",
        "author": "Sophia St. Germain",
        "keywords": ["tongue", "sweet", "deadly", "germain", "sophia"],
        "series_known": ["crown of gilded bones", "promise so bold", "sweet and deadly"]
    },
    {
        "title": "The Kingdom of Almonds",
        "clean_title": "kingdom of almonds",
        "author": "Ariel Kaplan",
        "keywords": ["kingdom", "almonds", "ariel", "kaplan"],
        "series_known": ["mirror realm", "kingdom of almonds", "kaplan"]
    },
    {
        "title": "Duskbound",
        "clean_title": "duskbound",
        "author": "Bree Grenwich, Parker Lennox",
        "keywords": ["duskbound", "grenwich", "lennox"],
        "series_known": ["duskbound", "shadowbound"]
    },
    {
        "title": "The Wrath of the Fallen",
        "clean_title": "wrath of the fallen",
        "author": "Amber V. Nicole",
        "keywords": ["wrath", "fallen", "azrael", "dianna", "liam", "amber v", "nicole"],
        "series_known": ["gods and monsters", "gods & monsters", "book of azrael"]
    }
]

wb = openpyxl.load_workbook(CATALOG_FILE, data_only=True)
ws = wb.active

headers = [str(cell.value or '').strip() for cell in ws[1]]
print("HEADERS:", headers)

rows_data = []
for r_idx in range(2, ws.max_row + 1):
    row_vals = [ws.cell(row=r_idx, column=c).value for c in range(1, len(headers) + 1)]
    title = str(row_vals[0] or '').strip()
    author = str(row_vals[1] or '').strip()
    link = str(row_vals[3] or '').strip()
    synopsis = str(row_vals[7] or '').strip()
    
    rows_data.append({
        "row": r_idx,
        "title": title,
        "author": author,
        "link": link,
        "synopsis": synopsis,
        "all_text": f"{title} {author} {link} {synopsis}".lower()
    })

print(f"Total rows scanned: {len(rows_data)}\n")

for b in books_to_check:
    print("=" * 70)
    print(f"CHECKING: '{b['title']}' by {b['author']}")
    print("=" * 70)
    
    # Technique A: Exact or Normalized Title Substring
    norm_target = re.sub(r'[^\w\s]', '', b['title'].lower()).strip()
    t_matches = []
    
    # Technique B: Author match
    auth_matches = []
    
    # Technique C: Fuzzy ratio (> 0.65) on Title
    fuzzy_matches = []
    
    # Technique D: Keyword match in Series Name / Synopsis / Goodreads link
    keyword_matches = []
    
    # Technique E: Series Name match (for books in known series)
    series_matches = []
    
    for r in rows_data:
        norm_row_t = re.sub(r'[^\w\s]', '', r['title'].lower()).strip()
        norm_row_a = re.sub(r'[^\w\s]', '', r['author'].lower()).strip()
        
        # A: Title match
        if norm_target in norm_row_t or (len(norm_row_t) > 5 and norm_row_t in norm_target):
            t_matches.append(r)
            
        # B: Author match (exact full last name)
        authors = [a.strip().lower() for a in b['author'].replace('&', ',').split(',')]
        for auth in authors:
            last_name = auth.split()[-1]
            if len(last_name) > 3 and last_name in norm_row_a.split():
                auth_matches.append((r, auth))
                break
                
        # C: Fuzzy ratio
        ratio = SequenceMatcher(None, norm_target, norm_row_t).ratio()
        if ratio > 0.65 and r not in t_matches:
            fuzzy_matches.append((r, ratio))
            
        # D: Known series match
        for s in b['series_known']:
            if s.lower() in r['all_text']:
                series_matches.append((r, s))
                break
                
        # E: Keyword in synopsis or link
        for kw in b['keywords']:
            if len(kw) > 4 and kw.lower() in r['synopsis'].lower():
                keyword_matches.append((r, kw))
                break

    # Report findings for this book
    if t_matches:
        print("  [Technique 1: Direct Title Match]")
        for m in t_matches:
            print(f"    -> Row {m['row']}: '{m['title']}' by '{m['author']}'")
    else:
        print("  [Technique 1: Direct Title Match] -> NONE")

    if fuzzy_matches:
        print("  [Technique 2: Fuzzy String Similarity (>65%)]")
        for m, ratio in sorted(fuzzy_matches, key=lambda x: x[1], reverse=True)[:3]:
            print(f"    -> Row {m['row']} ({ratio*100:.1f}%): '{m['title']}' by '{m['author']}'")
    else:
        print("  [Technique 2: Fuzzy String Similarity] -> NONE")

    if auth_matches:
        print(f"  [Technique 3: Author Catalog Match ({len(auth_matches)} books by author)]")
        for m, a_name in auth_matches[:5]:
            print(f"    -> Row {m['row']}: '{m['title']}' by '{m['author']}'")
    else:
        print("  [Technique 3: Author Catalog Match] -> NONE")

    if series_matches:
        print(f"  [Technique 4: Series / Franchise / Universe Match]")
        for m, s_term in series_matches[:4]:
            print(f"    -> Row {m['row']} (Matched on '{s_term}'): '{m['title']}' by '{m['author']}'")
    else:
        print("  [Technique 4: Series / Franchise Match] -> NONE")

    if keyword_matches:
        print(f"  [Technique 5: Synopsis Keyword Match]")
        for m, kw in keyword_matches[:3]:
            print(f"    -> Row {m['row']} (Found '{kw}' in synopsis): '{m['title']}'")
    else:
        print("  [Technique 5: Synopsis Keyword Match] -> NONE")

    print()

