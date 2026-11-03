with open(r"backend/mega_goodreads_scraper.py", "r", encoding="utf-8") as f:
    code = f.read()

# Fix dtype inference
old_dtype_block = '''    # Ensure all target columns exist
    for col in ["GoodReads_Series_URL", "Book1_Rating", "Book1_Num_Ratings", "Num_Primary_Books_in_Series", "Total_Page_Count_of_Primary_Books", "Approx Length (Hrs)", "Genre Tags", "Synopsis", "Romantasy Checker"]:
        if col not in df.columns:
            df[col] = None'''

new_dtype_block = '''    # Ensure all target columns exist and are object dtype so strings can be assigned without float64 error
    for col in ["GoodReads_Series_URL", "Book1_Rating", "Book1_Num_Ratings", "Num_Primary_Books_in_Series", "Total_Page_Count_of_Primary_Books", "Approx Length (Hrs)", "Genre Tags", "Goodreads Synopsis", "Synopsis", "Romantasy Checker"]:
        if col not in df.columns:
            df[col] = None
        df[col] = df[col].astype(object)'''

code = code.replace(old_dtype_block, new_dtype_block)

with open(r"backend/mega_goodreads_scraper.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Applied dtype fix to backend/mega_goodreads_scraper.py!")

