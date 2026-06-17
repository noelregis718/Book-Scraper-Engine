import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from apply_jra_style import apply_styling

columns = [
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
    "Name of agent in the main folder"
]

df = pd.DataFrame(columns=columns)
output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "New_Agency.xlsx")
df.to_excel(output_path, index=False)
print(f"Created {output_path}")

try:
    apply_styling(output_path)
    print("Styling applied.")
except Exception as e:
    print(f"Error applying styling: {e}")

import subprocess
subprocess.Popen(["start", output_path], shell=True)
