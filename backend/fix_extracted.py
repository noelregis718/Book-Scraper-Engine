import pandas as pd

file_path = r"e:\Internship\PocketFM\Romantasy_v2_extracted.xlsx"
df = pd.read_excel(file_path)

# The current columns are actually the first row of data, plus the 5 appended empty columns
current_columns = list(df.columns)
data_row_1 = current_columns[:28] # first 28 are the real data

original_headers = ['S. No.', 'Title', 'Author Name', 'GR Book 1 link', 'Agency (if)', 'GR Series Link', 'No. of books in the series', 'Page count', 'No. of Hours (appx)', 'Subjective Review (if needed)', 'Latest Stage', 'Status (for Anvita)', 'Licensor / POC', 'No. of books Licensed/To be licensed', 'Molly Comments', 'Vikrant Comments', 'Restrictions', 'GR ratings', 'Tier', 'MG', 'Rev. Share', 'Gross/Net', 'Confidence Level', 'Sub-Genre', 'Drive link', 'Unnamed: 25', 'Unnamed: 26', 'Unnamed: 27']

# Drop the appended columns (indices 28 to end)
df = df.iloc[:, :28]

# Create a new dataframe with original headers
df.columns = original_headers

# Create a dataframe for the first row of data
row1_df = pd.DataFrame([data_row_1], columns=original_headers)

# Concatenate them
df_fixed = pd.concat([row1_df, df], ignore_index=True)

df_fixed.to_excel(file_path, index=False)
print("File fixed!")
