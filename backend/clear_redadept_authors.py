import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from apply_jra_style import apply_styling

excel_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Next_Agency.xlsx")
df = pd.read_excel(excel_file)

# Clear the Author Name column
df['Author Name'] = ''

df.to_excel(excel_file, index=False)
apply_styling(excel_file)

print(f"Successfully cleared the Author Name column in {excel_file}")
