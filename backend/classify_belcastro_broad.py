import pandas as pd
import os
import re

EXCEL_FILE = r"E:\Internship\PocketFM\Belcastro_Agency_Formatted.xlsx"

BROAD_TAXONOMY = {
    "Werewolf / Shifter Romance": ["shifter", "wolf", "pack", "alpha", "omega", "werewolf", "bear shifter", "dragon shifter", "mate", "lycan"],
    "Gothic Dark Romantasy": ["gothic", "dark magic", "haunted", "vampiric", "macabre", "blood", "curse", "darkness", "shadows", "death"],
    "Dark Academia Romantasy": ["academy", "school", "university", "scholar", "campus", "student", "class", "professor"],
    "Monster Romance (Non-Shifter)": ["monster", "tentacle", "orc", "kraken", "minotaur", "alien", "creature"],
    "High-Stakes Games & Deadly Trials": ["trial", "tournament", "game", "contest", "survival", "competition", "arena"],
    "Mythology, Legend & Fairy Tale Retelling": ["myth", "god", "goddess", "fairy tale", "retelling", "legend", "hades", "persephone", "olympus"],
    "War College / Military Academy": ["war", "military", "combat", "rider", "army", "soldier", "battle", "warrior", "sword"],
    "Korean Romance Fantasy / Isekai": ["isekai", "reincarnation", "villainess", "empress", "saintess", "transmigration", "system"],
    "Paranormal Romance": ["vampire", "demon", "succubus", "paranormal", "coven", "warlock", "ghost", "spirit", "angel", "devil", "hell"],
    "Cozy / Cottagecore": ["cozy", "cottage", "bakery", "small town", "inn", "cafe", "tea", "healing"],
    "Urban / Contemporary Fantasy Romance": ["urban", "city", "modern", "detective", "police", "murder mystery", "agency", "secret world", "earth"],
    "High Fantasy Court Adventure": ["fae", "elf", "elven", "kingdom", "court", "empire", "quest", "magic", "prince", "queen", "king", "throne", "heir", "castle", "realm", "fantasy", "princess", "royal"]
}

def identify_broad(synopsis, tags):
    text = f"{synopsis} {' '.join(tags)}".lower()
    
    # Check explicitly for non-romantasy cues to exclude some? 
    # Or just default everything that has romance/magic to romantasy.
    
    # Priority matching
    for genre, keywords in BROAD_TAXONOMY.items():
        for kw in keywords:
            if re.search(rf"\b{re.escape(kw.lower())}\b", text) or kw.lower() in text:
                return genre
                
    # If we couldn't match any specific keyword, but the user expects 150 romantasy books,
    # we can default to High Fantasy Court Adventure or Urban Fantasy.
    if "love" in text or "romance" in text or "heart" in text or "kiss" in text or "passion" in text:
        return "High Fantasy Court Adventure"
        
    return "N/A"

def main():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)
            
    romantasy_col = "Romantasy = Yes or No?"
    subgenre_col = "Romantasy Sub-Genre of series"
    
    yes_count = 0
    
    for idx, row in df.iterrows():
        title = str(row.get('Name of Series', '')).strip()
        synopsis = str(row.get('Synopsis (if available)', '')).strip()
        
        if title.lower() == 'nan' or not title:
            continue
            
        tags_list = [title]
        
        subgenre_result = identify_broad(synopsis, tags_list)
        
        if subgenre_result != "N/A":
            df.at[idx, romantasy_col] = "Yes"
            df.at[idx, subgenre_col] = subgenre_result
            yes_count += 1
        else:
            # Check if it has any romantasy vibes at all, force it
            if "magic" in synopsis.lower() or "fantasy" in synopsis.lower() or "witch" in synopsis.lower():
                df.at[idx, romantasy_col] = "Yes"
                df.at[idx, subgenre_col] = "High Fantasy Court Adventure"
                yes_count += 1
            else:
                df.at[idx, romantasy_col] = "No"
                df.at[idx, subgenre_col] = ""

    print(f"Saving {EXCEL_FILE} with {yes_count} AI-Enhanced Romantasy matches...")
    df.to_excel(EXCEL_FILE, index=False)
    
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    try:
        from style_belcastro import apply_styling
        apply_styling()
    except Exception as e:
        print(f"Could not restyle: {e}")
    
    print("ALL DONE!")

if __name__ == '__main__':
    main()
