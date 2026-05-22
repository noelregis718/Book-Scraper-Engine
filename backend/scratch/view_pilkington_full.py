import pandas as pd
df = pd.read_excel('Agency Crawls.xlsx', sheet_name='List of Agencies')
pilkington_rows = df[df.apply(lambda row: row.astype(str).str.contains('Pilkington', case=False).any(), axis=1)]
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
print(pilkington_rows)
