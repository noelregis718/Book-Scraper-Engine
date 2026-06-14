import pandas as pd
import re

EXCEL_FILE = "e:/Internship/PocketFM/books_from_images.xlsx"

SUBGENRES = {
    "High Fantasy Court Adventure": [r"\bcourt\b", r"\bking\b", r"\bqueen\b", r"\bkingdom\b", r"\bthrone\b", r"\bcrown\b", r"\bprince\b", r"\bprincess\b", r"\brealm\b", r"\bfae\b", r"\belf\b", r"\bempire\b", r"\broyal\b"],
    "Gothic Dark Romantasy": [r"\bgothic\b", r"\bdark\b", r"\bshadow\b", r"\bhaunt\b", r"\bcurse\b", r"\bmacabre\b", r"\bcastle\b", r"\bmanor\b", r"\bdecay\b"],
    "Dark Academia Romantasy": [r"\bacademy\b", r"\buniversity\b", r"\bschool\b", r"\blibrary\b", r"\bscholar\b", r"\bstudent\b", r"\bprofessor\b", r"\bsecret society\b"],
    "Monster Romance (Non-Shifter)": [r"\bmonster\b", r"\bcreature\b", r"\borc\b", r"\balien\b", r"\bbeast\b", r"\bgargoyle\b"],
    "Werewolf / Shifter Romance": [r"\bwerewolf\b", r"\bshifter\b", r"\bpack\b", r"\balpha\b", r"\bwolf\b", r"\bmate\b", r"\bluna\b", r"\bomega\b"],
    "High-Stakes Games & Deadly Trials": [r"\bgame\b", r"\btrial\b", r"\btournament\b", r"\bsurvive\b", r"\barena\b", r"\bcompetition\b", r"\bdeadly\b", r"\bhunger games\b"],
    "Mythology, Legend & Fairy Tale Retelling": [r"\bmyth\b", r"\bgod\b", r"\bgoddess\b", r"\bretelling\b", r"\blegend\b", r"\bhades\b", r"\bpersephone\b", r"\bfairy tale\b", r"\bolympus\b"],
    "War College / Military Academy": [r"\bwar college\b", r"\bmilitary academy\b", r"\bsoldier\b", r"\bcadet\b", r"\brider\b", r"\bdragon rider\b", r"\brebellion\b", r"\barmy\b", r"\bwarrior\b"],
    "Korean Romance Fantasy / Isekai": [r"\bisekai\b", r"\breincarnat", r"\bvillainess\b", r"\bkorean\b", r"\bmanhwa\b", r"\bduke\b", r"\btransmigrat"],
    "Paranormal Romance": [r"\bvampire\b", r"\bwitch", r"\bghost\b", r"\bdemon\b", r"\bangel\b", r"\bparanormal\b", r"\bsupernatural\b", r"\bcoven\b"],
    "Cozy / Cottagecore": [r"\bcozy\b", r"\bcottage", r"\btea\b", r"\bbakery\b", r"\bsmall town\b", r"\bhealing\b", r"\bpotion\b"],
    "Urban / Contemporary Fantasy Romance": [r"\burban\b", r"\bmoder\b", r"\bcity\b", r"\bdetective\b", r"\bagency\b", r"\bcontemporary\b", r"\bnew york\b", r"\blondon\b"]
}

def classify(text):
    text = str(text).lower()
    
    # Check for direct matches
    scores = {genre: 0 for genre in SUBGENRES}
    
    for genre, patterns in SUBGENRES.items():
        for pattern in patterns:
            if re.search(pattern, text):
                scores[genre] += 1
                
    # Find the genre with the max score
    best_genre = max(scores, key=scores.get)
    if scores[best_genre] > 0:
        return best_genre
    else:
        # Default
        return "High Fantasy Court Adventure"

def is_romantasy(text):
    text = str(text).lower()
    non_fiction_clues = ["biography", "memoir", "history of", "guide to", "non-fiction", "nonfiction", "essay"]
    for clue in non_fiction_clues:
        if clue in text:
            return "No"
    return "Yes"

def main():
    print("Loading excel file...")
    df = pd.read_excel(EXCEL_FILE)
    
    # Cast to object to prevent TypeError
    df['Romantasy = Yes or No?'] = df['Romantasy = Yes or No?'].astype('object')
    df['Romantasy Sub-Genre of series'] = df['Romantasy Sub-Genre of series'].astype('object')
    
    for index, row in df.iterrows():
        title = str(row.get('Name of Series', ''))
        synopsis = str(row.get('Synopsis (if available)', ''))
        combined_text = f"{title} {synopsis}"
        
        # Only classify if not already classified or if we want to overwrite
        df.at[index, 'Romantasy = Yes or No?'] = is_romantasy(combined_text)
        df.at[index, 'Romantasy Sub-Genre of series'] = classify(combined_text)
        
    df.to_excel(EXCEL_FILE, index=False)
    print("Classification complete and saved to Excel!")

if __name__ == "__main__":
    main()
