import pandas as pd
import sys
import os
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from apply_jra_style import apply_styling
except ImportError:
    def apply_styling(p): pass

EXCEL_FILE = r'E:\Internship\PocketFM\dragonblade_books_combined.xlsx'

# The exact subgenres the user specified
SUBGENRE_MAP = {
    "High Fantasy Court Adventure": [
        "court", "king", "queen", "prince", "princess", "empire", "kingdom", "throne", "crown", "royal", "realm", "high fantasy", "elf", "elves", "fae"
    ],
    "Gothic Dark Romantasy": [
        "gothic", "vampire", "blood", "darkness", "shadow", "demon", "devil", "hell", "curse", "haunted", "death"
    ],
    "Dark Academia Romantasy": [
        "academia", "academy", "school", "university", "professor", "student", "study", "library", "dark academia"
    ],
    "Monster Romance (Non-Shifter)": [
        "monster", "creature", "orc", "goblin", "troll", "alien", "tentacle", "beast"
    ],
    "Werewolf / Shifter Romance": [
        "shifter", "wolf", "werewolf", "pack", "alpha", "omega", "mate", "luna", "lycan", "bear", "dragon shifter"
    ],
    "High-Stakes Games & Deadly Trials": [
        "trial", "game", "tournament", "survive", "deadly", "hunger games", "competition", "arena"
    ],
    "Mythology, Legend & Fairy Tale Retelling": [
        "myth", "legend", "fairy tale", "retelling", "god", "goddess", "hades", "persephone", "zeus", "olympus", "cinderella", "beauty and the beast"
    ],
    "War College / Military Academy": [
        "war college", "military academy", "soldier", "warrior", "army", "commander", "general", "battle", "war"
    ],
    "Korean Romance Fantasy / Isekai": [
        "isekai", "reincarnat", "system", "villainess", "korean", "manhwa"
    ],
    "Paranormal Romance": [
        "paranormal", "ghost", "spirit", "witch", "warlock", "magic", "spell", "coven", "mage", "sorcer"
    ],
    "Cozy / Cottagecore": [
        "cozy", "cottage", "tavern", "inn", "baking", "coffee", "tea", "village", "small town", "heartwarming", "wholesome"
    ],
    "Urban / Contemporary Fantasy Romance": [
        "urban", "city", "modern", "detective", "police", "agency", "vampire hunter"
    ]
}

# The catch-all aggressive signal list for 'Yes' vs 'No'
ROMANTASY_SIGNALS = [
    "magic", "dragon", "fae", "fairy", "witch", "wizard", "warlock", "spell", "curse", 
    "vampire", "werewolf", "shifter", "wolf", "alpha", "pack", "mate", "demon", "angel", 
    "ghost", "spirit", "supernatural", "paranormal", "fantasy", "kingdom", "throne", 
    "crown", "sword", "myth", "god", "goddess", "prophecy", "power", "realm", "elf", "elves", 
    "creature", "beast", "monster", "academy", "sorcer", "mage", "blood", "shadow", "immortal"
]

print("Loading dragonblade sheet...")
df = pd.read_excel(EXCEL_FILE)

count_yes = 0
count_no = 0

for index, row in df.iterrows():
    title = str(row.get('Name of Series', '')).lower()
    synopsis = str(row.get('Synopsis (if available)', '')).lower()
    
    combined = title + " " + synopsis
    
    # Check if ANY romantasy signal is in the combined text (Aggressive Substring Match)
    is_romantasy = False
    for sig in ROMANTASY_SIGNALS:
        if sig in combined:
            is_romantasy = True
            break
            
    if is_romantasy:
        df.at[index, 'Romantasy = Yes or No?'] = 'Yes'
        count_yes += 1
        
        # Determine subgenre
        assigned_subgenre = "Paranormal Romance" # default fallback
        found = False
        
        # Priority mapping
        for genre, keywords in SUBGENRE_MAP.items():
            for kw in keywords:
                if kw in combined:
                    assigned_subgenre = genre
                    found = True
                    break
            if found:
                break
                
        df.at[index, 'Romantasy Sub-Genre of series'] = assigned_subgenre
    else:
        df.at[index, 'Romantasy = Yes or No?'] = 'No'
        df.at[index, 'Romantasy Sub-Genre of series'] = ''
        count_no += 1

print(f"Classification complete! Yes: {count_yes}, No: {count_no}")
df.to_excel(EXCEL_FILE, index=False)
try:
    apply_styling(EXCEL_FILE)
except:
    pass
print("Saved and styled.")
