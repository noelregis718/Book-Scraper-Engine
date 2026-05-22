import pandas as pd
import os

def check_excel_status():
    file_path = r"e:\Internship\PocketFM\Amazon Keyword - Werewolves & Shifters.xlsx"
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    df = pd.read_excel(file_path)
    # Filter out rows where 'Book Title' is NaN
    valid_df = df.dropna(subset=['Book Title'])
    
    total_books = len(valid_df)
    last_book = valid_df.iloc[-1]
    second_last_book = valid_df.iloc[-2] if total_books > 1 else None

    print(f"Total Books in Excel: {total_books}")
    print(f"Last Book Title: {last_book['Book Title']}")
    print(f"Last Book ASIN: {last_book.get('ASIN', 'N/A')}")
    
    if second_last_book is not None:
        print(f"Second Last Book Title: {second_last_book['Book Title']}")
        print(f"Second Last Book ASIN: {second_last_book.get('ASIN', 'N/A')}")

if __name__ == "__main__":
    check_excel_status()
