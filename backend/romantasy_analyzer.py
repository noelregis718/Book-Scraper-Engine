import pandas as pd
import os
import re

# The 12 Romantasy Categories
TAXONOMY = [
    "High Fantasy Court Adventure",
    "Gothic Dark Romantasy",
    "Dark Academia Romantasy",
    "Monster Romance (Non-Shifter)",
    "Werewolf / Shifter Romance",
    "High-Stakes Games & Deadly Trials",
    "Mythology, Legend & Fairy Tale Retelling",
    "War College / Military Academy",
    "Korean Romance Fantasy / Isekai",
    "Paranormal Romance",
    "Cozy / Cottagecore",
    "Urban / Contemporary Fantasy Romance"
]

def identify_romantasy_subgenre(synopsis, genre_text=""):
    """Analyzes synopsis and genre to classify into one of the 12 Romantasy categories."""
    if not isinstance(synopsis, str) or len(synopsis) < 10:
        return "N/A"
    
    text = (synopsis + " " + str(genre_text)).lower()
    
    # 1. Werewolf / Shifter Romance
    if any(k in text for k in ["werewolf", "shifter", "alpha", "pack", "omega", "luna"]):
        return "Werewolf / Shifter Romance"
    
    # 2. Monster Romance (Non-Shifter)
    if any(k in text for k in ["monster", "orc", "kraken", "alien", "demon", "beast"]) and "shifter" not in text:
        return "Monster Romance (Non-Shifter)"
    
    # 3. Mythology, Legend & Fairy Tale Retelling
    if any(k in text for k in ["retelling", "mythology", "greek gods", "hades", "persephone", "fairy tale", "legend"]):
        return "Mythology, Legend & Fairy Tale Retelling"
    
    # 4. War College / Military Academy
    if any(k in text for k in ["war college", "military academy", "dragon rider", "training", "fourth wing", "basgiath"]):
        return "War College / Military Academy"
    
    # 5. High-Stakes Games & Deadly Trials
    if any(k in text for k in ["trials", "deadly games", "competition", "tournament", "survival", "hunger games style"]):
        return "High-Stakes Games & Deadly Trials"
    
    # 6. Dark Academia Romantasy
    if any(k in text for k in ["university", "secret society", "library", "dark academia", "campus", "scholarly"]):
        return "Dark Academia Romantasy"
    
    # 7. Gothic Dark Romantasy
    if any(k in text for k in ["gothic", "haunted", "manor", "dark romance", "gloomy", "castle", "shadows"]):
        return "Gothic Dark Romantasy"
    
    # 8. Korean Romance Fantasy / Isekai
    if any(k in text for k in ["isekai", "reincarnated", "villainess", "otome", "korean", "manhwa style"]):
        return "Korean Romance Fantasy / Isekai"
    
    # 9. Cozy / Cottagecore
    if any(k in text for k in ["cozy", "cottagecore", "small town", "low stakes", "wholesome", "magical bakery"]):
        return "Cozy / Cottagecore"
    
    # 10. Paranormal Romance
    if any(k in text for k in ["vampire", "ghost", "witch", "paranormal", "psychic", "medium"]):
        return "Paranormal Romance"
    
    # 11. High Fantasy Court Adventure
    if any(k in text for k in ["court", "throne", "kingdom", "royalty", "epic fantasy", "fae", "high fantasy"]):
        return "High Fantasy Court Adventure"
    
    # 12. Urban / Contemporary Fantasy Romance
    if any(k in text for k in ["urban fantasy", "modern day", "city", "contemporary fantasy", "hidden world"]):
        return "Urban / Contemporary Fantasy Romance"

    return "N/A"

def analyze_catalog(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"\n>>> Analyzing {file_path}...")
    df = pd.read_excel(file_path)
    
    # Find the right columns (handles both Speilburg and Bookends naming)
    syn_col = next((c for c in df.columns if 'Synopsis' in c), None)
    rom_yes_no_col = next((c for c in df.columns if 'Romantasy = Yes or No?' in c), None)
    rom_genre_col = next((c for c in df.columns if 'Romantasy Sub-Genre' in c), None)
    
    if not syn_col or not rom_yes_no_col or not rom_genre_col:
        print("Error: Could not find necessary columns for analysis.")
        return

    count = 0
    for idx, row in df.iterrows():
        synopsis = str(row[syn_col])
        subgenre = identify_romantasy_subgenre(synopsis)
        
        if subgenre != "N/A":
            df.at[idx, rom_yes_no_col] = "Yes"
            df.at[idx, rom_genre_col] = subgenre
            count += 1
        else:
            # Check if it was already marked as Romance/Fantasy to be safe
            df.at[idx, rom_yes_no_col] = "No"
            df.at[idx, rom_genre_col] = "N/A"
            
    df.to_excel(file_path, index=False)
    print(f"Analysis Complete! Classified {count} books as Romantasy.")

if __name__ == "__main__":
    # You can run it for both files
    analyze_catalog("Speilburg_Media_Catalog_Final.xlsx")
    analyze_catalog("Bookends_Literary_Catalog_Final.xlsx")
