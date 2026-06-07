import pandas as pd
import re
import sys
import os

TAXONOMY = {
    "High Fantasy Court Adventure": [
        "fae", "elven", "elf", "kingdom", "court", "empire", "epic", "crown", "prince", "princess", "queen", "king", 
        "throne", "heir", "castle", "realm", "rebellion", "sword", "magic", "sorcery", "high fantasy", "royalty", "emperor", "empress"
    ],
    "Gothic Dark Romantasy": [
        "gothic", "dark magic", "haunted", "vampiric", "macabre", "blood", "curse", "death", "graveyard", "necromancer", 
        "mansion", "shadows", "darkness", "brooding", "sinister", "monster", "demon"
    ],
    "Dark Academia Romantasy": [
        "academy", "secret society", "school", "university", "scholar", "campus", "library", "professors", "students", 
        "dark academia", "institute", "college", "boarding school", "dormitory"
    ],
    "Monster Romance (Non-Shifter)": [
        "monster", "tentacle", "orc", "kraken", "minotaur", "beast", "alien", "demon", "gargoyle", "creature", "non-human"
    ],
    "Werewolf / Shifter Romance": [
        "shifter", "wolf", "bear", "dragon", "pack", "alpha", "omega", "mate", "lycan", "werewolf", "fated", "luna"
    ],
    "High-Stakes Games & Deadly Trials": [
        "trial", "tournament", "game", "contest", "survival", "arena", "hunger games", "competition", "deadly", "compete"
    ],
    "Mythology, Legend & Fairy Tale Retelling": [
        "myth", "greek", "norse", "retelling", "fairy tale", "god", "goddess", "hades", "persephone", "olympus", 
        "beauty and the beast", "cinderella", "legend", "folklore"
    ],
    "War College / Military Academy": [
        "war college", "military", "dragon rider", "combat", "training", "soldier", "army", "warrior", "squad", "legion", "commander"
    ],
    "Korean Romance Fantasy / Isekai": [
        "isekai", "reincarnation", "villainess", "empress", "saintess", "transmigration", "manhwa", "korean", "past life", "reborn"
    ],
    "Paranormal Romance": [
        "vampire", "demon", "succubus", "witch", "coven", "warlock", "ghost", "spirit", "paranormal", "supernatural", "angel"
    ],
    "Cozy / Cottagecore": [
        "cozy", "cottage", "bakery", "small town", "tea", "coffee", "inn", "tavern", "low-stakes", "healing", "wholesome", "familiar"
    ],
    "Urban / Contemporary Fantasy Romance": [
        "urban", "city", "hidden world", "modern", "detective", "agency", "underworld", "new york", "london", "contemporary"
    ]
}

ROMANCE_KEYWORDS = ["love", "romance", "desire", "passion", "kiss", "heart", "lover", "mate", "bond", "seduction", "attraction", "feelings", "marriage", "betrothal", "wedding", "husband", "wife", "boyfriend", "girlfriend"]

def aggressive_classify():
    file_path = r'E:\Internship\PocketFM\deborah_harris_merged.xlsx'
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return
        
    print(f"Loading {file_path}...")
    df = pd.read_excel(file_path)
    
    count_yes = 0
    count_no = 0
    
    for idx, row in df.iterrows():
        synopsis = str(row.get('Synopsis (if available)', '')).lower()
        title = str(row.get('Name of Series', '')).lower()
        
        text_to_analyze = synopsis + " " + title
        
        # If text is empty, leave as N/A
        if not text_to_analyze.strip() or text_to_analyze == 'nan ':
            df.at[idx, 'Romantasy Sub-Genre of series'] = 'N/A'
            df.at[idx, 'Romantasy = Yes or No?'] = 'No'
            continue
            
        # Score each sub-genre
        scores = {genre: 0 for genre in TAXONOMY.keys()}
        
        for genre, keywords in TAXONOMY.items():
            for kw in keywords:
                # Use regex word boundary
                pattern = rf"\b{re.escape(kw)}\b"
                matches = len(re.findall(pattern, text_to_analyze))
                scores[genre] += matches
                
        # Find the max score
        best_genre = max(scores, key=scores.get)
        max_score = scores[best_genre]
        
        # Check romance score
        romance_score = 0
        for kw in ROMANCE_KEYWORDS:
            pattern = rf"\b{re.escape(kw)}\b"
            romance_score += len(re.findall(pattern, text_to_analyze))
            
        # Decision: If there's ANY fantasy sub-genre hit > 0, we consider it.
        # But to be 'Romantasy', it should either have romance keywords OR be a genre that implies romance (like Werewolf/Shifter Romance, Monster Romance, Paranormal Romance)
        inherently_romantic = ["Monster Romance (Non-Shifter)", "Werewolf / Shifter Romance", "Paranormal Romance", "Gothic Dark Romantasy", "Korean Romance Fantasy / Isekai"]
        
        is_romantasy = False
        if max_score > 0:
            if romance_score > 0 or best_genre in inherently_romantic:
                is_romantasy = True
            # Even if no strict romance keywords, the user said "most of the books over there are romantasy". 
            # If it hits fantasy tags heavily (>1), assume it's romantasy.
            elif max_score > 1:
                is_romantasy = True

        if is_romantasy:
            df.at[idx, 'Romantasy Sub-Genre of series'] = best_genre
            df.at[idx, 'Romantasy = Yes or No?'] = 'Yes'
            count_yes += 1
        else:
            df.at[idx, 'Romantasy Sub-Genre of series'] = 'N/A'
            df.at[idx, 'Romantasy = Yes or No?'] = 'No'
            count_no += 1
            
    print(f"Classification complete! Found {count_yes} Romantasy books and {count_no} Non-Romantasy/Unknown.")
    print("Saving Excel file...")
    
    df.to_excel(file_path, index=False)
    
    try:
        from style_books_authors import apply_styling
        apply_styling(file_path)
    except Exception as e:
        print(f"Could not apply styling: {e}")
        
    print("ALL DONE!")

if __name__ == "__main__":
    aggressive_classify()
