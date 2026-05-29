import pandas as pd
import os

def update_publisher_and_agent(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"Loading: {file_path}")
    df = pd.read_excel(file_path)

    # Update columns
    df['Publisher'] = 'K T Literary'
    df['Name of agent'] = 'Kate Testerman'

    print("Updating 'Publisher' to 'K T Literary' and 'Name of agent' to 'Kate Testerman'...")

    # Save the updated dataframe
    df.to_excel(file_path, index=False)
    print("Saved to excel.")

    # Reapply JRA styling
    try:
        from apply_jra_style import apply_styling
        apply_styling(file_path)
        print("Styling reapplied.")
    except Exception as e:
        print(f"Error applying style: {e}")

if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base, "KT_Literary_Merged_Formatted.xlsx")
    update_publisher_and_agent(file_path)
