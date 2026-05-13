import pandas as pd
import os
import sys
from excel_utility import save_lima_excel

# --- CONFIGURATION ---
INPUT_FILE = r"E:\Internship\PocketFM\Lima Agency.xlsx"

def classify_book(title, author, synopsis):
    title = str(title).lower()
    author = str(author).lower()
    synopsis = str(synopsis).lower()
    combined = f"{title} {synopsis}"
    
    # 1. Werewolf / Shifter Romance
    if any(k in combined for k in ["werewolf", "shifter", " wolf", "pack", "alpha", "omega", "mate", "luna"]):
        return "Yes", "Werewolf / Shifter Romance"
    
    # 2. Dark Academia Romantasy
    if any(k in combined for k in ["university", "college", "campus", "professor", "student", "academia", "secret society", "library"]):
        if any(k in combined for k in ["dark", "murder", "mystery", "forbidden"]):
            return "Yes", "Dark Academia Romantasy"
            
    # 3. War College / Military Academy
    if any(k in combined for k in ["war college", "military academy", "cadet", "soldier", "general", "training", "army"]):
        return "Yes", "War College / Military Academy"
        
    # 4. Korean Romance Fantasy / Isekai
    if any(k in combined for k in ["reincarnated", "reborn", "villainess", "isekai", "otome", "webtoon", "korean", "manhwa"]):
        return "Yes", "Korean Romance Fantasy / Isekai"
        
    # 5. Mythology, Legend & Fairy Tale Retelling
    if any(k in combined for k in ["retelling", "myth", "legend", "hades", "persephone", "greek", "gods", "goddess", "fairy tale", "retold"]):
        return "Yes", "Mythology, Legend & Fairy Tale Retelling"
        
    # 6. High-Stakes Games & Deadly Trials
    if any(k in combined for k in ["game", "trial", "competition", "deadly", "survival", "tournament", "arena"]):
        return "Yes", "High-Stakes Games & Deadly Trials"
        
    # 7. Gothic Dark Romantasy
    if any(k in combined for k in ["gothic", "mansion", "estate", "victorian", "haunted", "shadows", "darkness"]):
        return "Yes", "Gothic Dark Romantasy"
        
    # 8. Monster Romance (Non-Shifter)
    if any(k in combined for k in ["monster", "beast", "alien", "creature", "non-human", "tentacle", "orc"]):
        return "Yes", "Monster Romance (Non-Shifter)"
        
    # 9. Cozy / Cottagecore
    if any(k in combined for k in ["cozy", "cottage", "small town", "bakery", "shop", "gentle", "tea", "comfort"]):
        return "Yes", "Cozy / Cottagecore"
        
    # 10. High Fantasy Court Adventure
    if any(k in combined for k in ["court", "throne", "kingdom", "realm", "crown", "princess", "prince", "politics", "epic"]):
        return "Yes", "High Fantasy Court Adventure"
        
    # 11. Paranormal Romance
    if any(k in combined for k in ["vampire", "ghost", "demon", "angel", "psychic", "spirit", "supernatural", "witch"]):
        return "Yes", "Paranormal Romance"
        
    # 12. Urban / Contemporary Fantasy Romance
    if any(k in combined for k in ["city", "modern", "contemporary", "urban", "new york", "london", "detective"]):
        return "Yes", "Urban / Contemporary Fantasy Romance"

    # Default if no keywords match but it sounds like fantasy
    if any(k in combined for k in ["magic", "fantasy", "sword", "dragon", "love", "heart", "romance"]):
        return "Yes", "Urban / Contemporary Fantasy Romance" # Default category
        
    return "No", "N/A"

def run_classification():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: File not found: {INPUT_FILE}")
        return

    print(f"Reading {INPUT_FILE}...")
    df = pd.read_excel(INPUT_FILE)
    
    total = len(df)
    print(f"Processing {total} titles...")
    
    for index, row in df.iterrows():
        title = row.get('Name of Series', '')
        author = row.get('Author Name', '')
        synopsis = row.get('Synopsis (if available)', '')
        
        is_romantasy, subgenre = classify_book(title, author, synopsis)
        
        df.at[index, 'Is it Romantasy ?'] = is_romantasy
        df.at[index, 'Romantasy Sub-Genre of series'] = subgenre
        
        if (index + 1) % 50 == 0:
            print(f"  Processed {index + 1}/{total}...")
            
    print(f"Saving classified results to {INPUT_FILE}...")
    save_lima_excel(df.to_dict('records'), INPUT_FILE)
    print("Classification Complete!")

if __name__ == "__main__":
    run_classification()
