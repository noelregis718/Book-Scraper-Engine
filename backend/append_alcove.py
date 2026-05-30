import pandas as pd
import os
import sys

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
formatted_file = os.path.join(base_path, "Alcove_Press_Formatted.xlsx")
new_list_file = os.path.join(base_path, "alcove_press_fantasy_historical_bookclub_books.xlsx")

def append_alcove():
    if not os.path.exists(formatted_file):
        print(f"File not found: {formatted_file}")
        return
        
    if not os.path.exists(new_list_file):
        print(f"File not found: {new_list_file}")
        return
        
    print(f"Loading {formatted_file}...")
    df_existing = pd.read_excel(formatted_file)
    print(f"Existing rows: {len(df_existing)}")
    
    print(f"Loading {new_list_file}...")
    df_new = pd.read_excel(new_list_file)
    
    new_rows = []
    for _, row in df_new.iterrows():
        title = row.get('Book Name', '')
        author = row.get('Author Name', '')
        
        if pd.isna(title) and pd.isna(author):
            continue
            
        new_rows.append({
            "Name of Series": title,
            "Author Name": author,
            "Publisher": "Alcove Press",
            "GoodReads series link": "N/A",
            "Number of PRIMARY books in the series": "N/A",
            "Rating (out of 5) of Primary Book 1": "N/A",
            "Ratings (#) of Primary Book 1": "N/A",
            "Synopsis (if available)": "N/A",
            "Romantasy = Yes or No?": "No",
            "Romantasy Sub-Genre of series": "",
            "Name of agent": "N/A"
        })
        
    if new_rows:
        df_to_append = pd.DataFrame(new_rows)
        
        # Merge them
        merged_df = pd.concat([df_existing, df_to_append], ignore_index=True)
        
        # Drop duplicates by Name of Series and Author Name
        merged_df = merged_df.drop_duplicates(subset=['Name of Series', 'Author Name'], keep='first')
        
        print(f"Saving {len(merged_df)} total rows to {formatted_file}...")
        merged_df.to_excel(formatted_file, index=False)
        
        try:
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from apply_jra_style import apply_styling
            apply_styling(formatted_file)
            print("Styling applied.")
        except Exception as e:
            print(f"Styling error: {e}")
    else:
        print("No valid rows found in the new list.")

if __name__ == '__main__':
    append_alcove()
