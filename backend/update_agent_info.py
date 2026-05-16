import pandas as pd
import os

MASTER_FILE = "Deep_Catalog_Enrichment.xlsx"

def update_agent_info():
    if not os.path.exists(MASTER_FILE):
        print(f"Error: {MASTER_FILE} not found.")
        return

    print(f"Loading {MASTER_FILE}...")
    df = pd.read_excel(MASTER_FILE)

    print("Updating Publisher and Agent columns...")
    
    # Update 'Publisher' where it is 'N/A' or empty
    df['Publisher'] = df['Publisher'].fillna('N/A')
    df.loc[df['Publisher'] == 'N/A', 'Publisher'] = '1852 Literary'
    
    # Update 'Name of agent' where it is 'N/A' or empty
    df['Name of agent'] = df['Name of agent'].fillna('N/A')
    df.loc[df['Name of agent'] == 'N/A', 'Name of agent'] = 'Heather Roberts'

    print(f"Saving changes to {MASTER_FILE}...")
    df.to_excel(MASTER_FILE, index=False)
    print("Done! All Publisher and Agent columns have been updated.")

if __name__ == "__main__":
    update_agent_info()
