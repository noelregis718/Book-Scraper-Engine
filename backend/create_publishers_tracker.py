import pandas as pd
import os
import sys

# Append backend directory to use existing styling module
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))
from apply_jra_style import apply_styling

def create_publishers_sheet():
    columns = [
        "Publisher Name",
        "Category",
        "Number of authors in that publishing house",
        "Number of titles published per year",
        "Revenue of these publishing houses",
        "Year of establishment of these",
        "Genres they specialise in"
    ]
    
    # Create an empty DataFrame with these columns
    df = pd.DataFrame(columns=columns)
    
    # Target path
    excel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Publishers_Tracker.xlsx")
    
    # Save to Excel
    df.to_excel(excel_path, index=False)
    print(f"Created empty sheet at: {excel_path}")
    
    # Apply standard styling
    try:
        apply_styling(excel_path)
        print("Applied standard styling.")
    except Exception as e:
        print(f"Could not apply styling: {e}")

if __name__ == "__main__":
    create_publishers_sheet()
