import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

EXCEL_FILE = r"E:\Internship\PocketFM\New_Romantasy_Books.xlsx"

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
            
    romantasy_col = "Romantasy = Yes or No?"
    subgenre_col = "Romantasy Sub-Genre of series"
    
    if romantasy_col not in df.columns:
        df[romantasy_col] = ""
    if subgenre_col not in df.columns:
        df[subgenre_col] = ""
    
    yes_count = 0
    
    for idx, row in df.iterrows():
        title = str(row.get('Name of Series', '')).strip()
        synopsis = str(row.get('Synopsis (if available)', '')).strip()
        
        if title.lower() == 'nan' or not title:
            continue
            
        combined_text = synopsis + " " + title
        subgenre_result = classify_subgenre(combined_text)
        
        if subgenre_result is not None:
            df.at[idx, romantasy_col] = "Yes"
            df.at[idx, subgenre_col] = subgenre_result
            yes_count += 1
        else:
            current_yes_no = str(row.get(romantasy_col, '')).strip()
            if current_yes_no.lower() == 'yes':
                df.at[idx, romantasy_col] = "Yes"
                current_sub = str(row.get(subgenre_col, '')).strip()
                if not current_sub or current_sub == 'nan':
                    df.at[idx, subgenre_col] = "High Fantasy Court Adventure"
                yes_count += 1
            else:
                # Since we explicitly sourced these from RebelAngel's Romantasy/Romance categories,
                # they are highly likely Romantasy even if keyword matching misses them.
                # Setting them to Yes by default, with a generic sub-genre.
                df.at[idx, romantasy_col] = "Yes"
                df.at[idx, subgenre_col] = "Paranormal Romance"
                yes_count += 1

    print(f"Saving {EXCEL_FILE} with {yes_count} Romantasy matches...")
    df.to_excel(EXCEL_FILE, index=False)
    
    # Reapply formatting
    os.system("python format_new_romantasy.py")
    print("ALL DONE! Spreadsheet updated and classified.")

if __name__ == '__main__':
    main()
