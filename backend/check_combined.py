import pandas as pd

df = pd.read_excel('e:/Internship/PocketFM/LDLA_Combined.xlsx')
print(f"Total rows: {len(df)}")
print(df[['Name of Series', 'Author Name']].head(10))
