import pandas as pd
import os
import sys

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
input_file = os.path.join(base_path, "handspun_romance_books_from_instagram_update.xlsx")
output_file = os.path.join(base_path, "Handspun_Literary_Formatted.xlsx")

def format_handspun():
    if not os.path.exists(input_file):
        print(f"File not found: {input_file}")
        return
        
    print(f"Loading {input_file}...")
    df_in = pd.read_excel(input_file)
    
    new_rows = []
    for _, row in df_in.iterrows():
        title = row.get('Book Title', '')
        author = row.get('Author', '')
        
        # If book title is empty but we have an author, we might want to keep the row per user request "make sure you dont remove the book names or author names"
        if pd.isna(title) and pd.isna(author):
            continue
            
        new_rows.append({
            "Name of Series": title if not pd.isna(title) else "",
            "Author Name": author if not pd.isna(author) else "",
            "Publisher": "N/A",
            "GoodReads series link": "N/A",
            "Number of PRIMARY books in the series": "N/A",
            "Rating (out of 5) of Primary Book 1": "N/A",
            "Ratings (#) of Primary Book 1": "N/A",
            "Synopsis (if available)": "N/A",
            "Romantasy = Yes or No?": "No",
            "Romantasy Sub-Genre of series": "",
            "Name of agent": "Handspun Literary"
        })
        
    if new_rows:
        df_out = pd.DataFrame(new_rows)
        FINAL_COLUMNS = [
            "Name of Series", "Author Name", "Publisher", "GoodReads series link",
            "Number of PRIMARY books in the series", "Rating (out of 5) of Primary Book 1",
            "Ratings (#) of Primary Book 1", "Synopsis (if available)", "Romantasy = Yes or No?",
            "Romantasy Sub-Genre of series", "Name of agent"
        ]
        df_out = df_out.reindex(columns=FINAL_COLUMNS)
        
        print(f"Saving {len(df_out)} rows to {output_file}...")
        df_out.to_excel(output_file, index=False)
        
        try:
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from apply_jra_style import apply_styling
            apply_styling(output_file)
            print("Styling applied.")
        except Exception as e:
            print(f"Styling error: {e}")
            
        # Open the file for the user
        if os.name == 'nt':
            os.startfile(output_file)
    else:
        print("No valid rows found in input file.")

if __name__ == '__main__':
    format_handspun()
