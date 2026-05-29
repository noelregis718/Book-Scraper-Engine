import pandas as pd
import os
import sys

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bradford_file = os.path.join(base_path, "Bradford_Literary_Formatted.xlsx")
solstice_file = os.path.join(base_path, "Solstice_Romance_Formatted.xlsx")
merged_file = os.path.join(base_path, "Bradford_Solstice_Merged_Formatted.xlsx")

def merge_sheets():
    print(f"Reading {bradford_file}...")
    if not os.path.exists(bradford_file):
        print(f"File not found: {bradford_file}")
        return
        
    df1 = pd.read_excel(bradford_file)
    print(f"Found {len(df1)} rows in Bradford sheet.")
    
    print(f"Reading {solstice_file}...")
    if not os.path.exists(solstice_file):
        print(f"File not found: {solstice_file}")
        return
        
    df2 = pd.read_excel(solstice_file)
    print(f"Found {len(df2)} rows in Solstice sheet.")
    
    # Merge
    merged_df = pd.concat([df1, df2], ignore_index=True)
    
    # Remove any potential empty rows or duplicates based on Title and Author
    merged_df = merged_df.dropna(subset=['Author Name'], how='all')
    merged_df = merged_df.drop_duplicates(subset=['Name of Series', 'Author Name'], keep='first')
    
    # Fill NAs to keep it clean
    merged_df = merged_df.fillna('')
    
    # Save to new Excel
    print(f"Saving {len(merged_df)} total rows to {merged_file}...")
    merged_df.to_excel(merged_file, index=False)
    
    # Apply styling
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from apply_jra_style import apply_styling
        apply_styling(merged_file)
        print("Styling applied successfully.")
    except Exception as e:
        print(f"Styling error: {e}")

if __name__ == '__main__':
    merge_sheets()
