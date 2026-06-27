import pandas as pd
import os
import sys

# Append backend directory to use existing styling module
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))
from apply_jra_style import apply_styling

def run():
    source_excel = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Romantasy Combined_Amazon Keyword searches_Claude Mapping.xlsx')
    target_excel = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Publishers_Tracker.xlsx')
    
    print("Loading source Excel file...")
    xl = pd.ExcelFile(source_excel)
    
    all_publishers = set()
    
    # Iterate through all sheets that might contain the book data
    for sheet_name in xl.sheet_names:
        df_sheet = xl.parse(sheet_name)
        if 'Publisher' in df_sheet.columns:
            # Extract unique publishers
            publishers = df_sheet['Publisher'].dropna().unique()
            for pub in publishers:
                pub_str = str(pub).strip()
                if pub_str and pub_str.lower() not in ['nan', 'none']:
                    all_publishers.add(pub_str)
                    
    # Sort alphabetically
    unique_publishers = sorted(list(all_publishers))
    
    print(f"Found {len(unique_publishers)} unique publishers.")
    
    # Load the target tracker
    print("Loading target tracker sheet...")
    df_target = pd.read_excel(target_excel)
    
    # Assign the unique publishers to the 'Publisher Name' column
    # Ensure DataFrame is large enough
    if len(df_target) < len(unique_publishers):
        # Extend dataframe
        df_target = df_target.reindex(range(len(unique_publishers)))
        
    df_target['Publisher Name'] = pd.Series(unique_publishers)
    
    # Fill NaN with empty string for other columns
    df_target.fillna("", inplace=True)
    
    # Save the updated target Excel file
    print("Saving updated tracker...")
    df_target.to_excel(target_excel, index=False)
    
    # Re-apply styling
    try:
        apply_styling(target_excel)
        print("Styling applied.")
    except Exception as e:
        print(f"Error applying styling: {e}")

if __name__ == '__main__':
    run()
