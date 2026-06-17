import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from apply_jra_style import apply_styling

def scrape_boroughs():
    excel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "New_Agency.xlsx")
    
    # Check if the excel exists
    if os.path.exists(excel_path):
        df = pd.read_excel(excel_path)
    else:
        columns = [
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
            "Name of agent in the main folder"
        ]
        df = pd.DataFrame(columns=columns)

    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    books_data = []

    for page in range(19):
        print(f"Scraping page {page + 1}/19...")
        url = f"https://www.boroughspublishinggroup.com/books?page={page}"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch page {page}. Status code: {response.status_code}")
            continue
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for the book ul containers
        ul_elements = soup.find_all('ul')
        
        for ul in ul_elements:
            title_li = ul.find('li', class_='title')
            author_li = ul.find('li', class_='author')
            
            if title_li and author_li:
                title = title_li.text.strip()
                author = author_li.text.replace('by', '').strip()
                
                # Append to our data
                books_data.append({
                    "Name of Series": title,
                    "Author Name": author
                })
        
        time.sleep(1) # Be polite

    print(f"Found {len(books_data)} books total.")
    
    # Append the new data to df
    new_df = pd.DataFrame(books_data)
    
    if not new_df.empty:
        # Align columns
        for col in df.columns:
            if col not in new_df.columns:
                new_df[col] = None
                
        df = pd.concat([df, new_df], ignore_index=True)
        
        df.to_excel(excel_path, index=False)
        print(f"Saved data to {excel_path}")
        
        try:
            apply_styling(excel_path)
            print("Styling applied successfully.")
        except Exception as e:
            print(f"Error applying styling: {e}")

if __name__ == "__main__":
    scrape_boroughs()
