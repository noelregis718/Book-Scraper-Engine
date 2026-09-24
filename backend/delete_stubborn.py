import os
import shutil

target = r"\\?\e:\Internship\PocketFM\downloads\Pet Whisperer P.I."
try:
    os.system(f'rmdir /S /Q "{target}"')
    print("Deleted")
except Exception as e:
    print(e)
