import pandas as pd
df = pd.read_excel('e:/Internship/PocketFM/LDLA_Combined.xlsx')
print(df.tail(10)[['Name of Series', 'Author Name']])
