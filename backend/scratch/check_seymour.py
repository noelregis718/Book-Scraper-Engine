import pandas as pd
import os

catalog_path = r"E:\Internship\PocketFM\Seymour_Media_Catalog.xlsx"
if os.path.exists(catalog_path):
    df = pd.read_excel(catalog_path)
    print(f"Total Rows: {len(df)}")
    
    gr_col = 'GoodReads series link'
    if gr_col in df.columns:
        # Convert column to string safely to avoid attribute errors
        df[gr_col] = df[gr_col].astype(str)
        scraped_indices = df[df[gr_col].notna() & (df[gr_col].str.strip() != "") & (df[gr_col] != "nan") & (df[gr_col] != "N/A")].index.tolist()
        print(f"Total Scraped Rows: {len(scraped_indices)}")
        if scraped_indices:
            print(f"Scraped Row range (Excel 1-based): Row {scraped_indices[0] + 2} to Row {scraped_indices[-1] + 2}")
            
            # Let's count how many are scraped in blocks of 100 rows
            print("\nScraped rows density by blocks of 100 Excel rows:")
            for start in range(0, len(df), 100):
                end = min(start + 100, len(df))
                subset = df.iloc[start:end]
                scraped_in_block = subset[subset[gr_col].notna() & (subset[gr_col].str.strip() != "") & (subset[gr_col] != "nan") & (subset[gr_col] != "N/A")]
                print(f"Rows {start+2} to {end+1}: {len(scraped_in_block)} scraped")
                
            target_rows = []
            for r in range(len(df)):
                row_num = r + 2
                book_title = df.loc[r, 'Name of Series']
                gr_link = df.loc[r, gr_col]
                
                if book_title and str(book_title).strip() != "" and str(book_title).strip() != "nan" and book_title != "N/A":
                    title_str = str(book_title).strip()
                    if title_str[0].isdigit():
                        continue
                    if not gr_link or str(gr_link).strip() == "" or str(gr_link).strip() == "nan" or gr_link == "N/A" or not str(gr_link).strip().startswith("http"):
                        target_rows.append((row_num, title_str, str(df.loc[r, 'Author Name']).strip()))
            
            print(f"\nTotal eligible unscraped rows remaining: {len(target_rows)}")
            if target_rows:
                print(f"Next 5 rows to be scraped in the next batch:")
                for r_info in target_rows[:5]:
                    print(f"Row {r_info[0]}: Author='{r_info[2]}', Book='{r_info[1]}'")
        else:
            print("No rows are scraped!")
    else:
        print(f"Column '{gr_col}' not found.")
else:
    print(f"Seymour Media Catalog not found at {catalog_path}")
