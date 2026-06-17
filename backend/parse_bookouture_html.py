import pandas as pd
from bs4 import BeautifulSoup
import os

def parse_html():
    excel_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Standard_11_Column_Format_2.xlsx')
    
    with open('bookouture_romance.html', 'r', encoding='utf-8') as f:
        html = f.read()
        
    soup = BeautifulSoup(html, 'html.parser')
    
    # The books are enclosed in <a> tags containing an h4 for title and p.MannequinContentPreview__book__author
    authors_elements = soup.find_all('p', class_='MannequinContentPreview__book__author')
    
    books_data = []
    seen = set()
    
    for author_elem in authors_elements:
        author = author_elem.get_text(strip=True)
        # Find the sibling h4 for title
        title_elem = author_elem.find_previous_sibling('h4')
        if title_elem:
            title = title_elem.get_text(strip=True)
            if title not in seen:
                seen.add(title)
                books_data.append({
                    'Name of Series': title,
                    'Author Name': author,
                    'Publisher': 'Bookouture',
                    'GoodReads series link': 'N/A',
                    'Number of PRIMARY books in the series': 'N/A',
                    'Rating (out of 5) of Primary Book 1': 'N/A',
                    'Ratings (#) of Primary Book 1': 'N/A',
                    'Synopsis (if available)': 'N/A',
                    'Romantasy = Yes or No?': 'N/A',
                    'Romantasy Sub-Genre of series': 'N/A',
                    'Name of agent': 'N/A'
                })
                
    print(f"Extracted {len(books_data)} books from the HTML.")
    
    if books_data:
        df = pd.read_excel(excel_path)
        new_df = pd.DataFrame(books_data)
        df = pd.concat([df, new_df], ignore_index=True)
        df.to_excel(excel_path, index=False)
        print("Successfully saved to Excel!")
        
if __name__ == '__main__':
    parse_html()
