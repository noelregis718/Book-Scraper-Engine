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
    ("Korean Romance Fantasy / Isekai",
     ["isekai", "reincarnated", "villainess", "otome", "korean", "manhwa", "transmigrated", "possessed", "regression", "saintess", "transmigration", "system"]),

    ("Werewolf / Shifter Romance",
     ["werewolf", "shifter", "pack", "luna", "wolf", "shapeshifter", "bear shifter", "dragon shifter", "true mate", "fated mate", "lycan", "alpha", "omega", "omegaverse", "mating", "mate", "bite"]),

    ("Monster Romance (Non-Shifter)",
     ["monster", "orc", "kraken", "alien", "beast", "creature", "demon", "minotaur", "tentacle", "beastman", "non-human", "gargoyle", "succubus", "incubus", "devil", "cyborg", "mutant"]),

    ("War College / Military Academy",
     ["war college", "military academy", "dragon rider", "fourth wing", "basgiath", "aerial", "flight school", "rider", "bonded dragon", "combat training", "lethal training"]),

    ("High-Stakes Games & Deadly Trials",
     ["trial", "deadly game", "tournament", "competition", "arena", "death match", "blood game", "lethal", "hunger game", "deadly trials", "magical tournament"]),

    ("Dark Academia Romantasy",
     ["dark academia", "secret society", "forbidden library", "magic school", "arcane academy", "magical academy", "university of magic", "scholar", "campus", "cursed school", "academy"]),

    ("Gothic Dark Romantasy",
     ["gothic", "haunted", "manor", "dark romance", "gloomy castle", "shadow court", "cursed castle", "decaying estate", "vampire lord", "immortal lord", "blood magic", "macabre", "vampiric"]),

    ("Mythology, Legend & Fairy Tale Retelling",
     ["retelling", "mythology", "greek god", "hades", "persephone", "fairy tale", "legend", "arthurian", "norse", "medusa", "circe", "orpheus", "gods and monsters", "olympus", "folklore", "camelot", "wish", "prophecy", "god", "goddess"]),

    ("Cozy / Cottagecore",
     ["cozy", "cottagecore", "small town magic", "bakery", "low stakes", "wholesome", "botanical", "village witch", "flower shop", "magical inn", "low-stakes"]),

    ("Paranormal Romance",
     ["vampire", "ghost", "witch", "paranormal", "psychic", "medium", "warlock", "necromancer", "haunting", "supernatural", "fairy", "coven", "spirit", "angel", "genie", "magic", "witches", "vampires", "ghosts", "vamp", "fang", "mage", "wizard", "sorcerer", "seer"]),

    ("Urban / Contemporary Fantasy Romance",
     ["urban fantasy", "modern day", "contemporary fantasy", "hidden world", "secret magic", "real world", "city magic", "supernatural city", "magic in the city", "hidden magic", "modern magic", "superpower", "hero", "villain"]),

    ("High Fantasy Court Adventure",
     ["court", "throne", "kingdom", "royalty", "fae", "high fantasy", "crown", "empire", "queen", "king", "prince", "realm", "dragon", "epic fantasy", "war", "political intrigue", "magic system", "elven", "fantasy", "enchant", "spell", "magical", "curse", "immortal", "sword", "knight", "castle", "royal", "princess"]),
]

ROMANTASY_SIGNALS = [
    "fantasy", "magic", "magical", "fae", "witch", "wizard", "sorcerer",
    "enchant", "spell", "dragon", "vampire", "ghost", "paranormal",
    "supernatural", "fairy", "realm", "kingdom", "court", "throne",
    "mytholog", "retelling", "werewolf", "shifter", "isekai",
    "romantasy", "gothic", "dark romance", "monster", "orc", "demon",
    "warlock", "necromancer", "psychic", "medium", "genie", "alien",
    "angel", "spirit", "curse", "immortal", "succubus", "lycan", "alpha", "omega",
    "camelot", "prophecy", "vamp", "fang", "mage", "seer",
    "sword", "knight", "castle", "royal", "princess", "prince", "king", "queen",
    "mate", "bite", "cyborg", "mutant", "superpower", "villain", "hero", "god", "goddess"
]

def classify(synopsis: str, title: str) -> tuple:
    combined = (str(title) + " " + str(synopsis)).lower()
    
    # Use word boundaries for all signals to avoid partial matches
    is_rom = False
    for sig in ROMANTASY_SIGNALS:
        if sig in combined:
            is_rom = True
            break
            
    for subgenre, keywords in KEYWORD_MAP:
        for k in keywords:
            if k in combined:
                return "Yes", subgenre
                
    if is_rom:
        return "Yes", "Paranormal Romance"
        
    return "No", ""

excel_path = r"E:\Internship\PocketFM\first_for_romance_books.xlsx"
print(f"Loading {excel_path}...")
df = pd.read_excel(excel_path)

for index, row in df.iterrows():
    syn = str(row.get("Synopsis (if available)", ""))
    title = str(row.get("Name of Series", ""))
    
    rom, sub = classify(syn, title)
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
