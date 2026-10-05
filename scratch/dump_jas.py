import pandas as pd
df = pd.read_excel('JAS Self-Pub Revenue Payouts (1).xlsx', sheet_name='Oct 1, 2026')
with open('jas_sheet.txt', 'w', encoding='utf-8') as f:
    f.write(df.head(20).to_string())
