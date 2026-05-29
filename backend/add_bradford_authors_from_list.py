import pandas as pd
import os
import sys

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
excel_file = os.path.join(base_path, "Bradford_Literary_Formatted.xlsx")

authors_string = """Natalie Anderson
Duley Anderson
AC Arthur
Tessa Bailey
Jenn Bennett
Laura Bradford
Sarah Castille
Twinkie Chan
Amy Z. Chan
Emmy Curtis
Victoria De La O
Jen Devon
HelenKay Dimon
Monique Domovitch
A. Rae Dunlap
Barbara Dunlop
kc dyer
Hope Ellis
Jacqueline Firkins
Courtney Floyd
Amanda Gayle
Jess Granger
Tamara Hubbard
Sara Johnson
Alison Kent
Caroline Kimberly
Thien-Kim Lam
Katie Lane
Soraya Lane
Kat Latham
Ellen Lindseth
Catherine Linka
Thea Liu
Erin McCarthy
Nikoo & Jim McGoldrick
Cara McKenna
Victoria Morgan
Danica Nava
Tanner Orel
Ellie Palmer
Katee Robert
Maggie Robinson
Caty Rogan
Julie Tieu
Amarie Wheeler"""

def add_authors():
    if not os.path.exists(excel_file):
        print(f"File not found: {excel_file}")
        return
        
    df = pd.read_excel(excel_file)
    existing_authors = set(df['Author Name'].dropna().tolist())
    
    # Also handle some edge cases if the user provided agent names in the list.
    # We will assume all names in the string are authors.
    authors = [a.strip() for a in authors_string.split("\n") if a.strip()]
    
    new_rows = []
    for author in authors:
        if author not in existing_authors:
            new_rows.append({
                "Name of Series": "",
                "Author Name": author,
                "Publisher": "",
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
        new_df = pd.DataFrame(new_rows)
        FINAL_COLUMNS = [
            "Name of Series", "Author Name", "Publisher", "GoodReads series link",
            "Number of PRIMARY books in the series", "Rating (out of 5) of Primary Book 1",
            "Ratings (#) of Primary Book 1", "Synopsis (if available)", "Romantasy = Yes or No?",
            "Romantasy Sub-Genre of series", "Name of agent"
        ]
        new_df = new_df.reindex(columns=FINAL_COLUMNS)
        df = pd.concat([df, new_df], ignore_index=True)
        
        df.to_excel(excel_file, index=False)
        print(f"Appended {len(new_rows)} new authors from user list to Excel.")
        
        try:
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from apply_jra_style import apply_styling
            apply_styling(excel_file)
            print("Styling applied.")
        except Exception as e:
            print(f"Styling error: {e}")
    else:
        print("All authors in the list are already in the spreadsheet.")

if __name__ == '__main__':
    add_authors()
