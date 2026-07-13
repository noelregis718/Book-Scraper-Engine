import pandas as pd
import shutil

file_path = 'Next_Agency.xlsx'
backup_path = 'Next_Agency_backup.xlsx'

try:
    # Create a backup just in case
    shutil.copy(file_path, backup_path)
    
    # Read without treating the first row as a header
    df = pd.read_excel(file_path, header=None)
    
    print(f"Original shape: {df.shape}")
    
    # Keep from row 264 onwards (index 263)
    df_cleaned = df.iloc[263:].reset_index(drop=True)
    
    print(f"Cleaned shape: {df_cleaned.shape}")
    
    # Save back to the original file
    df_cleaned.to_excel(file_path, index=False, header=False)
    print("Successfully deleted the first 263 rows and updated Next_Agency.xlsx")

except Exception as e:
    print(f"Error: {e}")
