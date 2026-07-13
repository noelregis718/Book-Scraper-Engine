import pandas as pd

try:
    df = pd.read_excel('Next_Agency.xlsx')
    
    # Check column 8 which is 'Romantasy = Yes or No?'
    rom_col = 'Romantasy = Yes or No?'
    
    print("Value counts in Romantasy column:")
    print(df[rom_col].value_counts(dropna=False))
    
    # Also check if there's any synopsis to use for classification
    synopsis_col = 'Synopsis (if available)'
    empty_synopsis = df[synopsis_col].isna().sum()
    print(f"Total rows: {len(df)}, Empty synopses: {empty_synopsis}")

except Exception as e:
    print(e)
