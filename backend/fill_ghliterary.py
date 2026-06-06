import os
import pandas as pd
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

EXCEL_FILE = r"E:\Internship\PocketFM\books_authors_corrected.xlsx"

def fill_ghliterary():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)

    if df.empty:
        print("Excel file is empty.")
        return

    # Update columns
    df["Publisher"] = "Gandolfo Helin & Fountain Literary"
    df["Name of agent"] = "Italia Gandolfo"

    print("Columns filled successfully.")

    df.to_excel(EXCEL_FILE, index=False)
    
    try:
        from apply_jra_style import apply_styling
        apply_styling(EXCEL_FILE)
        print("Styling applied successfully.")
    except Exception as e:
        print(f"Error applying style: {e}")

    print("Opening Excel file...")
    import subprocess
    subprocess.Popen(["start", EXCEL_FILE], shell=True)
    print("All done!")

if __name__ == "__main__":
    fill_ghliterary()
