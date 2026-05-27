import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

EXCEL_FILE = r"E:\Internship\PocketFM\CozyRomantasy_Merged.xlsx"

# Master list from the images
image_books = [
    {"Title": "Saltwater and Sweets", "Author": "KD Fraser"},
    {"Title": "A Witch and Her Dragon", "Author": "Emberly Wyndham"},
    {"Title": "Must Love Scones & Secrets", "Author": "Maisy Magill"},
    {"Title": "The Rebellious Fae's Guide to Family Rivalries", "Author": "Ariana Jade"},
    {"Title": "Potions & Prejudice", "Author": "Tee Harlowe"},
    {"Title": "The Queen & The Candle Maker", "Author": "Heloise Hull"},
    {"Title": "When the Baker met the Dragon", "Author": "Lila Appleton"},
    {"Title": "Bargains with Benefits", "Author": "Jillian Witt"},
    {"Title": "The Hidden Magic of Ordinary Things", "Author": "Olivia McCullough"},
    {"Title": "My Big Fat Orc Wedding", "Author": "Lucy Rose Edwards"},
    {"Title": "Love Letters and Lemon Drops", "Author": "Laura Greenwood"}
]

ELEVEN_COLUMN_HEADERS = [
    "Name of Series",
    "Author Name",
    "Publisher",
    "GoodReads series link",
    "Number of PRIMARY books in the series",
    "Rating (out of 5) of Primary Book 1",
    "Ratings (#) of Primary Book 1",
    "Synopsis (if available)",
    "Romantasy = Yes or No?",
    "Romantasy Sub-Genre of series",
    "Name of agent"
]

def clean_title(t):
    return str(t).lower().replace("&", "and").replace(" ", "")

def main():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    df = pd.read_excel(EXCEL_FILE)
    
    # We will reconstruct a cleaner dataframe
    new_rows = []
    
    # Track which image books we found
    found_books = set()
    
    for idx, row in df.iterrows():
        title = str(row.get('Name of Series', '')).strip()
        
        # Skip garbage rows from bad scraping
        if title.upper() == 'AUTHORS' or title == 'nan' or not title:
            continue
            
        # The scraper incorrectly parsed 'Emberly Wyndham' as a title
        if 'Emberly Wyndham' in title:
            # We will handle it by matching the real book
            continue
            
        # Find match in image_books
        matched = False
        for ib in image_books:
            if clean_title(ib["Title"]) in clean_title(title) or clean_title(title) in clean_title(ib["Title"]):
                # Found it! Let's fix the author and title just in case
                row['Name of Series'] = ib["Title"]
                row['Author Name'] = ib["Author"]
                new_rows.append(row)
                found_books.add(ib["Title"])
                matched = True
                break
                
        if not matched:
            # Keep it if it's some other valid book we missed
            new_rows.append(row)
            
    # Now add any books from the images that were NOT in the original sheet
    for ib in image_books:
        if ib["Title"] not in found_books:
            print(f"Adding completely missing book: {ib['Title']}")
            new_row = pd.Series(index=ELEVEN_COLUMN_HEADERS, dtype=object)
            new_row['Name of Series'] = ib["Title"]
            new_row['Author Name'] = ib["Author"]
            new_row['Publisher'] = "Cozy Coven"
            new_row['Number of PRIMARY books in the series'] = 1
            new_row['Rating (out of 5) of Primary Book 1'] = "N/A"
            new_row['Ratings (#) of Primary Book 1'] = "N/A"
            new_row['Synopsis (if available)'] = ""
            new_rows.append(new_row)
            
    # Combine and save
    new_df = pd.DataFrame(new_rows, columns=ELEVEN_COLUMN_HEADERS)
    
    print(f"Saving updated list with {len(new_df)} books...")
    new_df.to_excel(EXCEL_FILE, index=False)
    
    try:
        from classify_cozy_final import main as classify_main
        print("Running classification on the updated sheet...")
        classify_main()
    except Exception as e:
        print(f"Error classifying: {e}")
        try:
            from apply_jra_style import apply_styling
            apply_styling(EXCEL_FILE)
            import subprocess
            subprocess.Popen(["start", EXCEL_FILE], shell=True)
        except:
            pass

if __name__ == '__main__':
    main()
