import pandas as pd
import os

file_path = r"E:\Internship\PocketFM\Crime_Thriller_Template.xlsx"
df = pd.read_excel(file_path)
print("Columns in Excel:")
for col in df.columns:
    print(f"- {col}")
