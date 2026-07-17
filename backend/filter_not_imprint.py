import pandas as pd

file_path = r'e:\Internship\PocketFM\Publishing House.xlsx'
df = pd.read_excel(file_path)

# Filter out rows where Category contains 'imprint'
mask = ~df['Category'].str.contains('imprint', case=False, na=False)
df_not_imprint = df[mask]

output_path = r'e:\Internship\PocketFM\Not_Imprint_Publishing_Houses.xlsx'
df_not_imprint.to_excel(output_path, index=False)
print("Created 'Not_Imprint_Publishing_Houses.xlsx' containing only non-imprint rows.")
