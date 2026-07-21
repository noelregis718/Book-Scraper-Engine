import pandas as pd

def main():
    file_path = "e:/Internship/PocketFM/1852 Media.xlsx"
    print(f"Loading {file_path}...")
    
    df = pd.read_excel(file_path, engine="openpyxl")
    
    # Rename "Name of Series" to "Name of books"
    if 'Name of Series' in df.columns:
        df.rename(columns={'Name of Series': 'Name of books'}, inplace=True)
        print("Renamed 'Name of Series' -> 'Name of books'")
        
    # Add a new column named "Series" if it doesn't exist
    if 'Series' not in df.columns:
        # We insert it right after the first column (Name of books)
        df.insert(1, 'Series', None)
        print("Added new column 'Series'")
        
    print("Saving updated Excel file...")
    df.to_excel(file_path, index=False, engine="openpyxl")
    print("Success!")

if __name__ == "__main__":
    main()
