import pandas as pd

df = pd.read_excel(r"e:\Internship\PocketFM\Romantasy_v2_extracted.xlsx", header=1)
print(df.columns)
print(df.head(3))
