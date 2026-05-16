import re

# --- ROMANTASY TAXONOMY (AI-Enhanced for Classification) ---
TAXONOMY = {
    "High Fantasy Court Adventure": ["fae", "elven", "magical kingdom", "royal court", "fantasy empire", "epic quest", "magic world", "crown prince", "queen of", "king of", "throne of", "heir to the", "castle of"],
    "Gothic Dark Romantasy": ["gothic romance", "dark magic", "haunted castle", "vampiric", "macabre", "blood magic", "deathly curse", "gothic mystery"],
    "Dark Academia Romantasy": ["magical academy", "secret society", "magic school", "university of magic", "scholar of the", "campus of magic"],
    "Monster Romance (Non-Shifter)": ["monster romance", "tentacle", "orc", "kraken", "minotaur", "beastman", "non-human lover"],
    "Werewolf / Shifter Romance": ["shapeshifter", "wolf shifter", "bear shifter", "dragon shifter", "pack alpha", "omegaverse", "true mate", "shifter romance"],
    "High-Stakes Games & Deadly Trials": ["deadly trials", "magical tournament", "deadly games", "magical contest", "trial of the"],
    "Mythology, Legend & Fairy Tale Retelling": ["greek myth", "norse myth", "retelling", "fairy tale retelling", "gods and monsters", "mortal and god"],
    "War College / Military Academy": ["war college", "military academy", "dragon rider", "beast bond", "combat training", "lethal training"],
    "Korean Romance Fantasy / Isekai": ["isekai", "reincarnation", "villainess", "empress", "saintess", "transmigration", "isekai romance"],
    "Paranormal Romance": ["vampire romance", "demon lover", "succubus", "paranormal mystery", "coven of witches", "warlock"],
    "Cozy / Cottagecore": ["cozy fantasy", "cottagecore", "magical bakery", "small town magic", "low-stakes fantasy"],
    "Urban / Contemporary Fantasy Romance": ["urban fantasy", "hidden magic", "magic in the city", "secret supernatural", "hidden world"]
}

def identify_subgenre(synopsis, tags):
    """Matches synopsis and tags against the taxonomy using word boundaries."""
    if not synopsis and not tags:
        return "N/A"
        
    text = f"{synopsis} {' '.join(tags)}".lower()
    
    for genre, keywords in TAXONOMY.items():
        for kw in keywords:
            # Use regex to find whole word matches
            pattern = rf"\b{re.escape(kw.lower())}\b"
            if re.search(pattern, text):
                return genre
            
    return "N/A"
