import pandas as pd
import difflib
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
    {"title": "Duskbound", "author": "Bree Grenwich, Parker Lennox"},
    {"title": "The Wrath of the Fallen", "author": "Amber V. Nicole"}
]

def clean_for_diff(name):
    if not name or pd.isna(name):
        return ""
    name = str(name).lower()
    name = re.sub(r'[:\-—\(].*$', '', name)
    name = re.sub(r'[\W_]+', '', name)
    for p in ['deluxespecialedition', 'deluxelimitededition', 'deluxeedition', 'the', 'a', 'an']:
        name = name.replace(p, '')
    return name.strip()

print("Loading Kensington_Fantasy_Fiction_Catalog.xlsx (Master)...")
df_master = pd.read_excel("Kensington_Fantasy_Fiction_Catalog.xlsx")
title_col = df_master.columns[0]
author_col = df_master.columns[1]

master_titles = df_master[title_col].dropna().astype(str).tolist()
clean_to_orig_master = {}
for idx, t in enumerate(master_titles, start=2):
    c = clean_for_diff(t)
    if c:
        clean_to_orig_master[c] = (idx, t, str(df_master.iloc[idx-2][author_col]))

print(f"Total Master Titles: {len(master_titles)}")

for idx, b in enumerate(target_books, 1):
    c_target = clean_for_diff(b["title"])
    matches = difflib.get_close_matches(c_target, clean_to_orig_master.keys(), n=2, cutoff=0.6)
    
    print(f"\n{idx}. TARGET: '{b['title']}' by {b['author']}")
    if matches:
        for m in matches:
            row_num, orig_t, orig_a = clean_to_orig_master[m]
            ratio = difflib.SequenceMatcher(None, c_target, m).ratio()
            print(f"   -> [Row {row_num}] '{orig_t}' by '{orig_a}' (Similarity: {ratio:.2f})")
    else:
        print("   -> NO MATCH >= 0.60")

