import pandas as pd
import os
import re

# ── The exact 12 sub-genres the user specified ──────────────────────
KEYWORD_MAP = [
    # Priority order matters — more specific first

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

    # Broadest — last resort for anything fantasy+romance
    ("High Fantasy Court Adventure",
     ["court", "throne", "kingdom", "royalty", "fae court", "high fantasy",
      "crown", "empire", "queen", "king", "prince", "realm", "dragon",
      "epic fantasy", "war", "political intrigue", "magic system",
      "fae", "elven", "magical kingdom", "fantasy", "sorcerer",
      "enchant", "spell", "magical", "magic"]),
]

# ── Keywords that signal ANY romantasy (for Yes/No gate) ─────────────
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

def classify(synopsis: str, existing_subgenre: str = "") -> tuple[str, str]:
    """
    Returns (romantasy_yes_no, subgenre).
    Uses existing_subgenre first (already filled from GoodReads genre),
    then falls back to synopsis keyword scan.
    """
    combined = (str(existing_subgenre) + " " + str(synopsis)).lower()

    if not is_romantasy(combined):
        return "No", ""

    # Scan keyword map in priority order
    for subgenre, keywords in KEYWORD_MAP:
        if any(k in combined for k in keywords):
            return "Yes", subgenre

    # Romantasy signals hit but no sub-genre matched
    return "Yes", "High Fantasy Court Adventure"


def classify_root_literary(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"Loading: {file_path}")
    df = pd.read_excel(file_path)

    romantasy_col = "Romantasy = Yes or No?"
    subgenre_col  = "Romantasy Sub-Genre of series"
    synopsis_col  = "Synopsis (if available)"

    for col in [romantasy_col, subgenre_col]:
        if col not in df.columns:
            print(f"ERROR: column '{col}' not found. Columns: {df.columns.tolist()}")
            return

    yes_count = 0
    for idx, row in df.iterrows():
        synopsis  = str(row.get(synopsis_col,  ""))
        existing  = str(row.get(subgenre_col,  ""))

        romantasy, subgenre = classify(synopsis, existing)

        df.at[idx, romantasy_col] = romantasy
        df.at[idx, subgenre_col]  = subgenre

        if romantasy == "Yes":
            yes_count += 1
            print(f"  [Yes] {str(row.get('Name of Series',''))[:45]:45s} -> {subgenre}")
        else:
            print(f"  [No ] {str(row.get('Name of Series',''))[:45]:45s}")

    df.to_excel(file_path, index=False)
    print(f"\nDone! {yes_count}/{len(df)} books classified as Romantasy.")

    from apply_jra_style import apply_styling
    apply_styling(file_path)
    print("Styling reapplied.")

    import subprocess
    subprocess.Popen(["start", file_path], shell=True)


if __name__ == "__main__":
    base      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base, "Root_Literary_Formatted.xlsx")
    classify_root_literary(file_path)
