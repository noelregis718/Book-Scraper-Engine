import pandas as pd

file_path = 'Next_Agency.xlsx'
df = pd.read_excel(file_path, header=None)

print(df.head(3).to_string())
