import pandas as pd

def main():
    filepath = r"E:\Internship\PocketFM\Maass_Agency_Complete_List_With_Image_Books.xlsx"
    df = pd.read_excel(filepath)
    
    # Update Publisher
    if "Publisher" in df.columns:
        df["Publisher"] = "Maass Agency"
        
    # Update Name of agent
    if "Name of agent" in df.columns:
        df["Name of agent"] = "Donald Maass"
        
    df.to_excel(filepath, index=False)
    print("Updated Publisher and Name of agent successfully.")

if __name__ == "__main__":
    main()
