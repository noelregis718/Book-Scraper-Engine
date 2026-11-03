import openpyxl

wb = openpyxl.load_workbook('Kensington_Unique_Fantasy_Fiction_Catalog.xlsx', data_only=True)
ws = wb.active

titles_in_sheet = []
for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
    if row and row[0]:
        title = str(row[0]).strip()
        author = str(row[1]).strip() if len(row) > 1 and row[1] else ''
        titles_in_sheet.append((idx, title, author))

books_to_check = [
    ("A Sorcerer's Tail", "Victor Konara"),
    ("When the Tides Held the Moon: Deluxe Special Edition", "Venessa Vida Kelley"),
    ("The Hollow Crown of Heaven", "Karen Osborne"),
    ("A Sanctuary of Beasts: Deluxe Limited Edition", "Kalyn Josephson"),
    ("The Memory Hunters", "Mia Tsai"),
    ("The Lost Unicorn: Deluxe Limited Edition", "Sarah Maslin Nir"),
    ("A Tongue so Sweet and Deadly: Deluxe Limited Edition", "Sophia St. Germain"),
    ("The Kingdom of Almonds", "Ariel Kaplan"),
    ("Duskbound: Deluxe Limited Edition", "Bree Grenwich, Parker Lennox"),
    ("The Wrath of the Fallen: Deluxe Special Edition", "Amber V. Nicole")
]

print(f"Total rows in Kensington_Unique_Fantasy_Fiction_Catalog.xlsx: {len(titles_in_sheet)}")
print("-" * 60)

for b_title, b_author in books_to_check:
    # search logic
    core_title = b_title.split(":")[0].strip().lower()
    # also remove leading articles
    for art in ["the ", "a ", "an "]:
        if core_title.startswith(art):
            core_title_clean = core_title[len(art):]
            break
    else:
        core_title_clean = core_title

    authors = [a.strip() for a in b_author.replace("&", ",").split(",")]
    
    matches = []
    for r_idx, t, a in titles_in_sheet:
        t_low = t.lower()
        a_low = a.lower()
        
        # Check title match
        if core_title in t_low or core_title_clean in t_low:
            matches.append((r_idx, t, a, "Title Match"))
            continue
            
        # Check author match
        for auth in authors:
            last_name = auth.split()[-1].lower()
            if len(last_name) > 3 and last_name in a_low:
                matches.append((r_idx, t, a, f"Author Match ({auth})"))
                break

    print(f"Book: {b_title} | Author: {b_author}")
    if matches:
        for m in matches:
            print(f"   -> [Row {m[0]}] '{m[1]}' by '{m[2]}' ({m[3]})")
    else:
        print("   -> NOT PRESENT")
    print("-" * 60)

