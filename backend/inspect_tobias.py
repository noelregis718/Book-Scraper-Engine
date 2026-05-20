import pandas as pd

df = pd.read_excel('../Tobias_All_144_Books.xlsx')
df.head(10).to_csv('tobias_preview.txt', index=False, encoding='utf-8')
with open('tobias_info.txt', 'w', encoding='utf-8') as f:
    f.write("Columns:\n")
    for c in df.columns.tolist():
        f.write(f"  {c}\n")
    f.write(f"\nShape: {df.shape}\n")
