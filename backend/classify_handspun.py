import pandas as pd
import os
import re
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from apply_jra_style import apply_styling
except ImportError:
    def apply_styling(path): pass

KEYWORD_MAP = [
    ("Werewolf / Shifter Romance",
     ["werewolf", "shifter", "alpha", "pack", "omega", "luna", "wolf",
      "shapeshifter", "bear shifter", "dragon shifter", "true mate"]),

    ("Monster Romance (Non-Shifter)",
     ["monster", "orc", "kraken", "alien", "beast", "creature", "demon lover",
      "minotaur", "tentacle", "beastman", "non-human"]),

    ("War College / Military Academy",
     ["war college", "military academy", "dragon rider", "fourth wing",
      "basgiath", "aerial", "flight school", "rider", "bonded dragon",
      "combat training", "lethal training"]),

    ("High-Stakes Games & Deadly Trials",
     ["trial", "deadly game", "tournament", "competition", "arena",
      "death match", "blood game", "lethal", "hunger game", "deadly trials",
      "magical tournament", "magical contest"]),

    ("Dark Academia Romantasy",
     ["dark academia", "secret society", "forbidden library", "magic school",
      "arcane academy", "magical academy", "university of magic",
      "scholar", "campus", "cursed school"]),

    ("Gothic Dark Romantasy",
     ["gothic", "haunted", "manor", "dark romance", "gloomy castle",
      "shadow court", "cursed castle", "decaying estate", "vampire lord",
      "immortal lord", "blood magic", "macabre", "vampiric"]),

    ("Korean Romance Fantasy / Isekai",
     ["isekai", "reincarnated", "villainess", "otome", "korean", "manhwa",
      "transmigrated", "possessed", "regression", "saintess", "empress",
      "transmigration"]),

    ("Mythology, Legend & Fairy Tale Retelling",
     ["retelling", "mythology", "greek god", "hades", "persephone",
      "fairy tale", "legend", "arthurian", "norse", "medusa", "circe",
      "orpheus", "gods and monsters", "greek myth", "norse myth"]),

    ("Cozy / Cottagecore",
     ["cozy", "cottagecore", "small town magic", "bakery", "low stakes",
      "wholesome", "botanical", "village witch", "flower shop",
      "magical inn", "low-stakes", "magical bakery"]),

    ("Paranormal Romance",
     ["vampire", "ghost", "witch", "paranormal", "psychic", "medium",
      "warlock", "necromancer", "haunting", "supernatural romance",
      "fae romance", "fairy", "coven", "demon", "succubus"]),

    ("Urban / Contemporary Fantasy Romance",
     ["urban fantasy", "modern day", "contemporary fantasy", "hidden world",
      "secret magic", "real world", "city magic", "supernatural city",
      "magic in the city", "hidden magic"]),

    ("High Fantasy Court Adventure",
     ["court", "throne", "kingdom", "royalty", "fae court", "high fantasy",
      "crown", "empire", "queen", "king", "prince", "realm", "dragon",
      "epic fantasy", "war", "political intrigue", "magic system",
      "fae", "elven", "magical kingdom", "fantasy", "sorcerer",
      "enchant", "spell", "magical", "magic"]),
]

ROMANTASY_SIGNALS = [
    "fantasy", "magic", "magical", "fae", "witch", "wizard", "sorcerer",
    "enchant", "spell", "dragon", "vampire", "ghost", "paranormal",
    "supernatural", "fairy", "realm", "kingdom", "court", "throne",
    "mytholog", "retelling", "werewolf", "shifter", "isekai",
    "romantasy", "gothic", "dark romance", "monster", "orc", "demon",
    "warlock", "necromancer", "psychic", "medium",
]

def is_romantasy(text: str) -> bool:
    t = text.lower()
    return any(sig in t for sig in ROMANTASY_SIGNALS)

def classify(synopsis: str, existing_subgenre: str = "") -> tuple:
    combined = (str(existing_subgenre) + " " + str(synopsis)).lower()
    if not is_romantasy(combined):
        return "No", ""
    for subgenre, keywords in KEYWORD_MAP:
        if any(k in combined for k in keywords):
            return "Yes", subgenre
    return "Yes", "High Fantasy Court Adventure"

excel_path = r"E:\Internship\PocketFM\handspun_romance_books_combined.xlsx"
print(f"Loading {excel_path}...")
df = pd.read_excel(excel_path)

for index, row in df.iterrows():
    syn = str(row.get("Synopsis (if available)", ""))
    # Use 'Original Series / Category' if it exists to aid classification
    old_cat = str(row.get("Original Series / Category", "")) if "Original Series / Category" in df.columns else ""
    
    rom, sub = classify(syn, old_cat)
    df.at[index, "Romantasy = Yes or No?"] = rom
    df.at[index, "Romantasy Sub-Genre of series"] = sub

df.to_excel(excel_path, index=False)
print("Classification complete!")
try:
    apply_styling(excel_path)
    print("Styling applied.")
except:
    pass
print("All done!")
