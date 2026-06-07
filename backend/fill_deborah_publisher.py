import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def fill_publisher():
    f = r'E:\Internship\PocketFM\deborah_harris_merged.xlsx'
    
    if not os.path.exists(f):
        print(f"File not found: {f}")
        return
        
    print("Loading excel file...")
    df = pd.read_excel(f)
    
    df['Publisher'] = 'The Deborah Harris Agency'
    df['Name of agent'] = 'Deborah Harris'
    
    df.to_excel(f, index=False)
    print('Successfully updated Publisher and Agent!')
    
    try:
        from style_books_authors import apply_styling
        apply_styling(f)
    except Exception as e:
        print(f"Failed to style: {e}")

if __name__ == "__main__":
    fill_publisher()
