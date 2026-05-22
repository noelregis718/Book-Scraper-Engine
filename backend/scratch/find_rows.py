import pandas as pd
import os

file_path = r"E:\Internship\PocketFM\Master_Author_Enrichment.xlsx"
if os.path.exists(file_path):
    df = pd.read_excel(file_path)
    print(f"Total rows in enrichment sheet: {len(df)}")
    
    # Find Jacob Peppers
    jacob = df[df['Author Name'].str.contains('Jacob Peppers', case=False, na=False)]
    if not jacob.empty:
        # Pandas index + 2 (1 for header, 1 for 1-indexing)
        print(f"Jacob Peppers is at index(es): {jacob.index.tolist()}")
        for idx in jacob.index:
            print(f"Jacob Peppers: Row {idx + 2}")
    else:
        print("Jacob Peppers not found.")
        
    # Find last row
    print(f"Last row in sheet: {len(df) + 1}")
    print(f"Last author: {df.iloc[-1]['Author Name']}")
    
    # Look for "Kelly" near the end
    kelly = df[df['Author Name'].str.contains('Kelly', case=False, na=False)]
    if not kelly.empty:
        last_kelly = kelly.tail(1)
        print(f"Last Kelly found at Row {last_kelly.index[0] + 2}: {last_kelly.iloc[0]['Author Name']}")
else:
    print("File not found.")
