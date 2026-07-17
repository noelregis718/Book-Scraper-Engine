import pandas as pd

file_path = 'Publishing House.xlsx'
df = pd.read_excel(file_path)

# New sheet with only small agencies
df_small = df[df['Category'] == 'Small']
df_small.to_excel('Small Publishing Agencies.xlsx', index=False)
print("Created 'Small Publishing Agencies.xlsx' with only small agencies.")

# Remove large agencies from the original
df_no_large = df[df['Category'] != 'Large']
df_no_large.to_excel(file_path, index=False)
print("Removed large publishing agencies from 'Publishing House.xlsx'.")
