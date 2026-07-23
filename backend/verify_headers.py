import pandas as pd

df = pd.read_excel(r"e:\Internship\PocketFM\Romantasy_v2_extracted.xlsx", header=None)
print("First row (Header):")
print(df.iloc[0].tolist()[:10]) # print first 10 columns
