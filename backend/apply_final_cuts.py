import pandas as pd

def main():
    file_path = 'e:/Internship/PocketFM/Sheet3_With_Calculated_Hours.xlsx'
    print(f"Loading {file_path}...")
    df = pd.read_excel(file_path, engine='openpyxl')
    
    initial_count = len(df)
    
    # Cut 1: Primary Books > 4
    books_numeric = pd.to_numeric(df['No. of Primary Books'], errors='coerce').fillna(0)
    df = df[books_numeric > 4]
    after_books = len(df)
    
    # Cut 2: Hours > 40
    # (Using the column where missing hours were already filled using the boss's formula)
    hours_numeric = pd.to_numeric(df['No. of Hours'], errors='coerce').fillna(0)
    df = df[hours_numeric > 40]
    after_hours = len(df)
    
    out_path = 'e:/Internship/PocketFM/Final_CT_Wishlist_Filtered.xlsx'
    df.to_excel(out_path, index=False)
    
    print("\n--- Filter Results ---")
    print(f"Original list size: {initial_count}")
    print(f"Cut {initial_count - after_books} series that had 4 or fewer books.")
    print(f"Cut {after_books - after_hours} series that fell under 40 hours.")
    print(f"Final pristine list size: {after_hours}")
    print(f"Successfully saved to: {out_path}")

if __name__ == '__main__':
    main()
