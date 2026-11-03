import openpyxl
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
    # Remove subtitles after colon, dash
    name = re.sub(r'[:\-—\(].*$', '', name)
    # Remove punctuation
    name = re.sub(r'[\W_]+', '', name)
    # Remove common filler words
    for p in ['deluxespecialedition', 'deluxelimitededition', 'deluxeedition', 'the', 'a', 'an']:
        name = name.replace(p, '')
    return name.strip()

print("Loading Kensington_Unique_Fantasy_Fiction_Catalog.xlsx...")
df_unique = pd.read_excel("Kensington_Unique_Fantasy_Fiction_Catalog.xlsx")
title_col = df_unique.columns[0]
author_col = df_unique.columns[1]

# Build clean mapping
unique_titles = df_unique[title_col].dropna().astype(str).tolist()
clean_to_orig_unique = {}
for idx, t in enumerate(unique_titles, start=2):
    c = clean_for_diff(t)
    if c:
        clean_to_orig_unique[c] = (idx, t, str(df_unique.iloc[idx-2][author_col]))

print(f"Total Unique Titles Loaded: {len(unique_titles)}")
print("=" * 80)
print("RUNNING AGGRESSIVE / CLOSE MATCH (difflib cutoff=0.45):")
print("=" * 80)

for idx, b in enumerate(target_books, 1):
    c_target = clean_for_diff(b["title"])
    matches = difflib.get_close_matches(c_target, clean_to_orig_unique.keys(), n=3, cutoff=0.45)
    
    print(f"\n{idx}. TARGET: '{b['title']}' by {b['author']}")
    print(f"   [Cleaned: '{c_target}']")
    if matches:
        print("   -> Close Matches Found in Catalog:")
        for m in matches:
            row_num, orig_t, orig_a = clean_to_orig_unique[m]
            ratio = difflib.SequenceMatcher(None, c_target, m).ratio()
            print(f"      * [Row {row_num}] '{orig_t}' by '{orig_a}' (Similarity: {ratio:.2f})")
    else:
        print("   -> NO CLOSE MATCH (Cutoff 0.45)")

