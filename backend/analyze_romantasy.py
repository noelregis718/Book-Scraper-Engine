import pandas as pd

try:
    df = pd.read_excel('Next_Agency.xlsx')
    
    subgenre_col = 'Romantasy Sub-Genre of series'
    
    print(f"Non-null subgenres:")
    print(df[subgenre_col].value_counts(dropna=False))
    
    # Let's also look for common romantasy keywords more broadly
    # Print a few synopses that have "magic" but not "romance"
    mask = df['Synopsis (if available)'].fillna('').str.contains('magic', case=False)
    mask2 = df['Romantasy = Yes or No?'] == 'No'
    
    print("\nSample of 'No' books with 'magic':")
    for idx, row in df[mask & mask2].head(5).iterrows():
        print(f"- {row['Name of Series']}: {row['Synopsis (if available)'][:150]}...")
        
except Exception as e:
    print(e)
