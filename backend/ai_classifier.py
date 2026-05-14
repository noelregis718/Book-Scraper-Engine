import re

# --- ROMANTASY TAXONOMY (AI-Enhanced for Classification) ---
TAXONOMY = {
    "High Fantasy Court Adventure": ["royal", "court", "fae", "kingdom", "throne", "prince", "princess", "queen", "king", "empire", "epic", "quest", "heir", "magic world", "castle"],
    "Gothic Dark Romantasy": ["horror", "curse", "dark magic", "atmospheric", "gothic", "haunting", "shadow", "macabre", "creepy", "blood", "morbid", "vampiric", "deathly", "ripper"],
    "Dark Academia Romantasy": ["school", "university", "academy", "secret society", "rival", "library", "scholar", "student", "professor", "campus", "scholastic", "boarding school", "heritage", "inheritance"],
    "Monster Romance (Non-Shifter)": ["monster", "alien", "inhuman", "non-human", "beast", "creature", "tentacle", "abominable", "kraken", "orc", "beastman", "non-shifter"],
    "Werewolf / Shifter Romance": ["shapeshifter", "wolf", "bear", "dragon", "leopard", "tiger", "pack", "alpha", "mate", "shifter", "werewolf", "lycan", "luna", "omega", "knot"],
    "High-Stakes Games & Deadly Trials": ["competition", "game", "tournament", "bargain", "deal", "trial", "forced proximity", "prize", "contest", "deadly game", "deadly trials", "final trial"],
    "Mythology, Legend & Fairy Tale Retelling": ["mortal", "god", "goddess", "divine", "prophecy", "pantheon", "myth", "mythology", "olympus", "deity", "retelling", "fairy tale", "fable", "legend"],
    "War College / Military Academy": ["lethal training", "dragon bond", "beast bond", "rider", "training", "war", "soldier", "mercenary", "combat", "war college", "military academy", "wing", "quadrant"],
    "Korean Romance Fantasy / Isekai": ["reincarnation", "transmigration", "regression", "past life", "second chance", "isekai", "rebirth", "reborn", "villainess", "empress", "saintess", "system", "incarnation"],
    "Paranormal Romance": ["vampire", "demon", "angel", "reaper", "ghost", "spirit", "undead", "succubus", "incubus", "paranormal", "witch", "warlock", "coven"],
    "Cozy / Cottagecore": ["cozy", "low-stakes", "found family", "slow-burn", "magical bakery", "tea", "comfort", "wholesome", "cottagecore", "small town magic", "whimsical"],
    "Urban / Contemporary Fantasy Romance": ["modern world", "contemporary", "magic layered", "city", "hidden world", "masquerade", "urban", "street magic", "ley-line", "modern day"]
}

def identify_subgenre(synopsis, tags):
    """Matches synopsis and tags against the taxonomy to classify sub-genre."""
    if not synopsis and not tags:
        return "N/A"
        
    text = f"{synopsis} {' '.join(tags)}".lower()
    
    # Priority matching for specific high-fidelity keywords
    for genre, keywords in TAXONOMY.items():
        if any(kw.lower() in text for kw in keywords):
            return genre
            
    return "N/A"
