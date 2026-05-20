import pandas as pd

df = pd.read_excel('JRA_Bestsellers_Complete.xlsx')
df.head(10).to_csv('jra_columns.txt', index=False, encoding='utf-8')
