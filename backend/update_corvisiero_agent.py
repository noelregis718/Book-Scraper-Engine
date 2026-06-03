import pandas as pd
import os

EXCEL_FILE = r"E:\Internship\PocketFM\corvisiero_merged.xlsx"

def update_publisher_and_agent():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found!")
        return

    print(f"Loading {EXCEL_FILE}...")
    df = pd.read_excel(EXCEL_FILE)
    
    df['Publisher'] = "Corvisiero Agency"
    df['Name of agent'] = "Maggie Sadler"
    
    print(f"Saving {EXCEL_FILE} with updated Publisher and Agent...")
    df.to_excel(EXCEL_FILE, index=False)
    print("Done!")

if __name__ == '__main__':
    update_publisher_and_agent()
