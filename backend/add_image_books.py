import pandas as pd
import os
import sys

file_path = r"e:\Internship\PocketFM\New_Agency.xlsx"

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from apply_jra_style import apply_styling

books = [
    {"Name of Series": "She is a Haunting", "Author Name": "Trang Thanh Tran"},
    {"Name of Series": "Guardians of Dawn: Zhara", "Author Name": "S. Jae-Jones"},
    {"Name of Series": "Road of the Lost", "Author Name": "Nafiza Azad"},
    {"Name of Series": "Tender Morsels", "Author Name": "Margo Lanagan"},
    {"Name of Series": "A Touch of Blood", "Author Name": "Sajni Patel"},
    {"Name of Series": "Blood Moon", "Author Name": "Britney S. Lewis"},
    {"Name of Series": "Cinder", "Author Name": "Marissa Meyer"},
    {"Name of Series": "Sabriel", "Author Name": "Garth Nix"},
    {"Name of Series": "Uglies", "Author Name": "Scott Westerfeld"},
    {"Name of Series": "Jellicoe Road", "Author Name": "Melina Marchetta"},
    {"Name of Series": "The Prince & The Apocalypse", "Author Name": "Kara McDowell"},
    {"Name of Series": "Well, That Was Unexpected", "Author Name": "Jesse Q. Sutanto"},
    {"Name of Series": "Tenderly, I Am Devoured", "Author Name": "Lyndall Clipstone"},
    {"Name of Series": "The Book of Gothel", "Author Name": "Mary McMyne"},
    {"Name of Series": "The Sweet Blue Distance", "Author Name": "Sara Donati"},
    {"Name of Series": "The Trouble with Hating You", "Author Name": "Sajni Patel"},
    {"Name of Series": "Sir Hereward and Mister Fitz", "Author Name": "Garth Nix"}
]

df = pd.read_excel(file_path)

# Create a DataFrame from the new books
new_df = pd.DataFrame(books)

# Concatenate the original and new DataFrames
updated_df = pd.concat([df, new_df], ignore_index=True)

# Save back to Excel
updated_df.to_excel(file_path, index=False)
print("Books added successfully.")

try:
    apply_styling(file_path)
    print("Styling applied.")
except Exception as e:
    print(f"Error applying styling: {e}")

# Open the excel sheet
import subprocess
subprocess.Popen(["start", file_path], shell=True)
