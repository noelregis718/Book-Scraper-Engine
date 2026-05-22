import pandas as pd
import os
import json
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from format_madwoman import format_madwoman

EXCEL_FILE = r"e:\Internship\PocketFM\madeleine_milburn_combined.xlsx"
STATE_FILE = r"e:\Internship\PocketFM\backend\madeleine_state.json"

KEYWORD_MAP = [
    ("Werewolf / Shifter Romance", ["werewolf", "shifter", "alpha", "pack", "omega", "luna", "wolf", "lycan"]),
    ("Monster Romance (Non-Shifter)", ["monster", "orc", "kraken", "alien", "beast", "creature", "demon lover", "tentacle"]),
    ("Mythology, Legend & Fairy Tale Retelling", ["retelling", "mythology", "greek god", "hades", "persephone", "fairy tale", "legend", "arthurian", "norse", "anansi", "medusa", "circe", "orpheus", "beauty and the beast"]),
    ("War College / Military Academy", ["war college", "military academy", "dragon rider", "fourth wing", "basgiath", "aerial", "flight school", "training camp", "rider", "bonded dragon", "academy"]),
    ("High-Stakes Games & Deadly Trials", ["trial", "deadly game", "tournament", "competition", "survival", "arena", "hunger game", "death match", "blood game", "lethal"]),
    ("Dark Academia Romantasy", ["dark academia", "secret society", "forbidden library", "ancient university", "campus", "scholarly", "cursed school", "arcane academy", "magic school"]),
    ("Gothic Dark Romantasy", ["gothic", "haunted", "manor", "dark romance", "gloomy castle", "shadow court", "cursed castle", "decaying estate", "vampire lord", "immortal lord"]),
    ("Korean Romance Fantasy / Isekai", ["isekai", "reincarnated", "villainess", "otome", "korean", "manhwa", "transmigrated", "possessed", "regression"]),
    ("Cozy / Cottagecore", ["cozy", "cottagecore", "small town magic", "bakery", "low stakes", "wholesome", "botanical", "village witch", "flower shop", "magical inn", "christmas miracle", "mail order bride"]),
    ("Paranormal Romance", ["vampire", "ghost", "witch", "paranormal", "psychic", "medium", "warlock", "necromancer", "haunting", "supernatural romance", "fae romance", "fairy", "magic"]),
    ("High Fantasy Court Adventure", ["court", "throne", "kingdom", "royalty", "fae court", "high fantasy", "crown", "empire", "queen", "king", "prince", "realm", "dragon", "epic fantasy", "war", "political intrigue", "magic system"]),
    ("Urban / Contemporary Fantasy Romance", ["urban fantasy", "modern day", "contemporary fantasy", "hidden world", "secret magic", "real world", "city magic", "supernatural city"])
]

def classify_subgenre(text):
    text = str(text).lower()
    for subgenre, keywords in KEYWORD_MAP:
        if any(k in text for k in keywords):
            return subgenre
    return None

def main():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)
    
    state = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            state = json.load(f)
            
    romantasy_col = "Romantasy = Yes or No?"
    subgenre_col = "Romantasy Sub-Genre of series"
    
    yes_count = 0
    
    for idx, row in df.iterrows():
        title = str(row.get('Name of Series', '')).strip()
        author = str(row.get('Author Name', '')).strip()
        synopsis = str(row.get('Synopsis (if available)', '')).strip()
        
        if title.lower() == 'nan' or not title:
            continue
            
        current_yes_no = str(row.get(romantasy_col, '')).strip()
        current_sub = str(row.get(subgenre_col, '')).strip()
        
        # Preserve specific user overrides (like the last two rows)
        if current_sub and current_sub != 'nan' and current_sub != 'N/A' and current_yes_no == 'Yes':
            yes_count += 1
            continue
            
        # 1. Lookup in state for Goodreads Genre / Romantasy flag
        gr_romantasy = 'No'
        gr_genres = ''
        if author in state:
            for b in state[author]:
                if b.get('title') == title or b.get('Book_Title') == title:
                    gr_romantasy = b.get('Romantasy_Subgenre', 'No')
                    gr_genres = str(b.get('Genre', '')) + " " + str(b.get('Sub_Genre', ''))
                    break
                    
        # 2. Combine all text to classify subgenre
        combined_text = gr_genres + " " + synopsis + " " + title
        
        # 3. Classify
        subgenre_result = classify_subgenre(combined_text)
        
        # 4. Decide Yes/No
        # If Goodreads explicitly says it's romantasy, or our classifier found a romantasy sub-genre
        if gr_romantasy == 'Yes' or current_yes_no == 'Yes' or subgenre_result is not None:
            df.at[idx, romantasy_col] = "Yes"
            df.at[idx, subgenre_col] = subgenre_result if subgenre_result else "High Fantasy Court Adventure"
            yes_count += 1
        else:
            df.at[idx, romantasy_col] = "No"
            df.at[idx, subgenre_col] = ""

    print(f"Saving {EXCEL_FILE} with {yes_count} Romantasy matches...")
    df.to_excel(EXCEL_FILE, index=False)
    
    # Format and strip validation
    print("Formatting...")
    format_madwoman(EXCEL_FILE, EXCEL_FILE)
    
    print("Copying to Downloads...")
    os.system(r'powershell -Command "Copy-Item e:\Internship\PocketFM\madeleine_milburn_combined.xlsx -Destination C:\Users\noelr\Downloads\madeleine_milburn_combined_v3.xlsx -Force"')
    
    print("ALL DONE!")

if __name__ == '__main__':
    main()
