import pandas as pd
import re

file_path = 'Next_Agency.xlsx'

# Significantly broadened keywords
fantasy_keywords = [
    r'\bmagic', r'\bfae\b', r'\belf\b', r'\belves\b', r'\bwitch', r'\bwizard', 
    r'\bsupernatural\b', r'\bdragon', r'\brealm', r'\bfantasy', r'\bcurse', 
    r'\bmyth', r'\bvampire', r'\bwerewolf', r'\bshifter', r'\bdemon', r'\bangel',
    r'\bkingdom', r'\bcourt\b', r'\bthrone', r'\bcrown', r'\bspell', r'\benchant',
    r'\bmonster', r'\bparanormal', r'\bprophecy', r'\bgods\b', r'\bgoddess'
]

romance_keywords = [
    r'\bromanc', r'\blove\b', r'\blovers\b', r'\bsoulmate', r'\bheart', 
    r'\bswoon', r'\bkiss', r'\bmate\b', r'\bmarriage', r'\bdesire', 
    r'\bpassion', r'\bspicy', r'\benemies to lovers', r'\bfake dating',
    r'\bseduct', r'\bflirt', r'\bbride\b', r'\bhusband', r'\bwife',
    r'\bbetrothal', r'\barranged marriage', r'\bfated', r'\btriangle', 
    r'\bhandsome', r'\bbeautiful', r'\byearning'
]

# Explicit romantasy/subgenre indicators
exact_match = [
    r'\bromantasy\b', r'fantasy romance', r'romantic fantasy', r'paranormal romance',
    r'fated mate', r'spice'
]

re_fantasy = re.compile('|'.join(fantasy_keywords), re.IGNORECASE)
re_romance = re.compile('|'.join(romance_keywords), re.IGNORECASE)
re_exact = re.compile('|'.join(exact_match), re.IGNORECASE)

def is_romantasy_broad(text):
    if pd.isna(text) or not isinstance(text, str):
        return 'No'
    
    if re_exact.search(text):
        return 'Yes'
        
    if re_fantasy.search(text) and re_romance.search(text):
        return 'Yes'
        
    return 'No'

try:
    df = pd.read_excel(file_path)
    title_col = df.columns[0]
    synopsis_col = 'Synopsis (if available)'
    
    text_data = df[title_col].fillna('') + ' ' + df[synopsis_col].fillna('')
    
    df['Romantasy = Yes or No?'] = text_data.apply(is_romantasy_broad)
    
    counts = df['Romantasy = Yes or No?'].value_counts()
    print("New Classification Results:")
    print(counts)
    
    df.to_excel(file_path, index=False)
    print("Updated the Excel file with the broader classification.")

except Exception as e:
    print(e)
