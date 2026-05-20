import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from apply_jra_style import apply_styling

with open("page_text.txt", "r", encoding="utf-8") as f:
    lines = [line.strip() for line in f.readlines() if line.strip()]

start_idx = lines.index("Fiction ADULT") + 1
end_idx = lines.index("The P.S. Literary Agency (PSLA)")

books = []
title = ""
author = ""
previous_line = ""

for i in range(start_idx, end_idx):
    line = lines[i]
    if line in ["Fiction ADULT", "Fiction Children"]:
        continue
        
    if not title:
        title = line
    else:
        if line.startswith("("):
            title += " " + line
        elif line in ["and", ","]:
            author += " " + line
        else:
            if not author:
                author = line
            else:
                if previous_line in ["and", ","]:
                    author += " " + line
                else:
                    # Save the book and start a new one
                    books.append({"Name of Series": title, "Author Name": author})
                    title = line
                    author = ""
                    
    previous_line = line

# Append the last book
if title and author:
    books.append({"Name of Series": title, "Author Name": author})

# Now load New_Agency.xlsx and fill it
target_excel = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "New_Agency.xlsx")
df = pd.read_excel(target_excel)

for book in books:
    df.loc[len(df)] = {
        "Name of Series": book["Name of Series"],
        "Author Name": book["Author Name"]
    }

df.to_excel(target_excel, index=False)
print(f"Added {len(books)} books to {target_excel}")

try:
    apply_styling(target_excel)
    print("Styling applied.")
except Exception as e:
    print(f"Error applying style: {e}")

import subprocess
subprocess.Popen(["start", target_excel], shell=True)
