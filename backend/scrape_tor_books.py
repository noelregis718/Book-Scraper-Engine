import bs4
import pandas as pd
import sys

def scrape_tor(file_path):
    print(f"Reading {file_path}...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        sys.exit(1)
        
    soup = bs4.BeautifulSoup(html_content, 'html.parser')
    cards = soup.find_all('div', class_='card-post-content')
    
    books = []
    for card in cards:
        title_tag = card.find('h3')
        author_tag = card.find('span', class_='author-item')
        
        if title_tag and author_tag:
            title = title_tag.text.strip()
            author = author_tag.text.strip()
            books.append({'Name of Series': title, 'Author Name': author})
            
    print(f"Found {len(books)} books.")
    
    excel_file = 'agency_template.xlsx'
    try:
        df = pd.read_excel(excel_file)
    except FileNotFoundError:
        print(f"Error: {excel_file} not found.")
        sys.exit(1)
        
    new_df = pd.DataFrame(books)
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_excel(excel_file, index=False)
    print("Saved to excel.")

if __name__ == '__main__':
    file_path = sys.argv[1] if len(sys.argv) > 1 else 'tor_romance.html'
    scrape_tor(file_path)
