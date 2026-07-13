import pandas as pd

try:
    df = pd.read_excel('Next_Agency.xlsx')
    print("DataFrame Shape:", df.shape)
    print("\n--- Columns ---")
    print(df.columns.tolist())
    
    print("\n--- Rows 260 to 264 ---")
    print(df.iloc[260:265].to_string())
    
    print("\n--- Rows 265 to 270 ---")
    print(df.iloc[265:271].to_string())

except Exception as e:
    print("Error:", e)
