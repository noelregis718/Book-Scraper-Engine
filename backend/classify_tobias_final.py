import pandas as pd
import os
import re

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

# Keyword map for each sub-genre
KEYWORD_MAP = [
    # (sub-genre name, [keywords that match it])
    ("Werewolf / Shifter Romance",
     ["werewolf", "shifter", "alpha", "pack", "omega", "luna", "wolf"]),

    ("Monster Romance (Non-Shifter)",
     ["monster", "orc", "kraken", "alien", "beast", "creature", "demon lover"]),

    ("Mythology, Legend & Fairy Tale Retelling",
     ["retelling", "mythology", "greek god", "hades", "persephone", "fairy tale", "legend",
      "arthurian", "norse", "anansi", "medusa", "circe", "orpheus"]),

    ("War College / Military Academy",
     ["war college", "military academy", "dragon rider", "fourth wing", "basgiath",
      "aerial", "flight school", "training camp", "rider", "bonded dragon"]),

    ("High-Stakes Games & Deadly Trials",
     ["trial", "deadly game", "tournament", "competition", "survival", "arena",
      "hunger game", "death match", "blood game", "lethal"]),

    ("Dark Academia Romantasy",
     ["dark academia", "secret society", "forbidden library", "ancient university",
      "campus", "scholarly", "cursed school", "arcane academy", "magic school"]),

    ("Gothic Dark Romantasy",
     ["gothic", "haunted", "manor", "dark romance", "gloomy castle", "shadow court",
      "cursed castle", "decaying estate", "vampire lord", "immortal lord"]),

    ("Korean Romance Fantasy / Isekai",
     ["isekai", "reincarnated", "villainess", "otome", "korean", "manhwa",
      "transmigrated", "possessed", "regression"]),

    ("Cozy / Cottagecore",
     ["cozy", "cottagecore", "small town magic", "bakery", "low stakes",
      "wholesome", "botanical", "village witch", "flower shop", "magical inn"]),

    ("Paranormal Romance",
     ["vampire", "ghost", "witch", "paranormal", "psychic", "medium",
      "warlock", "necromancer", "haunting", "supernatural romance",
      "fae romance", "fairy"]),

    ("High Fantasy Court Adventure",
     ["court", "throne", "kingdom", "royalty", "fae court", "high fantasy",
      "crown", "empire", "queen", "king", "prince", "realm", "dragon",
      "epic fantasy", "war", "political intrigue", "magic system"]),

    ("Urban / Contemporary Fantasy Romance",
     ["urban fantasy", "modern day", "contemporary fantasy", "hidden world",
      "secret magic", "real world", "city magic", "supernatural city"]),
]

def classify_from_genre_and_synopsis(genre_text, synopsis_text=""):
    """Match against genre field first, then synopsis for richer data."""
    text = (str(genre_text) + " " + str(synopsis_text)).lower()

    for subgenre, keywords in KEYWORD_MAP:
        if any(k in text for k in keywords):
            return subgenre

    return None  # Not romantasy

def analyze_tobias_final(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"\n>>> Analyzing {file_path}...")
    df = pd.read_excel(file_path)

    # Detect columns (2nd and 3rd from last)
    romantasy_col = "Romantasy = Yes or No?"
    subgenre_col = "Romantasy Sub-Genre of series"

    if romantasy_col not in df.columns or subgenre_col not in df.columns:
        print(f"Error: Could not find columns '{romantasy_col}' or '{subgenre_col}'")
        print("Available columns:", df.columns.tolist())
        return

    yes_count = 0
    for idx, row in df.iterrows():
        genre_text = str(row.get(subgenre_col, ""))
        synopsis_text = str(row.get("Synopsis (if available)", ""))

        result = classify_from_genre_and_synopsis(genre_text, synopsis_text)

        if result:
            df.at[idx, romantasy_col] = "Yes"
            df.at[idx, subgenre_col] = result
            yes_count += 1
        else:
            df.at[idx, romantasy_col] = "No"
            df.at[idx, subgenre_col] = ""

    df.to_excel(file_path, index=False)
    print(f"Done! Classified {yes_count} books as Romantasy out of {len(df)} total.")

    # Reapply styling
    from apply_jra_style import apply_styling
    apply_styling(file_path)
    print("Styling reapplied.")

if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    analyze_tobias_final(os.path.join(base, "Tobias_All_Books_FINAL.xlsx"))
