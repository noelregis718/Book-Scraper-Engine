import os
import sys

from romantasy_analyzer import analyze_catalog
from apply_jra_style import apply_styling

def process_jra_romantasy():
    excel_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'JRA_Bestsellers_Complete.xlsx')
    
    if not os.path.exists(excel_path):
        print(f"Error: {excel_path} not found.")
        return
        
    print(f"Applying Romantasy categorization to {excel_path}...")
    analyze_catalog(excel_path)
    
    print("Reapplying professional styling...")
    apply_styling(excel_path)
    print("All done!")

if __name__ == "__main__":
    process_jra_romantasy()
