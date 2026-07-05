import pandas as pd
import sys
import os

sys.path.append('e:/Internship/PocketFM/backend')
from apply_jra_style import apply_styling

file_path = 'e:/Internship/PocketFM/Next_Agency.xlsx'
df = pd.read_excel(file_path)

df['Name of agent in the main folder'] = 'Tracey Cheetham'
df.to_excel(file_path, index=False)
apply_styling(file_path)

print('Agent name successfully updated to Tracey Cheetham!')
