import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from apply_jra_style import apply_styling

excel_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Next_Agency.xlsx")
df = pd.read_excel(excel_file)

# Excel row 2 is pandas index 0
# Excel row 11 is pandas index 9
idx1, idx2 = 0, 9

# Swap the two rows
temp = df.iloc[idx1].copy()
df.iloc[idx1] = df.iloc[idx2]
df.iloc[idx2] = temp

df.to_excel(excel_file, index=False)
apply_styling(excel_file)

print(f"Successfully swapped Excel Row 2 (index {idx1}) with Excel Row 11 (index {idx2}).")
