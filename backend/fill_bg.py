import pandas as pd
import sys
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)

from agent_intelligent_classifier import classify_publisher
from backend.apply_jra_style import apply_styling

def get_genre(name):
    n = str(name).lower()
    if 'romance' in n or 'love' in n:
        return 'Romance'
    elif 'fantasy' in n:
        return 'Fantasy'
    return 'Exclusion List / General'

def run():
    p = os.path.join(base_dir, 'Publishers_Tracker_updated.xlsx')
    print("Loading Excel...")
    df = pd.read_excel(p)
    
    mask = df.index >= 2845
    print(f"Updating B and G columns for {mask.sum()} rows...")
    
    df.loc[mask, 'Category'] = df.loc[mask, 'Publisher Name'].apply(classify_publisher)
    df.loc[mask, 'Genres they specialise in'] = df.loc[mask, 'Publisher Name'].apply(get_genre)
    
    print("Saving...")
    df.to_excel(p, index=False)
    
    try:
        apply_styling(p)
        print("Styling applied.")
    except Exception as e:
        print("Style error:", e)
        
    print("Done!")

if __name__ == '__main__':
    run()
