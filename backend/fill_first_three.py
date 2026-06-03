import pandas as pd
import os

EXCEL_FILE = r"E:\Internship\PocketFM\corvisiero_merged.xlsx"

def fill_first_three():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)
    
    # Row 0: The Echoes of Radfield Hall
    df.at[0, "GoodReads series link"] = "N/A (Upcoming 2027)"
    df.at[0, "Number of PRIMARY books in the series"] = "1"
    df.at[0, "Rating (out of 5) of Primary Book 1"] = "N/A"
    df.at[0, "Ratings (#) of Primary Book 1"] = "N/A"
    df.at[0, "Synopsis (if available)"] = "Forthcoming book by Heather Carter, sold to City Owl Press for publication in 2027."
    df.at[0, "Romantasy = Yes or No?"] = "No"
    df.at[0, "Romantasy Sub-Genre of series"] = ""
    
    # Row 1: She Who Makes Monsters
    df.at[1, "GoodReads series link"] = "N/A (Upcoming 2027)"
    df.at[1, "Number of PRIMARY books in the series"] = "1"
    df.at[1, "Rating (out of 5) of Primary Book 1"] = "N/A"
    df.at[1, "Ratings (#) of Primary Book 1"] = "N/A"
    df.at[1, "Synopsis (if available)"] = "Follows a teenage Mary Shelley who runs away from home with Percy Shelley to track down a secret society of necromancers in an attempt to resurrect her mother."
    df.at[1, "Romantasy = Yes or No?"] = "Yes"
    df.at[1, "Romantasy Sub-Genre of series"] = "Gothic Dark Romantasy"

    # Row 2: The Poisoned Pen Podcast
    df.at[2, "GoodReads series link"] = "N/A (Podcast, not a book)"
    df.at[2, "Number of PRIMARY books in the series"] = "N/A"
    df.at[2, "Rating (out of 5) of Primary Book 1"] = "N/A"
    df.at[2, "Ratings (#) of Primary Book 1"] = "N/A"
    df.at[2, "Synopsis (if available)"] = "A well-known book-focused podcast produced by The Poisoned Pen Bookstore in Scottsdale, Arizona."
    df.at[2, "Romantasy = Yes or No?"] = "No"
    df.at[2, "Romantasy Sub-Genre of series"] = ""

    print(f"Saving {EXCEL_FILE} with updated manual entries for the first 3 rows...")
    df.to_excel(EXCEL_FILE, index=False)
    print("Done!")

if __name__ == '__main__':
    fill_first_three()
