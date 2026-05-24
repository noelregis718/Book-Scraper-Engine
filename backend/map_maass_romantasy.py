import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from romantasy_analyzer import analyze_catalog

def main():
    filepath = r"E:\Internship\PocketFM\Maass_Agency_Complete_List_With_Image_Books.xlsx"
    analyze_catalog(filepath)

if __name__ == "__main__":
    main()
