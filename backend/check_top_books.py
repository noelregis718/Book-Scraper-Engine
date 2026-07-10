import pandas as pd
import time
for i in range(10):
    try:
        df = pd.read_excel('e:/Internship/PocketFM/Next_Agency.xlsx')
        print(f"Total Rows: {len(df)}")
        print(f"Top Books Found so far: {len(df) - 125}")
        break
    except Exception as e:
        time.sleep(1)
