import pandas as pd
df = pd.read_excel('Agency Crawls.xlsx', sheet_name='List of Agencies')
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
print(df.iloc[13:18])
