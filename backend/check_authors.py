import pandas as pd
df = pd.read_excel('E:/Internship/PocketFM/Stonesong_Books.xlsx')
unknown_count = (df['Author Name'] == 'Unknown').sum()
print(f"Missing authors left: {unknown_count}")
print(f"Newly saved authors: {99 - unknown_count}")
