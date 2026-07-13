import pandas as pd

file_path = 'Next_Agency.xlsx'
df = pd.read_excel(file_path, header=None)

print(f"Dataframe shape: {df.shape}")
print("First row data:")
for i, val in enumerate(df.iloc[0]):
    print(f"Column {i}: {val}")
