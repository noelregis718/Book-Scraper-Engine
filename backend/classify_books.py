import pandas as pd
import re

excel_path = r'e:\Internship\PocketFM\Books_Scraping_Template.xlsx'
print("Loading Excel file...")
df = pd.read_excel(excel_path, engine='openpyxl')

sub_genres = {
    "Werewolf / Shifter Romance": ["werewolf", "shifter", "wolf", "pack", "alpha", "omega", "lycan", "shapeshifter", "bear", "tiger", "wolves"],
    "Paranormal Romance": ["vampire", "witch", "ghost", "paranormal", "supernatural", "demon", "angel", "coven", "spirit", "haunted", "witches", "vampires", "ghosts", "demons", "angels", "psychic"],
    "High Fantasy Court Adventure": ["court", "kingdom", "fae", "prince", "princess", "throne", "crown", "realm", "elf", "elves", "royal", "queen", "king", "sword", "dragon", "dragons", "knight", "magic", "magical"],
    "Dark Academia Romantasy": ["academy", "school", "university", "library", "scholar", "magic school", "student", "professor", "college", "boarding school"],
    "Gothic Dark Romantasy": ["gothic", "dark", "curse", "shadow", "manor", "blood", "macabre"],
    "Monster Romance (Non-Shifter)": ["monster", "alien", "orc", "creature", "tentacle", "kraken"],
    "High-Stakes Games & Deadly Trials": ["trial", "tournament", "game", "deadly", "survive", "survival", "hunger games", "challenge", "arena", "assassin"],
    "Mythology, Legend & Fairy Tale Retelling": ["mythology", "greek", "hades", "persephone", "retelling", "fairy tale", "cinderella", "legend", "god", "goddess", "myth", "olympus"],
    "War College / Military Academy": ["war college", "rider", "dragon rider", "military", "cadet", "war", "rebellion", "soldier", "army"],
    "Cozy / Cottagecore": ["cozy", "tea", "shop", "bakery", "cottage", "familiar", "village", "small town magic", "inn"],
    "Korean Romance Fantasy / Isekai": ["isekai", "reincarnated", "transmigrated", "villainess", "duke", "empire", "korean", "manhwa"],
    "Urban / Contemporary Fantasy Romance": ["urban fantasy", "city", "modern", "detective", "police", "agency", "contemporary fantasy", "secret society"]
}

# General fantasy / paranormal keywords to detect "Romantasy"
romantasy_keywords = set()
for keywords in sub_genres.values():
    romantasy_keywords.update(keywords)
# Add some general sci-fi/fantasy terms just in case
romantasy_keywords.update(["sci-fi", "science fiction", "space", "planet", "spaceship", "futuristic", "time travel", "immortal", "mage", "wizard", "sorcerer", "spell"])

def classify_book(synopsis):
    synopsis_lower = str(synopsis).lower() if pd.notna(synopsis) else ""
    
    # Since the user stated all books from this category are Romantasy, we default to Yes.
    is_romantasy = True
    
    # Determine sub-genre (count matches to find best fit)
    best_genre = "Paranormal Romance" # Default fallback
    max_matches = 0
    
    for genre, keywords in sub_genres.items():
        matches = sum(1 for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', synopsis_lower))
        if matches > max_matches:
            max_matches = matches
            best_genre = genre
            
    if max_matches == 0:
        # Try to infer from general keywords
        if "magic" in synopsis_lower or "sword" in synopsis_lower:
            best_genre = "High Fantasy Court Adventure"
        else:
            best_genre = "Paranormal Romance" # Broad fallback
            
    return "Yes", best_genre

print("Classifying books...")
count_romantasy = 0
for idx, row in df.iterrows():
    synopsis = row['Synopsis (if available)']
    is_romantasy, sub_genre = classify_book(synopsis)
    df.at[idx, 'Romantasy = Yes or No?'] = is_romantasy
    df.at[idx, 'Romantasy Sub-Genre of series'] = sub_genre
    if is_romantasy == "Yes":
        count_romantasy += 1

print(f"Identified {count_romantasy} Romantasy books out of {len(df)}.")
print("Saving to Excel...")
df.to_excel(excel_path, index=False, engine='openpyxl')
print("Done!")
