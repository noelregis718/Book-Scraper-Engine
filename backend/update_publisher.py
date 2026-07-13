import pandas as pd

file_path = 'Next_Agency.xlsx'

try:
    # Read the file
    df = pd.read_excel(file_path, header=None)
    
    # Let's clean up the residual "David Young" author row if it's there
    if pd.isna(df.iloc[0, 0]) and not pd.isna(df.iloc[0, 1]):
        df = df.iloc[1:].reset_index(drop=True)
        print("Dropped residual author row.")
        
    # Column 10 is the agency/publisher column. Let's fill it for all rows.
    df[10] = "DHH Literary Agency"
    
    # Save back
    df.to_excel(file_path, index=False, header=False)
    
    print(f"Updated shape: {df.shape}")
    print("Successfully set the publisher name 'DHH Literary Agency' for all rows.")

except Exception as e:
    print(f"Error: {e}")
