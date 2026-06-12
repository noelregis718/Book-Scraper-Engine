import pandas as pd
import re

df = pd.read_excel('romantasy_authors.xlsx')

subgenres = {
    'High Fantasy Court Adventure': ['court', 'kingdom', 'throne', 'prince', 'princess', 'king', 'queen', 'crown', 'empire', 'royal', 'palace'],
    'Gothic Dark Romantasy': ['gothic', 'dark', 'shadow', 'curse', 'blood', 'demon', 'death', 'macabre', 'haunted', 'sinister'],
    'Dark Academia Romantasy': ['academy', 'university', 'college', 'professor', 'student', 'school', 'scholars'],
    'Monster Romance (Non-Shifter)': ['monster', 'creature', 'orc', 'goblin', 'alien', 'tentacle', 'demon', 'gargoyle'],
    'Werewolf / Shifter Romance': ['shifter', 'wolf', 'werewolf', 'pack', 'alpha', 'mate', 'omega', 'bear', 'lion'],
    'High-Stakes Games & Deadly Trials': ['trial', 'game', 'tournament', 'survive', 'deadly', 'competition', 'arena'],
    'Mythology, Legend & Fairy Tale Retelling': ['myth', 'legend', 'retelling', 'fairy tale', 'god', 'goddess', 'hades', 'persephone', 'olympus', 'greek'],
    'War College / Military Academy': ['military', 'cadet', 'rider', 'conscription', 'squadron', 'rebellion', 'war'],
    'Korean Romance Fantasy / Isekai': ['isekai', 'reincarnated', 'villainess', 'manhwa', 'korean', 'duke', 'emperor', 'transmigrated'],
    'Paranormal Romance': ['vampire', 'ghost', 'paranormal', 'angel', 'witch', 'supernatural', 'immortal'],
    'Cozy / Cottagecore': ['cozy', 'cottage', 'tea', 'bakery', 'cafe', 'inn', 'tavern', 'low stakes', 'heartwarming', 'small town'],
    'Urban / Contemporary Fantasy Romance': ['urban', 'city', 'modern', 'detective', 'agency', 'contemporary']
}

def classify(synopsis, title):
    text = f"{str(synopsis)} {str(title)}".lower()
    
    best_genre = 'Paranormal Romance'
    max_matches = 0
    
    for genre, kw_list in subgenres.items():
        matches = sum(1 for k in kw_list if re.search(r'\b' + k + r'\b', text))
        if matches > max_matches:
            max_matches = matches
            best_genre = genre
            
    return 'Yes', best_genre

for idx in df.index:
    if pd.notna(df.loc[idx, 'Synopsis (if available)']):
        y_n, genre = classify(df.loc[idx, 'Synopsis (if available)'], df.loc[idx, 'Name of Series'])
        df.loc[idx, 'Romantasy = Yes or No?'] = y_n
        df.loc[idx, 'Romantasy Sub-Genre of series'] = genre

df.to_excel('romantasy_authors.xlsx', index=False)
print("Classification complete. Marked as 'Yes' and assigned sub-genres.")
