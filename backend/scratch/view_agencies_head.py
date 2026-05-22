import pandas as pd
df = pd.read_excel('Agency Crawls.xlsx', sheet_name='List of Agencies')
pd.set_option('display.max_columns', None)
print(df.columns)
print(df.head())
