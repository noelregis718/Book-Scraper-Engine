import pandas as pd
df = pd.read_excel('Agency Crawls.xlsx', sheet_name='List of Agencies')
# Filter for Pilkington
pilkington_rows = df[df.apply(lambda row: row.astype(str).str.contains('Pilkington', case=False).any(), axis=1)]
print(pilkington_rows)
