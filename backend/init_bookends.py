import pandas as pd
import os

SOURCE_FILE = "bookends_adult_children_merged.xlsx"
OUTPUT_FILE = "Bookends_Literary_Catalog_Final.xlsx"

def create_catalog():
    if not os.path.exists(SOURCE_FILE):
        print(f"Error: {SOURCE_FILE} not found!")
        return

    df_src = pd.read_excel(SOURCE_FILE)
    
    # Create the new DataFrame with the requested 11 columns
    df_final = pd.DataFrame()
    
    # 1. Name of Series (from Book Title)
    df_final['Name of Series'] = df_src['Book Title']
    
    # 2. Author Name (from Author)
    df_final['Author Name'] = df_src['Author']
    
    # 3. Publisher
    df_final['Publisher'] = "N/A"
    
    # 4. GoodReads series link
    df_final['GoodReads series link'] = "N/A"
    
    # 5. Number of PRIMARY books in the series
    df_final['Number of PRIMARY books in the series'] = "N/A"
    
    # 6. Rating (out of 5) of Primary Book 1
    df_final['Rating (out of 5) of Primary Book 1'] = "N/A"
    
    # 7. Ratings (#) of Primary Book 1
    df_final['Ratings (#) of Primary Book 1'] = "N/A"
    
    # 8. Synopsis (if available)
    df_final['Synopsis (if available)'] = "N/A"
    
    # 9. Romantasy = Yes or No?
    df_final['Romantasy = Yes or No?'] = "N/A"
    
    # 10. Romantasy Sub-Genre of series
    df_final['Romantasy Sub-Genre of series'] = "N/A"
    
    # 11. Name of agent
    df_final['Name of agent'] = "N/A"
    
    df_final.to_excel(OUTPUT_FILE, index=False)
    print(f"Successfully created {OUTPUT_FILE} with the specific 11-column schema.")

if __name__ == "__main__":
    create_catalog()
