import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import os
import sys

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
excel_file = os.path.join(base_path, "Bradford_Literary_Formatted.xlsx")

def scrape_bradford_authors():
    url = "https://bradfordlit.com/our-authors/adult-fiction-and-non-fiction/"
    print(f"Scraping {url} with cloudscraper...")
    
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True})
    response = scraper.get(url)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract authors
    # Look for .et_pb_text_inner or just any <a> tags
    links = soup.find_all('a')
    raw_texts = [a.get_text(strip=True) for a in links if a.get_text(strip=True)]
    
    authors = set()
    skip_list = ["Home", "About", "The Agency", "Our Authors", "Adult Fiction and Non-Fiction", 
                 "Children's & Teen", "Illustrators", "How To Submit", "Contact", "Foreign Rights", 
                 "News", "Visit site \u00bb", "Visit site \u2192", "Visit site", "Read More"]
                 
    for text in raw_texts:
        if text and text not in skip_list and not any(ext in text.lower() for ext in ['.com', '.net', '.org', 'visit site']):
            words = text.split()
            if 2 <= len(words) <= 4:
                if all(w[0].isupper() or w[0] in "('\"" for w in words if w.isalpha()):
                    authors.add(text)
                    
    authors = sorted(list(authors))
    
    agents = ["Laura Bradford", "Hannah Andrade", "Rebecca Matte", "Kaitlyn Sanchez", "Hillary Fazzari", "Privacy Policy", "Cookie Policy"]
    valid_authors = [a for a in authors if a not in agents and "Adult Fiction" not in a and "Fiction and" not in a]

    print(f"Found {len(valid_authors)} valid authors.")
    for a in valid_authors[:10]:
        print(f" - {a}")
        
    if not os.path.exists(excel_file):
        print(f"Excel file not found: {excel_file}")
        return
        
    df = pd.read_excel(excel_file)
    existing_authors = set(df['Author Name'].dropna().tolist())
    
    new_rows = []
    for author in valid_authors:
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
        print(f"Appended {len(new_rows)} authors to Excel.")
        
        try:
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from apply_jra_style import apply_styling
            apply_styling(excel_file)
            print("Styling applied.")
        except Exception as e:
            print(f"Styling error: {e}")
    else:
        print("No new authors to add.")

if __name__ == '__main__':
    scrape_bradford_authors()
