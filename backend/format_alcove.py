import pandas as pd
import os
import sys

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_file = os.path.join(base_path, "alcove_press_romance_title_author.csv")
excel_file = os.path.join(base_path, "Alcove_Press_Formatted.xlsx")

def format_alcove():
    if not os.path.exists(csv_file):
        print(f"File not found: {csv_file}")
        return
        
    print(f"Loading {csv_file}...")
    df_in = pd.read_csv(csv_file)
    
    new_rows = []
    for _, row in df_in.iterrows():
        title = row.get('Title', '')
        author = row.get('Author', '')
        
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
        df_out = pd.DataFrame(new_rows)
        FINAL_COLUMNS = [
            "Name of Series", "Author Name", "Publisher", "GoodReads series link",
            "Number of PRIMARY books in the series", "Rating (out of 5) of Primary Book 1",
            "Ratings (#) of Primary Book 1", "Synopsis (if available)", "Romantasy = Yes or No?",
            "Romantasy Sub-Genre of series", "Name of agent"
        ]
        df_out = df_out.reindex(columns=FINAL_COLUMNS)
        
        print(f"Saving {len(df_out)} rows to {excel_file}...")
        df_out.to_excel(excel_file, index=False)
        
        try:
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from apply_jra_style import apply_styling
            apply_styling(excel_file)
            print("Styling applied.")
        except Exception as e:
            print(f"Styling error: {e}")
    else:
        print("No valid rows found in CSV.")

if __name__ == '__main__':
    format_alcove()
