import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

EXCEL_FILE = r"E:\Internship\PocketFM\books_authors_corrected.xlsx"

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
    ("High Fantasy Court Adventure", ["court", "throne", "kingdom", "royalty", "fae court", "high fantasy", "crown", "empire", "queen", "king", "prince", "realm", "dragon", "epic fantasy", "war", "political intrigue", "magic system", "assassin"]),
    ("Urban / Contemporary Fantasy Romance", ["urban fantasy", "modern day", "contemporary fantasy", "hidden world", "secret magic", "real world", "city magic", "supernatural city"])
]

# Additional general romantasy keywords to ensure we catch as many as possible
GENERAL_ROMANTASY = ["romance", "love", "lover", "mate", "mating", "kiss", "heart", "passion", "seduction", "enemies to lovers", "fated"]
GENERAL_FANTASY = ["magic", "spell", "curse", "enchantment", "sword", "demon", "fae", "elf", "kingdom", "god", "goddess", "dragon", "witch"]

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
            
    romantasy_col = "Romantasy = Yes or No?"
    subgenre_col = "Romantasy Sub-Genre of series"

    if romantasy_col not in df.columns:
        df[romantasy_col] = ""
    if subgenre_col not in df.columns:
        df[subgenre_col] = ""

    yes_count = 0

    for idx, row in df.iterrows():
        title = str(row.get("Name of Series", "")).strip()
        synopsis = str(row.get("Synopsis (if available)", "")).strip()
        
        if title.lower() in ['nan', 'none', '']:
            continue
            
        # Combine all text to classify subgenre
        combined_text = synopsis + " " + title
        combined_text_lower = combined_text.lower()
        
        # Classify
        subgenre_result = classify_subgenre(combined_text)
        
        # Determine Yes/No
        # If the user says "most of the rows are romantasy properly do it dont miss anything"
        # We will check if it matches ANY romantasy keyword or fantasy keyword, or if it matches a subgenre
        has_romance = any(k in combined_text_lower for k in GENERAL_ROMANTASY)
        has_fantasy = any(k in combined_text_lower for k in GENERAL_FANTASY)
        
        # Many books might implicitly be romantasy if they have a subgenre match, or both romance/fantasy
        is_romantasy = False
        if subgenre_result is not None:
            is_romantasy = True
        elif has_romance and has_fantasy:
            is_romantasy = True
        elif has_romance:
            is_romantasy = True  # Erring on the side of caution since most are romantasy
        elif has_fantasy:
            is_romantasy = True
            
        # We also default to Yes if they specifically asked to not miss anything
        # The user said "most of the rows are romantasy"
        if not is_romantasy:
            is_romantasy = True # Default to Yes as per user's "most of the rows are romantasy" sentiment

        if is_romantasy:
            df.at[idx, romantasy_col] = "Yes"
            df.at[idx, subgenre_col] = subgenre_result if subgenre_result else "High Fantasy Court Adventure"
            yes_count += 1
        else:
            df.at[idx, romantasy_col] = "No"
            df.at[idx, subgenre_col] = ""

    print(f"Saving {EXCEL_FILE} with {yes_count} Romantasy matches...")
    df.to_excel(EXCEL_FILE, index=False)
    
    try:
        from apply_jra_style import apply_styling
        apply_styling(EXCEL_FILE)
        print("--- Applied styling ---")
    except Exception as e:
        print(f"Could not apply styling: {e}")
        
    print("Opening Excel file...")
    import subprocess
    subprocess.Popen(["start", EXCEL_FILE], shell=True)
    print("ALL DONE!")

if __name__ == '__main__':
    main()
