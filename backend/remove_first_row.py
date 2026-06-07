import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def remove_first_row():
    f = r'E:\Internship\PocketFM\deborah_harris_merged.xlsx'
    
    if not os.path.exists(f):
        print(f"File not found: {f}")
        return
        
    print("Loading excel file...")
    df = pd.read_excel(f)
    
    if len(df) == 0:
        print("File is already empty.")
        return
        
    book_title = df.iloc[0]['Name of Series']
    
    # Drop the first row
    df = df.iloc[1:]
    
    df.to_excel(f, index=False)
    print(f"Successfully removed '{book_title}' (row 0).")
    
    try:
        from style_books_authors import apply_styling
        apply_styling(f)
    except Exception as e:
        print(f"Failed to style: {e}")

if __name__ == "__main__":
    remove_first_row()
