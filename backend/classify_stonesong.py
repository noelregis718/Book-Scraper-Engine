import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

EXCEL_FILE = r"E:\Internship\PocketFM\Stonesong_Books.xlsx"

KEYWORD_MAP = [
    ("Werewolf / Shifter Romance", ["werewolf", "shifter", "alpha", "pack", "omega", "luna", "wolf", "lycan"]),
    ("Monster Romance (Non-Shifter)", ["monster", "orc", "kraken", "alien", "beast", "creature", "demon lover", "tentacle"]),
    ("Mythology, Legend & Fairy Tale Retelling", ["retelling", "mythology", "greek god", "hades", "persephone", "fairy tale", "legend", "arthurian", "norse", "anansi", "medusa", "circe", "orpheus", "beauty and the beast", "greek"]),
    ("War College / Military Academy", ["war college", "military academy", "dragon rider", "fourth wing", "basgiath", "aerial", "flight school", "training camp", "rider", "bonded dragon", "academy"]),
    ("High-Stakes Games & Deadly Trials", ["trial", "deadly game", "tournament", "competition", "survival", "arena", "hunger game", "death match", "blood game", "lethal", "battle royale"]),
    ("Dark Academia Romantasy", ["dark academia", "secret society", "forbidden library", "ancient university", "campus", "scholarly", "cursed school", "arcane academy", "magic school"]),
    ("Gothic Dark Romantasy", ["gothic", "haunted", "manor", "dark romance", "gloomy castle", "shadow court", "cursed castle", "decaying estate", "vampire lord", "immortal lord", "gothic romance"]),
    ("Korean Romance Fantasy / Isekai", ["isekai", "reincarnated", "villainess", "otome", "korean", "manhwa", "transmigrated", "possessed", "regression"]),
    ("Cozy / Cottagecore", ["cozy", "cottagecore", "small town magic", "bakery", "low stakes", "wholesome", "botanical", "village witch", "flower shop", "magical inn", "christmas miracle", "mail order bride", "cozy mystery"]),
    ("Paranormal Romance", ["vampire", "ghost", "witch", "paranormal", "psychic", "medium", "warlock", "necromancer", "haunting", "supernatural romance", "fae romance", "fairy", "magic", "vampires", "witches"]),
    ("High Fantasy Court Adventure", ["court", "throne", "kingdom", "royalty", "fae court", "high fantasy", "crown", "empire", "queen", "king", "prince", "realm", "dragon", "epic fantasy", "war", "political intrigue", "magic system", "assassin"]),
    ("Urban / Contemporary Fantasy Romance", ["urban fantasy", "modern day", "contemporary fantasy", "hidden world", "secret magic", "real world", "city magic", "supernatural city", "modern"])
]

# Adding romantasy trigger words to catch general romantasy if no specific subgenre is hit
ROMANTASY_TRIGGERS = ["romantasy", "fantasy romance", "romantic fantasy", "romance fantasy", "enemies to lovers", "fated mates", "fae romance", "vampire romance", "shifter romance", "paranormal romance"]

def classify_subgenre(text):
    text = str(text).lower()
    for subgenre, keywords in KEYWORD_MAP:
        if any(k in text for k in keywords):
            return subgenre
    return None

def is_general_romantasy(text):
    text = str(text).lower()
    if any(k in text for k in ROMANTASY_TRIGGERS):
        return True
    return False

def main():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE, keep_default_na=False)
            
    romantasy_col = "Romantasy = Yes or No?"
    subgenre_col = "Romantasy Sub-Genre of series"
    
    yes_count = 0
    
    for idx, row in df.iterrows():
        title = str(row.get('Name of Series', '')).strip()
        synopsis = str(row.get('Synopsis (if available)', '')).strip()
        genre = str(row.get('Romantasy Sub-Genre of series', '')).strip() # Previous scrape genres
        
        if title.lower() in ['nan', '']:
            continue
            
        current_yes_no = str(row.get(romantasy_col, '')).strip()
        
        # Combine all text to classify subgenre
        combined_text = synopsis + " " + title + " " + genre
        
        # Classify
        subgenre_result = classify_subgenre(combined_text)
        
        # Decide Yes/No
        # If the scraper found a romantasy match, or our classifier found a romantasy sub-genre, or general romantasy triggers
        if current_yes_no.lower() == 'yes' or subgenre_result is not None or is_general_romantasy(combined_text):
            df.at[idx, romantasy_col] = "Yes"
            df.at[idx, subgenre_col] = subgenre_result if subgenre_result else "High Fantasy Court Adventure"
            yes_count += 1
        else:
            df.at[idx, romantasy_col] = "No"
            df.at[idx, subgenre_col] = "N/A"

    print(f"Saving {EXCEL_FILE} with {yes_count} Romantasy matches...")
    df.to_excel(EXCEL_FILE, index=False)
    
    # Try formatting
    try:
        from format_stonesong_books import format_stonesong_books
        print("Running final styling format...")
        format_stonesong_books(EXCEL_FILE)
    except Exception as e:
        pass
        
    print("ALL DONE!")

if __name__ == '__main__':
    main()
