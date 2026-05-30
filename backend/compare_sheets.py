import pandas as pd
import re

df1 = pd.read_csv(r'E:\Internship\PocketFM\alcove_press_romance_title_author.csv')
df2 = pd.read_excel(r'E:\Internship\PocketFM\Alcove_Press_Formatted.xlsx')

def norm(t):
    return re.sub(r'[^a-z0-9]', '', str(t).lower()) if pd.notna(t) else ''

s2_titles = set(norm(r['Name of Series']) for _, r in df2.iterrows())

missing = []
for _, r in df1.iterrows():
    title = norm(r['Title'])
    if title and title not in s2_titles:
        missing.append((r['Title'], r['Author']))

print(f"Total in CSV source: {len(df1)}")
print(f"Total in Excel target: {len(df2)}")
print(f"Missing: {len(missing)}")

if missing:
    for title, author in missing[:20]:
        print(f" - {title} by {author}")
    if len(missing) > 20:
        print(f" ... and {len(missing)-20} more")
