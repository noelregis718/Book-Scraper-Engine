import pandas as pd
import webbrowser
import urllib.parse
import os

excel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Next_Agency.xlsx')

if os.path.exists(excel_path):
    df = pd.read_excel(excel_path)
    
    # Get first 10 book names
    books = df['Name of Series'].dropna().head(10).tolist()
    
    print(f"Opening {len(books)} browser tabs for Goodreads search...")
    for book in books:
        query = urllib.parse.quote_plus(book)
        search_url = f"https://www.goodreads.com/search?q={query}"
        print(f"Opening tab for: {book}")
        webbrowser.open_new_tab(search_url)
    
    print("Done!")
else:
    print(f"Excel file not found at {excel_path}")
