import pandas as pd

def append_sheets():
    file1 = "Sheet 1 .xlsx"
    file2 = "Sheet 2.xlsx"
    
    print(f"Reading {file1}...")
    df1 = pd.read_excel(file1)
    
    print(f"Reading {file2}...")
    df2 = pd.read_excel(file2)
    
    # Find common columns
    common_cols = list(set(df1.columns).intersection(set(df2.columns)))
    print(f"Common columns found: {common_cols}")
    
    # Keep only common columns in Sheet 2
    df2_filtered = df2[common_cols]
    
    # Also ensure df1 only considers common columns for duplicate checking,
    # but we don't want to lose df1's original columns.
    # To append and keep uniqueness, we can concatenate and drop duplicates.
    
    original_len = len(df1)
    
    # Concatenate df1 and df2_filtered
    df_combined = pd.concat([df1, df2_filtered], ignore_index=True)
    
    # Drop duplicates based on the common columns, keeping the first occurrence (from df1)
    df_combined.drop_duplicates(subset=common_cols, keep='first', inplace=True)
    
    new_len = len(df_combined)
    added_rows = new_len - original_len
    
    print(f"Original rows in Sheet 1: {original_len}")
    print(f"Rows after appending unique data: {new_len}")
    print(f"Total new rows added: {added_rows}")
    
    # Save back to Sheet 1
    print(f"Saving updated data back to {file1}...")
    df_combined.to_excel(file1, index=False)
    print("Done!")

if __name__ == "__main__":
    append_sheets()
