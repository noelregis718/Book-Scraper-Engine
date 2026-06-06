import pandas as pd
import os

base_dir = r'e:\Internship\PocketFM'
file1 = os.path.join(base_dir, 'books_scraped_updated_v2_backup.xlsx')
file2 = os.path.join(base_dir, 'books_scraped_updated_v2.xlsx')
output_file = os.path.join(base_dir, 'books_scraped_merged.xlsx')

df1 = pd.read_excel(file1)
df2 = pd.read_excel(file2)

# Merge the two DataFrames by appending them together
merged_df = pd.concat([df1, df2], ignore_index=True)

# Save the combined DataFrame
merged_df.to_excel(output_file, index=False)
print(f"Merged {len(df1)} rows and {len(df2)} rows into {len(merged_df)} total rows.")
print(f"Saved to {output_file}")
