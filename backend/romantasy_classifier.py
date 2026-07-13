import pandas as pd
import re

file_path = 'Next_Agency.xlsx'

# Keywords for classification
fantasy_keywords = [
    r'\bmagic\b', r'\bfae\b', r'\belf\b', r'\belves\b', r'\bwitch', r'\bwizard', 
    r'\bsupernatural\b', r'\bdragon', r'\brealm', r'\bfantasy\b', r'\bcurse', 
    r'\bmyth', r'\bvampire', r'\bwerewolf', r'\bshifter', r'\bdemon', r'\bangel'
]

romance_keywords = [
    r'\bromance\b', r'\bromantic\b', r'\blove\b', r'\blovers\b', r'\bsoulmate', 
    r'\bswoon', r'\bkiss', r'\bmate\b', r'\bmarriage\b', r'\bdesire\b', 
    r'\bpassion', r'\bspicy\b', r'\benemies to lovers\b', r'\bfake dating\b'
]

exact_match = [r'\bromantasy\b']

# Compile regex for speed (case insensitive)
re_fantasy = re.compile('|'.join(fantasy_keywords), re.IGNORECASE)
re_romance = re.compile('|'.join(romance_keywords), re.IGNORECASE)
re_exact = re.compile('|'.join(exact_match), re.IGNORECASE)

def is_romantasy(text):
    if pd.isna(text) or not isinstance(text, str):
        return 'No'
    
    # Direct mention of Romantasy
    if re_exact.search(text):
        return 'Yes'
        
    # Check for both Fantasy AND Romance elements
    if re_fantasy.search(text) and re_romance.search(text):
        return 'Yes'
        
    return 'No'

try:
    df = pd.read_excel(file_path)
    
    # Apply classifier to Synopsis and Title
    # We combine 'Name of Series' (Title) and 'Synopsis (if available)' for context
    # Fill NA with empty string for combination
    title_col = df.columns[0] # Usually 'Name of Series'
    synopsis_col = 'Synopsis (if available)'
    
    text_data = df[title_col].fillna('') + ' ' + df[synopsis_col].fillna('')
    
    # Apply logic
    df['Romantasy = Yes or No?'] = text_data.apply(is_romantasy)
    
    # Count results
    counts = df['Romantasy = Yes or No?'].value_counts()
    
    print("Classification Results:")
    print(counts)
    
    # Save back
    df.to_excel(file_path, index=False)
    print("\nSuccessfully updated the 'Romantasy = Yes or No?' column.")

except Exception as e:
    print("Error:", e)
