import pandas as pd
df = pd.read_excel('e:/Internship/PocketFM/LDLA_Combined.xlsx')
print(f"Rows: {len(df)}")
# Search for 'Breathe and Count Back from Ten'
breathe = df[df['Name of Series'].astype(str).str.contains('Breathe and Count', case=False, na=False)]
if not breathe.empty:
    print("Found Breathe and Count:")
    print(breathe[['Name of Series', 'Author Name']])
else:
    print("Not found!")
