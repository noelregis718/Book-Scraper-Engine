import pandas as pd
file_path = r"E:\Internship\PocketFM\Romantasy _ Self Publication Master (1).xlsx"
xl = pd.ExcelFile(file_path)
print(xl.sheet_names)
