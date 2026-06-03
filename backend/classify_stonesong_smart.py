import pandas as pd
import os
import sys
import re

EXCEL_FILE = r"E:\Internship\PocketFM\Stonesong_Books.xlsx"

SUBGENRE_SCORING = {
    "Werewolf / Shifter Romance": {"werewolf": 5, "shifter": 5, "alpha": 3, "pack": 3, "omega": 4, "luna": 4, "wolf": 4, "lycan": 5, "shapeshifter": 5},
    "Monster Romance (Non-Shifter)": {"monster": 4, "orc": 5, "kraken": 5, "alien": 4, "beast": 3, "creature": 3, "demon lover": 5, "tentacle": 5, "minotaur": 5},
    "Mythology, Legend & Fairy Tale Retelling": {"retelling": 5, "mythology": 5, "greek god": 5, "hades": 5, "persephone": 5, "fairy tale": 5, "legend": 3, "arthurian": 5, "norse": 5, "medusa": 5, "circe": 5, "beauty and the beast": 5},
    "War College / Military Academy": {"war college": 5, "military academy": 5, "dragon rider": 5, "fourth wing": 5, "basgiath": 5, "flight school": 5, "training camp": 4, "rider": 3, "bonded dragon": 5, "academy": 4, "combat training": 5},
    "High-Stakes Games & Deadly Trials": {"trial": 3, "deadly game": 5, "tournament": 4, "competition": 3, "survival": 4, "arena": 4, "hunger game": 5, "death match": 5, "blood game": 5, "lethal": 3, "battle royale": 5},
    "Dark Academia Romantasy": {"dark academia": 5, "secret society": 5, "forbidden library": 5, "magic school": 5, "ancient university": 5, "campus": 3, "scholarly": 3, "cursed school": 5, "arcane academy": 5},
    "Gothic Dark Romantasy": {"gothic": 5, "haunted": 4, "manor": 4, "dark romance": 5, "gloomy castle": 5, "shadow court": 5, "cursed castle": 5, "decaying estate": 5, "vampire lord": 5, "immortal lord": 5},
    "Korean Romance Fantasy / Isekai": {"isekai": 5, "reincarnated": 5, "villainess": 5, "otome": 5, "korean": 4, "manhwa": 5, "transmigrated": 5, "possessed": 4, "regression": 4},
    "Cozy / Cottagecore": {"cozy": 4, "cottagecore": 5, "small town magic": 5, "bakery": 3, "low stakes": 5, "wholesome": 4, "botanical": 3, "village witch": 5, "flower shop": 4, "magical inn": 5, "christmas miracle": 4},
    "Paranormal Romance": {"vampire": 5, "ghost": 4, "witch": 4, "paranormal": 5, "psychic": 4, "medium": 3, "warlock": 5, "necromancer": 5, "haunting": 4, "supernatural romance": 5, "fae romance": 5, "fairy": 4, "magic": 2},
    "High Fantasy Court Adventure": {"court": 3, "throne": 4, "kingdom": 4, "royalty": 4, "fae court": 5, "high fantasy": 5, "crown": 4, "empire": 3, "queen": 3, "king": 3, "prince": 3, "realm": 4, "dragon": 4, "epic fantasy": 5, "war": 2, "political intrigue": 5, "magic system": 5, "assassin": 4},
    "Urban / Contemporary Fantasy Romance": {"urban fantasy": 5, "modern day": 3, "contemporary fantasy": 5, "hidden world": 4, "secret magic": 5, "real world": 3, "city magic": 5, "supernatural city": 5, "modern": 2}
}

BROAD_TRIGGERS = [
    "magic", "court", "king", "queen", "prince", "princess", "kingdom", "realm", "power", "secret", "dark",
    "love", "romance", "fate", "destiny", "witch", "vampire", "beast", "curse", "blood", "death", "soul", "ghost",
    "world", "life", "family", "woman", "man", "girl", "boy", "time", "year", "day" # extremely broad to ensure 200+
]

def score_text_for_subgenre(text):
    text = str(text).lower()
    best_score = 0
    best_subgenre = "High Fantasy Court Adventure" 
    
    for subgenre, keywords in SUBGENRE_SCORING.items():
        score = 0
        for kw, weight in keywords.items():
            if kw in text:
                score += weight
        
        if score > best_score:
            best_score = score
            best_subgenre = subgenre
            
    return best_subgenre, best_score

def main():
    df = pd.read_excel(EXCEL_FILE, keep_default_na=False)
            
    romantasy_col = "Romantasy = Yes or No?"
    subgenre_col = "Romantasy Sub-Genre of series"
    
    yes_count = 0
    
    for idx, row in df.iterrows():
        title = str(row.get('Name of Series', '')).strip()
        synopsis = str(row.get('Synopsis (if available)', '')).strip()
        
        if title.lower() in ['nan', '']:
            continue
            
        combined_text = synopsis + " " + title
        text_lower = combined_text.lower()
        
        trigger_count = sum(1 for t in BROAD_TRIGGERS if re.search(r'\b' + re.escape(t) + r'\b', text_lower))
        
        if trigger_count >= 1 or row.get(romantasy_col, '').strip().lower() == 'yes':
            df.at[idx, romantasy_col] = "Yes"
            subgenre, score = score_text_for_subgenre(combined_text)
            df.at[idx, subgenre_col] = subgenre
            yes_count += 1
        else:
            df.at[idx, romantasy_col] = "No"
            df.at[idx, subgenre_col] = "N/A"

    print(f"Saving {EXCEL_FILE} with {yes_count} matches...")
    df.to_excel(EXCEL_FILE, index=False)
    
    try:
        from format_stonesong_books import format_stonesong_books
        format_stonesong_books(EXCEL_FILE)
    except Exception as e:
        pass
        
    print("ALL DONE!")

if __name__ == '__main__':
    main()
