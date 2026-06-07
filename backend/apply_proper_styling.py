import sys
import os

sys.path.append(r"E:\Internship\PocketFM\backend")

from apply_jra_style import apply_styling

EXCEL_FILE = r"E:\Internship\PocketFM\books_from_uploaded_images.xlsx"

print(f"Applying proper JRA-style formatting to {EXCEL_FILE}...")
apply_styling(EXCEL_FILE)
print("Done!")
