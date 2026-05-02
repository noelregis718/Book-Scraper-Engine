import pandas as pd
from excel_utility import save_to_excel
import os

def reformat():
    main_file = r'E:\Internship\PocketFM\Amazon Keyword - Romantasy.xlsx'
    
    if not os.path.exists(main_file):
        print(f"File not found: {main_file}")
        return

    print(f"Loading data from {main_file}...")
    df = pd.read_excel(main_file)
    
    # Convert dataframe to list of dicts for the utility function
    data = df.to_dict('records')
    
    print(f"Applying professional formatting to {len(data)} rows...")
    # This will rewrite the file using the formatting logic in excel_utility.py
    save_to_excel(data, main_file)
    print("Formatting complete.")

if __name__ == "__main__":
    reformat()
