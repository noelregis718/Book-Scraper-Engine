import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

url = 'https://decadentpublishing.com/genres/young-adult/'
print(f"Scraping {url}")
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

books = []
for a in soup.select('.ProductDetails a.pname'):
    title = a.text.strip()
    if title:
        books.append(title)
        
print(f"Found {len(books)} books.")

excel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Next_Agency.xlsx')

if os.path.exists(excel_path):
    df = pd.read_excel(excel_path)
    # The existing dataframe might be empty, so we just create a new one with the same columns
    # and fill the 'Name of Series' with our book titles.
    
    new_data = []
    for book in books:
        row = {col: '' for col in df.columns}
        row['Name of Series'] = book
        new_data.append(row)
        
    new_df = pd.DataFrame(new_data)
    # Combine just in case there were already rows, though we know it's blank
    df = pd.concat([df, new_df], ignore_index=True)
    
    df.to_excel(excel_path, index=False)
    print(f"Saved to {excel_path}")
else:
    print(f"Excel file not found at {excel_path}")
