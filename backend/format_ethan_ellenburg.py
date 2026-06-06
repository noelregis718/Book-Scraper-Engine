import pandas as pd
import os

target_file = r'E:\Internship\PocketFM\books_and_authors_from_image.xlsx'

# Load the excel file
df = pd.read_excel(target_file)

# Desired columns in order
desired_columns = [
    "Name of Series",
    "Author Name",
    "Publisher",
    "GoodReads series link",
    "Number of PRIMARY books in the series",
    "Rating (out of 5) of Primary Book 1",
    "Ratings (#) of Primary Book 1",
    "Synopsis (if available)",
    "Romantasy = Yes or No?",
    "Romantasy Sub-Genre of series",
    "Name of agent"
]

# Rename 'Book Name' to 'Name of Series' if it exists
if 'Book Name' in df.columns and 'Name of Series' not in df.columns:
    df.rename(columns={'Book Name': 'Name of Series'}, inplace=True)

# Add any missing columns from desired_columns
for col in desired_columns:
    if col not in df.columns:
        df[col] = None

# Figure out the final column order
# It should be the desired_columns, followed by any other columns that existed in the original file
existing_other_columns = [c for c in df.columns if c not in desired_columns]
final_column_order = desired_columns + existing_other_columns

df = df[final_column_order]

# Save it back
df.to_excel(target_file, index=False)

# Apply styling
sys_path = os.path.dirname(os.path.abspath(__file__))
import sys
if sys_path not in sys.path:
    sys.path.append(sys_path)
    
try:
    from apply_jra_style import apply_styling
    apply_styling(target_file)
    print("Styling applied.")
except Exception as e:
    print(f"Could not apply styling: {e}")

print("Excel file successfully formatted to the 11-column style.")
