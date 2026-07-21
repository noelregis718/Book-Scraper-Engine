import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

EXCEL_FILE = r"E:\Internship\PocketFM\BookEnds_Literary_Agency_Genre_Subgenre_Mapped.xlsx"

# Base Genre Keywords
GENRE_MAP = {
    "Romantasy": ["romantasy", "fantasy romance", "paranormal romance", "fae romance"],
    "Crime Thriller": ["crime", "thriller", "mystery", "suspense", "detective", "murder"],
    "Romance Drama": ["romance", "contemporary romance", "love story", "drama", "new adult romance"],
    "Fantasy": ["fantasy", "magic", "high fantasy", "epic fantasy"]
}

# Sub-Genre Maps
KEYWORD_MAP_ROMANTASY = [
    ("Werewolf / Shifter Romance", ["werewolf", "shifter", "alpha", "pack", "omega", "luna", "wolf", "lycan"]),
    ("Monster Romance (Non-Shifter)", ["monster", "orc", "kraken", "alien", "beast", "creature", "demon lover", "tentacle"]),
    ("Mythology, Legend & Fairy Tale Retelling", ["retelling", "mythology", "greek god", "hades", "persephone", "fairy tale", "legend", "arthurian", "norse", "anansi", "medusa", "circe", "beauty and the beast"]),
    ("War College / Military Academy", ["war college", "military academy", "dragon rider", "fourth wing", "basgiath", "aerial", "flight school", "training camp", "academy"]),
    ("High-Stakes Games & Deadly Trials", ["trial", "deadly game", "tournament", "competition", "survival", "arena", "hunger game", "death match"]),
    ("Dark Academia Romantasy", ["dark academia", "secret society", "forbidden library", "ancient university", "campus", "cursed school", "magic school"]),
    ("Gothic Dark Romantasy", ["gothic", "haunted", "manor", "dark romance", "shadow court", "vampire lord"]),
    ("Korean Romance Fantasy / Isekai", ["isekai", "reincarnated", "villainess", "otome", "korean", "manhwa", "transmigrated"]),
    ("Cozy / Cottagecore", ["cozy", "cottagecore", "small town magic", "bakery", "low stakes", "wholesome", "village witch", "magical inn"]),
    ("Paranormal Romance", ["vampire", "ghost", "witch", "paranormal", "psychic", "warlock", "necromancer", "supernatural romance"]),
    ("High Fantasy Court Adventure", ["court", "throne", "kingdom", "royalty", "fae court", "high fantasy", "crown", "empire", "queen", "king", "epic fantasy", "political intrigue"]),
    ("Urban / Contemporary Fantasy Romance", ["urban fantasy", "modern day", "contemporary fantasy", "hidden world", "city magic", "supernatural city"])
]

KEYWORD_MAP_CT = [
    ("Police, PI & Investigative", ["police", "pi ", "private investigator", "detective", "fbi", "cia", "investigation", "cop", "homicide"]),
    ("Cozy Mystery & Amateur Sleuth", ["cozy mystery", "amateur sleuth", "baking mystery", "small town mystery", "cat sleuth", "cozy"]),
    ("Historical Crime & Mystery", ["historical crime", "historical mystery", "victorian mystery", "1920s mystery", "historical thriller"]),
    ("Psychological / Domestic Thriller", ["psychological thriller", "domestic thriller", "marriage thriller", "unreliable narrator", "gaslighting", "mind games"]),
    ("Serial Killer / Psychological Predator", ["serial killer", "predator", "profiler", "serial murder", "psychopath", "sociopath"]),
    ("Action Crime / Dark Thriller", ["action thriller", "dark thriller", "gritty", "assassin", "hitman", "cartel", "gunfight", "action crime"]),
    ("Mafia & Organized Crime", ["mafia", "organized crime", "mob", "cosa nostra", "yakuza", "triad", "cartel", "syndicate", "don "]),
    ("Heist & Caper Fiction", ["heist", "caper", "con artist", "thief", "robbery", "bank job", "art theft", "jewel thief"]),
    ("Legal, Political & Conspiracy Thriller", ["legal thriller", "political thriller", "conspiracy", "lawyer", "courtroom", "senator", "president", "white house", "cover-up"]),
    ("Military / Spy / Espionage Thriller", ["military thriller", "spy ", "espionage", "mi6", "black ops", "special forces", "kgb", "intelligence", "navy seal"]),
    ("Super Natural Thriller / Low Fantasy Thriller / Crime Thriller Universe", ["supernatural thriller", "occult detective", "low fantasy thriller", "crime thriller universe", "paranormal thriller"]),
    ("Survival Thriller", ["survival thriller", "wilderness survival", "stranded", "remote island", "locked room", "trapped", "escape"])
]

def classify_genre(text):
    text = text.lower()
    for genre, keywords in GENRE_MAP.items():
        if any(k in text for k in keywords):
            return genre
    return ""

def classify_subgenre(text, genre):
    text = text.lower()
    if genre == "Romantasy":
        for subgenre, keywords in KEYWORD_MAP_ROMANTASY:
            if any(k in text for k in keywords):
                return subgenre
        return "High Fantasy Court Adventure" # Default for Romantasy if no match
    elif genre == "Crime Thriller":
        for subgenre, keywords in KEYWORD_MAP_CT:
            if any(k in text for k in keywords):
                return subgenre
        return "Psychological / Domestic Thriller" # Default for CT if no match
    
    return "" # No subgenre for Fantasy/Romance Drama according to strict list, or just leave blank

def main():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)
    
    # Ensure columns exist
    if 'Genre' not in df.columns:
        df['Genre'] = ''
    if 'Sub-Genre' not in df.columns:
        df['Sub-Genre'] = ''
            
    mapped_count = 0
    
    for idx, row in df.iterrows():
        title = str(row.get('Name of Series', '')).strip()
        synopsis = str(row.get('Synopsis (if available)', '')).strip()
        tags = str(row.get('Genre tags- Up to 7 tags', '')).strip()
        current_genre = str(row.get('Genre', '')).strip()
        current_sub = str(row.get('Sub-Genre', '')).strip()
        
        if title.lower() == 'nan' or not title:
            continue
            
        combined_text = tags + " " + synopsis + " " + title
        
        needs_update = False
        
        if not current_genre or current_genre.lower() == 'nan' or current_genre == 'Unknown' or current_genre == 'Needs Mapping':
            new_genre = classify_genre(combined_text)
            df.at[idx, 'Genre'] = new_genre
            current_genre = new_genre
            needs_update = True
            
        if not current_sub or current_sub.lower() == 'nan' or current_sub == 'Needs Mapping':
            new_sub = classify_subgenre(combined_text, current_genre)
            df.at[idx, 'Sub-Genre'] = new_sub
            needs_update = True
            
        if needs_update:
            mapped_count += 1

    print(f"Saving {EXCEL_FILE} after mapping {mapped_count} rows...")
    df.to_excel(EXCEL_FILE, index=False)
    print("ALL DONE!")

if __name__ == '__main__':
    main()
