import os
import sys
import pandas as pd
import requests
from bs4 import BeautifulSoup

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from apply_jra_style import apply_styling

EXCEL_FILE = r"E:\Internship\PocketFM\Next_Agency.xlsx"

def scrape_dhh_authors():
    print("Fetching DHH Literary Agency authors...")
    url = "https://www.dhhliteraryagency.com/our-authors"
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Exclude nav and footer links
    exclude_list = [
        '0', 'Skip to Content', 'Meet The Team', 'Our Authors', 'DHH Rights', 
        'Submissions', 'News', 'Back', 'Folder:\nMenu', 'here',
        'Sign up to our newsletter', 'Privacy Policy', 'Terms & Conditions'
    ]
    
    authors = []
    
    for a in soup.select('a'):
        href = a.get('href', '')
        text = a.text.strip().replace('\u200b', '') # Clean invisible characters
        
        if not text or not href: continue
        if text in exclude_list: continue
        if href.startswith('mailto:') or href.startswith('tel:'): continue
        if href == '/': continue
        
        # It's highly likely an author. 
        # Format names from "Last, First" to "First Last" if there's a comma
        if ',' in text:
            parts = text.split(',', 1)
            formatted_name = f"{parts[1].strip()} {parts[0].strip()}"
        else:
            formatted_name = text
            
        if formatted_name not in authors:
            authors.append(formatted_name)
            
    print(f"Extracted {len(authors)} authors. Saving to Excel...")
    
    df = pd.read_excel(EXCEL_FILE)
    
    new_rows = []
    for author in authors:
        row = {col: '' for col in df.columns}
        row['Author Name'] = author
        row['Name of agent in the main folder'] = 'DHH Literary Agency'
        new_rows.append(row)
        
    df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)
    
    apply_styling(EXCEL_FILE)
    print("Authors successfully saved to Next_Agency.xlsx and styling applied!")

if __name__ == "__main__":
    scrape_dhh_authors()
