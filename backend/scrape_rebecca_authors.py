import requests
from bs4 import BeautifulSoup
import pandas as pd
import sys
import subprocess
import os

EXCEL_FILE = r"E:\Internship\PocketFM\rebecca_freidmann_authors.xlsx"

def scrape_authors():
    url = "https://rfliterary.com/authors/"
    print(f"Fetching {url}...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Authors are inside <p style="text-align: center"> within the entry-content
    content_div = soup.find('div', class_='entry-content')
    p_tags = content_div.find_all('p')
    
    authors = []
    for p in p_tags:
        text = p.get_text(strip=True)
        # Skip empty lines, the image line, and the header line
        if not text or text == "Authors are listed alphabetically by LAST NAME" or text == "Team":
            continue
            
        # Clean up any trailing/leading spaces or strange characters
        text = text.replace('\xa0', ' ').strip()
        if text:
            authors.append(text)
            
    print(f"Found {len(authors)} authors on the website.")
    
    print("Updating Excel file...")
    df = pd.read_excel(EXCEL_FILE)
    existing_authors = set(df['Author Name'].dropna().str.strip().str.lower())
    
    new_rows = []
    for author in authors:
        if author.lower() not in existing_authors:
            new_rows.append({
                "Name of Series": "",
                "Author Name": author,
                "Publisher": "",
                "GoodReads series link": "",
                "Number of PRIMARY books in the series": "",
                "Rating (out of 5) of Primary Book 1": "",
                "Ratings (#) of Primary Book 1": "",
                "Synopsis (if available)": "",
                "Romantasy = Yes or No?": "",
                "Romantasy Sub-Genre of series": "",
                "Name of agent": "Rebecca Freidmann"
            })
            
    if new_rows:
        print(f"Adding {len(new_rows)} new authors to the sheet...")
        new_df = pd.DataFrame(new_rows)
        df = pd.concat([df, new_df], ignore_index=True)
        df.to_excel(EXCEL_FILE, index=False)
        
        sys.path.append(r'E:\Internship\PocketFM\backend')
        try:
            from style_rebecca_freidmann import apply_styling
            apply_styling(EXCEL_FILE)
        except Exception as e:
            print(f"Styling failed: {e}")
    else:
        print("No new authors found to add.")
        
    print("Opening Excel file...")
    subprocess.Popen(["start", EXCEL_FILE], shell=True)
    print("Done!")

if __name__ == "__main__":
    scrape_authors()
