import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

EXCEL_FILE = r"E:\Internship\PocketFM\books_and_authors_from_image.xlsx"

new_books = [
    {"Name of Series": "The Shattering Peace", "Author Name": "John Scalzi"},
    {"Name of Series": "The Fallen & The Kiss of Dusk", "Author Name": "Carissa Broadbent"},
    {"Name of Series": "To Kill A Badger", "Author Name": "Shelly Laurenston"},
    {"Name of Series": "Death in the Jungle", "Author Name": "Candace Fleming"},
    {"Name of Series": "Breakneck Bay", "Author Name": "Faith Gardner"},
    {"Name of Series": "Ask for Andrea", "Author Name": "Noelle W. Ihli"},
    {"Name of Series": "Daughter of No Worlds", "Author Name": "Carissa Broadbent"},
    {"Name of Series": "Iron & Embers", "Author Name": "Helen Scheuerer"},
    {"Name of Series": "Kitty St. Clair's Last Dance", "Author Name": "Kate Robb"},
    {"Name of Series": "We Are Legion (We Are Bob)", "Author Name": "Dennis E. Taylor"},
    {"Name of Series": "King of Ravens", "Author Name": "Clare Sager"},
    {"Name of Series": "Corvus", "Author Name": "Marko Kloos"}
]

def add_new_books():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)
    
    new_rows = []
    for b in new_books:
        row_data = {
            "Name of Series": b["Name of Series"],
            "Author Name": b["Author Name"],
            "Publisher": "",
            "GoodReads series link": "",
            "Number of PRIMARY books in the series": "1",
            "Rating (out of 5) of Primary Book 1": "N/A",
            "Ratings (#) of Primary Book 1": "N/A",
            "Synopsis (if available)": "N/A",
            "Romantasy = Yes or No?": "",
            "Romantasy Sub-Genre of series": "",
            "Name of agent": "Ethan Ellenburg"
        }
        new_rows.append(row_data)

    new_df = pd.DataFrame(new_rows)
    df = pd.concat([df, new_df], ignore_index=True)

    print(f"Saving {len(df)} total rows to {EXCEL_FILE}...")
    df.to_excel(EXCEL_FILE, index=False)
    
    try:
        from apply_jra_style import apply_styling
        apply_styling(EXCEL_FILE)
        print("Styling applied.")
    except Exception as e:
        print(f"Could not apply styling: {e}")

if __name__ == '__main__':
    add_new_books()
