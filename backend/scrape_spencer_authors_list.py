import os
import requests
from bs4 import BeautifulSoup
import pandas as pd

EXCEL_FILE = r"E:\Internship\PocketFM\Spencer_Hill_Press.xlsx"

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

def clean_name(name):
    return " ".join(str(name).split()).strip()

def get_all_authors():
    authors = []
    page = 1
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    while True:
        url = "https://www.spencerhillpress.com/authors/"
        if page > 1:
            url += f"page/{page}/"
            
        print(f"Fetching {url}...")
        r = requests.get(url, headers=headers)
        
        if r.status_code != 200:
            print(f"Stopping at page {page} - status {r.status_code}")
            break
            
        soup = BeautifulSoup(r.content, 'html.parser')
        h6_tags = soup.find_all('h6')
        
        page_authors = []
        for h6 in h6_tags:
            if h6.get('id', '').startswith('post-'):
                a_tag = h6.find('a')
                if a_tag:
                    name = clean_name(a_tag.text)
                    if name and name not in authors:
                        page_authors.append(name)
                        authors.append(name)
                        
        if not page_authors:
            print(f"No more authors found on page {page}.")
            break
            
        print(f"Found {len(page_authors)} authors on page {page}")
        page += 1
        
    return authors

def main():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found.")
        return
        
    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)
    
    existing_authors = set(clean_name(a).lower() for a in df['Author Name'].dropna().tolist())
    
    print("\nScraping all authors from Spencer Hill Press...")
    scraped_authors = get_all_authors()
    
    print(f"\nTotal authors scraped: {len(scraped_authors)}")
    
    new_rows = []
    for author in scraped_authors:
        if author.lower() not in existing_authors:
            new_row = pd.Series(index=ELEVEN_COLUMN_HEADERS, dtype=object)
            new_row['Name of Series'] = "AUTHORS"
            new_row['Author Name'] = author
            new_row['Publisher'] = "Spencer Hill Press"
            
            new_row['GoodReads series link'] = "N/A"
            new_row['Number of PRIMARY books in the series'] = "N/A"
            new_row['Rating (out of 5) of Primary Book 1'] = "N/A"
            new_row['Ratings (#) of Primary Book 1'] = "N/A"
            new_row['Synopsis (if available)'] = "N/A"
            new_row['Romantasy = Yes or No?'] = "N/A"
            new_row['Romantasy Sub-Genre of series'] = "N/A"
            new_row['Name of agent'] = "N/A"
            new_rows.append(new_row)
            
    if new_rows:
        print(f"\nFound {len(new_rows)} NEW authors not currently in the Excel sheet.")
        print("Appending to Excel...")
        new_df = pd.DataFrame(new_rows, columns=ELEVEN_COLUMN_HEADERS)
        
        for col in df.columns:
            if col not in new_df.columns:
                new_df[col] = "N/A"
                
        combined_df = pd.concat([df, new_df], ignore_index=True)
        combined_df.to_excel(EXCEL_FILE, index=False)
        print("Done! Excel sheet updated.")
    else:
        print("\nAll scraped authors are already in the Excel sheet. No new rows added.")

if __name__ == "__main__":
    main()
