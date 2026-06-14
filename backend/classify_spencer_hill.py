import pandas as pd
import os
import re

EXCEL_FILE = r"E:\Internship\PocketFM\Spencer_Hill_Press.xlsx"

KEYWORD_MAP = [
    ("High Fantasy Court Adventure", ["court", "kingdom", "throne", "prince", "princess", "king", "queen", "crown", "empire", "realm", "royal", "palace", "fae court", "high fae", "reign"]),
    ("Gothic Dark Romantasy", ["gothic", "dark", "shadow", "curse", "blood", "demon", "death", "macabre", "haunted", "sinister", "vampire", "nightmare", "manor", "asylum"]),
    ("Dark Academia Romantasy", ["academy", "university", "college", "professor", "student", "dark academia", "school", "scholar", "magic school", "boarding school"]),
    ("Monster Romance (Non-Shifter)", ["monster", "orc", "kraken", "alien", "beast", "creature", "demon lover", "tentacle", "minotaur", "gargoyle"]),
    ("Werewolf / Shifter Romance", ["werewolf", "shifter", "alpha", "pack", "omega", "luna", "wolf", "lycan", "bear shifter", "dragon shifter", "mate"]),
    ("High-Stakes Games & Deadly Trials", ["tournament", "trial", "game", "deadly", "survive", "arena", "hunger games", "contest", "maze", "gauntlet", "selection", "assassin", "survival"]),
    ("Mythology, Legend & Fairy Tale Retelling", ["retelling", "mythology", "greek god", "hades", "persephone", "fairy tale", "legend", "arthurian", "norse", "medusa", "circe", "orpheus", "beauty and the beast", "cinderella", "gods"]),
    ("War College / Military Academy", ["war college", "military academy", "dragon rider", "fourth wing", "basgiath", "aerial", "flight school", "training camp", "cadet", "legion", "regiment", "conscript", "military", "warrior", "army"]),
    ("Korean Romance Fantasy / Isekai", ["isekai", "reincarnated", "transmigrated", "villainess", "otome", "manhwa", "korean", "system", "rebirth", "regressed", "second life", "past life"]),
    ("Paranormal Romance", ["paranormal", "ghost", "witch", "warlock", "angel", "psychic", "magic", "supernatural", "seer", "medium", "necromancer", "demon hunter"]),
    ("Cozy / Cottagecore", ["cozy", "cottagecore", "tea", "bakery", "cafe", "small town", "gentle", "heartwarming", "low stakes", "witchy", "potion", "garden", "healing", "bookshop", "bake"]),
    ("Urban / Contemporary Fantasy Romance", ["urban fantasy", "city", "modern magic", "detective", "police", "new york", "london", "contemporary fantasy", "secret world", "hidden magic", "modern"])
]

def classify_row(synopsis, title):
    text = f"{synopsis} {title}".lower()
    if text.strip() == "" or text.strip() == "nan" or text.strip() == "n/a":
        return "N/A", "N/A"
        
    scores = {genre: 0 for genre, _ in KEYWORD_MAP}
    
    for genre, keywords in KEYWORD_MAP:
        for kw in keywords:
            # Add word boundaries for more accurate matching
            pattern = r'\b' + re.escape(kw) + r'\b'
            if re.search(pattern, text):
                scores[genre] += 1
                
    # If no keywords matched at all
    if sum(scores.values()) == 0:
        # Fallback check for general fantasy/romance terms to still flag as Romantasy
        general_terms = ["magic", "fantasy", "romance", "love", "spell", "dragon", "sword", "witch"]
        for term in general_terms:
            if re.search(r'\b' + term + r'\b', text):
                return "Yes", "Urban / Contemporary Fantasy Romance" # Default fallback
        return "No", "N/A"
        
    # Find the top genre
    best_genre = max(scores, key=scores.get)
    return "Yes", best_genre

def main():
    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)
    
    romantasy_col = "Romantasy = Yes or No?"
    subgenre_col = "Romantasy Sub-Genre of series"
    
    # Ensure columns exist
    if romantasy_col not in df.columns:
        df[romantasy_col] = "N/A"
    if subgenre_col not in df.columns:
        df[subgenre_col] = "N/A"
        
    updates = 0
    
    for index, row in df.iterrows():
        # Only classify if we have a title (and skip placeholder 'AUTHORS' rows if they snuck in)
        if str(row['Name of Series']) == 'nan' or str(row['Name of Series']) == 'AUTHORS':
            continue
            
        # We classify regardless of current value, or only if N/A. The prompt implies "do it now for the columns", so we update all that make sense
        synopsis = str(row['Synopsis (if available)'])
        title = str(row['Name of Series'])
        
        is_romantasy, subgenre = classify_row(synopsis, title)
        
        # We only override if it gives a positive classification or if it was empty/NA before
        current_val = str(row[romantasy_col]).strip()
        if is_romantasy == "Yes":
            df.at[index, romantasy_col] = is_romantasy
            df.at[index, subgenre_col] = subgenre
            updates += 1
        elif current_val == 'nan' or current_val == 'N/A' or current_val == '':
            df.at[index, romantasy_col] = is_romantasy
            df.at[index, subgenre_col] = subgenre
            updates += 1

    print(f"Classified {updates} rows based on keywords.")
    
    print(f"Saving to {EXCEL_FILE}...")
    df.to_excel(EXCEL_FILE, index=False)
    print("Done!")

if __name__ == "__main__":
    main()
