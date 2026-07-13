import pandas as pd

try:
    # 1. Get original headers from the backup file
    df_backup = pd.read_excel('Next_Agency_backup.xlsx', nrows=0)
    original_columns = df_backup.columns.tolist()
    
    # 2. Read the current cleaned data
    df_clean = pd.read_excel('Next_Agency.xlsx', header=None)
    
    # 3. Apply the original headers to the cleaned data
    df_clean.columns = original_columns
    
    # 4. Set the Publisher column (which the user asked for earlier)
    df_clean['Publisher'] = "DHH Literary Agency"
    
    # 5. Set the Agent column (which the user asked for just now)
    df_clean['Name of agent in the main folder'] = "Diana Beaumont"
    
    # 6. Save the final perfectly formatted file (now including headers!)
    df_clean.to_excel('Next_Agency.xlsx', index=False, header=True)
    
    print("Shape:", df_clean.shape)
    print("Successfully restored headers, set Publisher to 'DHH Literary Agency', and Agent to 'Diana Beaumont'.")
    
except Exception as e:
    print(e)
