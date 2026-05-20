import os
import sys
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from apply_jra_style import apply_styling

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
    "Urban / Contemporary Fantasy Romance",
]

# Order matters: more-specific buckets are checked before broader ones.
KEYWORD_MAP = [
    ("Werewolf / Shifter Romance",
     ["werewolf", "shifter", "alpha", "pack of wolves", "omegaverse", "luna",
      "wolf pack", "lycan", "shape-shifter", "shape shifter"]),

    ("Monster Romance (Non-Shifter)",
     ["monster romance", "orc", "kraken", "alien romance", "beast lover",
      "demon lover", "tentacle", "minotaur", "centaur", "naga"]),

    ("Mythology, Legend & Fairy Tale Retelling",
     ["retelling", "mythology", "greek god", "hades", "persephone", "fairy tale",
      "fairytale", "legend", "arthurian", "norse", "anansi", "medusa", "circe",
      "orpheus", "cinderella", "beauty and the beast", "snow white", "rumpelstiltskin"]),

    ("War College / Military Academy",
     ["war college", "military academy", "dragon rider", "fourth wing", "basgiath",
      "aerial squad", "flight school", "training camp", "bonded dragon",
      "cadet", "war school"]),

    ("High-Stakes Games & Deadly Trials",
     ["trial of", "deadly game", "tournament", "competition to the death",
      "survival game", "arena", "hunger games", "death match", "blood game",
      "lethal trial", "gauntlet"]),

    ("Dark Academia Romantasy",
     ["dark academia", "secret society", "forbidden library", "ancient university",
      "cursed school", "arcane academy", "magic school", "boarding school of magic",
      "magical college"]),

    ("Gothic Dark Romantasy",
     ["gothic", "haunted manor", "dark romance", "gloomy castle", "shadow court",
      "cursed castle", "decaying estate", "vampire lord", "immortal lord",
      "crumbling abbey", "moors"]),

    ("Korean Romance Fantasy / Isekai",
     ["isekai", "reincarnated", "villainess", "otome", "korean", "manhwa",
      "transmigrated", "possessed the body", "regression", "webnovel"]),

    ("Cozy / Cottagecore",
     ["cozy fantasy", "cottagecore", "small town magic", "bakery", "low stakes",
      "wholesome", "botanical", "village witch", "flower shop", "magical inn",
      "tea shop"]),

    ("Paranormal Romance",
     ["vampire", "ghost", "witch", "paranormal", "psychic", "medium",
      "warlock", "necromancer", "haunting", "supernatural romance",
      "fae romance", "fairy", "fae prince", "fae court"]),

    ("High Fantasy Court Adventure",
     ["court intrigue", "throne", "kingdom", "royalty", "fae court", "high fantasy",
      "crown prince", "empire", "queen", "king", "prince", "realm", "dragon",
      "epic fantasy", "political intrigue", "magic system", "sorceress", "mage"]),

    ("Urban / Contemporary Fantasy Romance",
     ["urban fantasy", "modern day magic", "contemporary fantasy", "hidden world",
      "secret magic", "city of magic", "supernatural city"]),
]


def classify(title, synopsis):
    text = (str(title) + " " + str(synopsis)).lower()
    for subgenre, keywords in KEYWORD_MAP:
        if any(k in text for k in keywords):
            return subgenre
    return None


def run(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"Loading: {file_path}")
    df = pd.read_excel(file_path, keep_default_na=False)

    romantasy_col = "Romantasy = Yes or No?"
    subgenre_col = "Romantasy Sub-Genre of series"
    title_col = "Name of Series"
    synopsis_col = "Synopsis (if available)"

    for c in (romantasy_col, subgenre_col):
        if c not in df.columns:
            print(f"Missing column: {c}")
            return
        df[c] = df[c].astype(object)

    yes_count = 0
    by_subgenre = {}
    for idx, row in df.iterrows():
        title = row.get(title_col, "")
        synopsis = row.get(synopsis_col, "")

        # Skip rows with no usable text
        if not str(title).strip() and not str(synopsis).strip():
            df.at[idx, romantasy_col] = ""
            df.at[idx, subgenre_col] = ""
            continue

        result = classify(title, synopsis)
        if result:
            df.at[idx, romantasy_col] = "Yes"
            df.at[idx, subgenre_col] = result
            yes_count += 1
            by_subgenre[result] = by_subgenre.get(result, 0) + 1
        else:
            df.at[idx, romantasy_col] = "No"
            df.at[idx, subgenre_col] = ""

    df.to_excel(file_path, index=False)
    print(f"\nClassified {yes_count}/{len(df)} rows as Romantasy.")
    print("Breakdown:")
    for sub, n in sorted(by_subgenre.items(), key=lambda x: -x[1]):
        print(f"  {n:3}  {sub}")

    print("\nReapplying styling...")
    apply_styling(file_path)
    print("Done.")


if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    run(os.path.join(base, "New_Agency.xlsx"))
