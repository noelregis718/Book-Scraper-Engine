import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from apply_jra_style import apply_styling

target_excel = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "New_Agency.xlsx")

df = pd.read_excel(target_excel)
df["Publisher"] = "P.S. Literary Agency"
df["Name of agent"] = "Maria Vicente"
df.to_excel(target_excel, index=False)
print(f"Updated {len(df)} rows in {target_excel}")

try:
    apply_styling(target_excel)
    print("Styling applied.")
except Exception as e:
    print(f"Error applying style: {e}")

import subprocess
subprocess.Popen(["start", target_excel], shell=True)
