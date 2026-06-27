import pandas as pd
import re
import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))
from apply_jra_style import apply_styling

# AI Knowledge injected into sets for fast classification
LARGE_PUBLISHERS = [
    "penguin", "random house", "harpercollins", "simon & schuster", "hachette", "macmillan", 
    "bloomsbury", "amazon publishing", "tor ", "tor books", "orbit", "del rey", "mira", "berkley", 
    "avon", "bramble", "47north", "montlake", "brilliance", "st. martin", "grand central", 
    "knopf", "doubleday", "crown", "bantam", "delacorte", "harlequin", "harper", "william morrow", 
    "gallery books", "atria", "pocket books", "scolastic", "little, brown", "farrar, straus", 
    "gollancz", "hodder", "pan macmillan", "penguin audio", "macmillan audio", "hachette audio",
    "simon & schuster audio", "harperaudio", "harpercollins publishers"
]

MEDIUM_PUBLISHERS = [
    "sourcebooks", "bloom books", "kensington", "entangled", "red tower", "amara", "blackstone", 
    "podium", "tantor", "recorded books", "dreamscape", "shadow mountain", "waterhouse", 
    "bookouture", "lake union", "thomas nelson", "zondervan", "tyndale", "bethany house", 
    "revell", "baker publishing", "scholastic", "disney hyperion", "angry robot", "baen", 
    "daw books", "subterranean", "ps publishing", "tachyon", "gideon", "crooked lane", "severn house"
]

SELF_PUB_EXACT = [
    "independently published", "independent", "amazon digital services", "amazon digital services llc",
    "kdp", "createspace", "smashwords", "draft2digital", "ingramspark", "lulu", "blurb", "bookbaby",
    "authorhouse", "xlibris", "iuniverse", "outskirts press", "balboa press", "friesenpress"
]

SELF_PUB_KEYWORDS = [
    " llc", " ltd", " books inc", " publishing inc"
]

JUNK_KEYWORDS = [
    "narrator", "narrated by", "review", "excerpt", "translated by", "audible original", 
    "amazon original", "introduction by", "foreword by", "illustrated by"
]

def classify_publisher(name):
    if pd.isna(name) or str(name).strip() == "":
        return "Unknown"
        
    name_clean = str(name).strip().lower()
    
    # 1. Check Junk
    if name_clean.startswith("(") or name_clean.startswith(")"):
        return "Unknown (Junk)"
    for j in JUNK_KEYWORDS:
        if j in name_clean:
            return "Unknown (Junk)"
            
    # 2. Check Self-Published
    for sp in SELF_PUB_EXACT:
        if sp == name_clean or name_clean.startswith(sp + " -"):
            return "Self-Published"
    for sp_kw in SELF_PUB_KEYWORDS:
        if sp_kw in name_clean:
            return "Self-Published"
            
    # Check for Author LLC (2 or 3 words followed by LLC or Publishing)
    # This is a heuristic. If it ends in LLC, we already caught it above.
    
    # 3. Check Large
    for lg in LARGE_PUBLISHERS:
        # Regex word boundary to avoid partial matches
        pattern = rf"\b{re.escape(lg)}\b"
        if re.search(pattern, name_clean):
            return "Large"
            
    # 4. Check Medium
    for md in MEDIUM_PUBLISHERS:
        pattern = rf"\b{re.escape(md)}\b"
        if re.search(pattern, name_clean):
            return "Medium"
            
    # 5. Default to Small
    return "Small"

def run():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    tracker_path = os.path.join(base_dir, 'Publishers_Tracker_updated.xlsx')
    
    print("Loading Publishers_Tracker.xlsx...")
    df = pd.read_excel(tracker_path)
    
    print("Classifying publishers using AI intelligence...")
    categories = []
    
    for pub in df['Publisher Name']:
        cat = classify_publisher(pub)
        categories.append(cat)
        
    df['Category'] = categories
    
    print("Saving classified publishers...")
    df.to_excel(tracker_path, index=False)
    
    print("Reapplying styling...")
    try:
        apply_styling(tracker_path)
        print("Success! Classification complete.")
    except Exception as e:
        print(f"Error applying style: {e}")
        
if __name__ == '__main__':
    run()
