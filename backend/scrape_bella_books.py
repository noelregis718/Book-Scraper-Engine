import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

base_url = "https://www.bellabooks.com/category/browse-by-genre/genre-romance/"
excel_path = r"e:\Internship\PocketFM\Books_Scraping_Template.xlsx"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

data = []

print("Aggressively scraping pages 51 to 60...")
for page in range(51, 61):
    if page == 1:
        url = base_url
    else:
        url = f"{base_url}page/{page}/"
        
    print(f"Scraping {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Failed to fetch page {page}. Status code: {response.status_code}")
            break
            
        soup = BeautifulSoup(response.content, 'html.parser')
        product_cards = soup.find_all('div', class_='product-card')
        
        if not product_cards:
            print(f"No more products found on page {page}.")
            break
            
        for card in product_cards:
            title_elem = card.find('h3')
            author_elem = card.find('p')
            
            if title_elem and author_elem:
                title = title_elem.get_text(strip=True)
                author = author_elem.get_text(strip=True)
                
                data.append({
                    "Name of Series": title,
                    "Author Name": author
                })
    except Exception as e:
        print(f"Error on page {page}: {e}")
        break

if data:
    print(f"Successfully scraped {len(data)} books. Saving to Excel...")
    df_new = pd.DataFrame(data)
    
    if os.path.exists(excel_path):
        df_exist = pd.read_excel(excel_path)
        
        # Append rows with matching column names
        for index, row in df_new.iterrows():
            new_row = {col: None for col in df_exist.columns}
            new_row['Name of Series'] = row['Name of Series']
            new_row['Author Name'] = row['Author Name']
            df_exist = pd.concat([df_exist, pd.DataFrame([new_row])], ignore_index=True)
            
        df_exist.to_excel(excel_path, index=False)
        print(f"Successfully appended to {excel_path}")
    else:
        print(f"Error: {excel_path} not found.")
else:
    print("No data was scraped.")
