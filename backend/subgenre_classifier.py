import pandas as pd

file_path = 'Next_Agency.xlsx'

def classify_subgenre(row, title_col, synopsis_col):
    # Only classify sub-genre if it is a Romantasy book
    if row['Romantasy = Yes or No?'] == 'No':
        return pd.NA
        
    text = str(row[title_col]).lower() + ' ' + str(row[synopsis_col]).lower()
    
    # Fae Fantasy
    if any(k in text for k in ['fae', 'fairy', 'faeries', 'unseelie', 'seelie', 'courts of']):
        return 'Fae Fantasy'
        
    # Paranormal / Urban Fantasy
    elif any(k in text for k in ['vampire', 'werewolf', 'shifter', 'paranormal', 'urban', 'modern', 'detective', 'agency']):
        return 'Paranormal / Urban Fantasy'
        
    # Mythological Fantasy
    elif any(k in text for k in ['myth', 'god ', 'gods', 'goddess', 'olympus', 'hades', 'persephone', 'deity']):
        return 'Mythological Fantasy'
        
    # Dark Fantasy
    elif any(k in text for k in ['demon', 'monster', 'dark', 'curse', 'assassin', 'underworld', 'deadly', 'blood']):
        return 'Dark Fantasy'
        
    # High / Epic Fantasy
    elif any(k in text for k in ['kingdom', 'throne', 'court', 'crown', 'empire', 'epic', 'dragon', 'realm', 'war', 'rebellion', 'magic', 'mage']):
        return 'High / Epic Fantasy'
        
    # Cozy Fantasy
    elif any(k in text for k in ['cozy', 'tea', 'bakery', 'shop', 'inn', 'tavern', 'lighthearted']):
        return 'Cozy Fantasy'
        
    # Default for Romantasy if no specific tropes are overwhelmingly present
    else:
        return 'General Romantasy'

try:
    df = pd.read_excel(file_path)
    title_col = df.columns[0]
    synopsis_col = 'Synopsis (if available)'
    
    # Apply sub-genre classification
    df['Romantasy Sub-Genre of series'] = df.apply(lambda row: classify_subgenre(row, title_col, synopsis_col), axis=1)
    
    # Print out value counts for the subgenres to see what we got
    counts = df['Romantasy Sub-Genre of series'].value_counts(dropna=False)
    print("Sub-Genre Classification Results:")
    print(counts)
    
    # Save back to Excel
    df.to_excel(file_path, index=False)
    print("\nSuccessfully updated the 'Romantasy Sub-Genre of series' column.")

except Exception as e:
    print("Error:", e)
