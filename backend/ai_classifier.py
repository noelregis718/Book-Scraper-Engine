import re

# --- ROMANTASY TAXONOMY (AI-Enhanced for Classification) ---
TAXONOMY = {
    "High Fantasy Court Adventure": ["fae", "elven", "magical kingdom", "royal court", "fantasy empire", "epic quest", "magic world", "crown prince", "queen of", "king of", "throne of", "heir to the", "castle of", "dragon", "knight", "sword", "crown", "realm"],
    "Gothic Dark Romantasy": ["gothic romance", "dark magic", "haunted castle", "vampiric", "macabre", "blood magic", "deathly curse", "gothic mystery", "vampire", "blood", "dracula", "bite", "nightmare", "shadow"],
    "Dark Academia Romantasy": ["magical academy", "secret society", "magic school", "university of magic", "scholar of the", "campus of magic", "academy"],
    "Monster Romance (Non-Shifter)": ["monster romance", "tentacle", "orc", "kraken", "minotaur", "beastman", "non-human lover", "beast", "alien", "demon", "gargoyle"],
    "Werewolf / Shifter Romance": ["shapeshifter", "wolf shifter", "bear shifter", "dragon shifter", "pack alpha", "omegaverse", "true mate", "shifter romance", "omega", "alpha", "beta", "knot", "mate", "wolf", "bear", "tiger", "fury", "pack", "fur"],
    "High-Stakes Games & Deadly Trials": ["deadly trials", "magical tournament", "deadly games", "magical contest", "trial of the", "games", "tournament"],
    "Mythology, Legend & Fairy Tale Retelling": ["greek myth", "norse myth", "retelling", "fairy tale retelling", "gods and monsters", "mortal and god", "hades", "persephone", "cinderella", "beauty and the beast"],
    "War College / Military Academy": ["war college", "military academy", "dragon rider", "beast bond", "combat training", "lethal training", "cadet"],
    "Korean Romance Fantasy / Isekai": ["isekai", "reincarnation", "villainess", "empress", "saintess", "transmigration", "isekai romance"],
    "Paranormal Romance": ["vampire romance", "demon lover", "succubus", "paranormal mystery", "coven of witches", "warlock", "ghost", "spirit", "haunting", "witch", "spell", "magic", "paranormal", "supernatural", "afterlife"],
    "Cozy / Cottagecore": ["cozy fantasy", "cottagecore", "magical bakery", "small town magic", "low-stakes fantasy", "bakery", "cafe", "tea", "cozy"],
    "Urban / Contemporary Fantasy Romance": ["urban fantasy", "hidden magic", "magic in the city", "secret supernatural", "hidden world", "city", "detective", "modern magic"]
}

def identify_subgenre(synopsis, tags):
    """Matches synopsis and tags against the taxonomy using word boundaries.
    Guarantees a sub-genre from the list (random distribution if no match is found)."""
    import random
    
    if not synopsis and not tags:
        return random.choice(list(TAXONOMY.keys()))
        
    text = f"{synopsis} {' '.join(tags)}".lower()
    
    for genre, keywords in TAXONOMY.items():
        for kw in keywords:
            # Use regex to find whole word matches
            pattern = rf"\b{re.escape(kw.lower())}\b"
            if re.search(pattern, text):
                return genre
            
    # If no match found, distribute across the taxonomy evenly rather than defaulting to one value
    return random.choice(list(TAXONOMY.keys()))
