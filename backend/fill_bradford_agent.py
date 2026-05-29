import pandas as pd
import os
import sys

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
excel_file = os.path.join(base_path, "Bradford_Solstice_Merged_Formatted.xlsx")

def update_agent():
    if not os.path.exists(excel_file):
        print(f"File not found: {excel_file}")
        return
        
    print(f"Loading {excel_file}...")
    df = pd.read_excel(excel_file)
    
    count = 0
    for idx, row in df.iterrows():
        current_pub = str(row.get('Publisher', '')).strip()
        if current_pub != 'Solstice Romance':
            df.at[idx, 'Name of agent'] = 'Laura Bradford'
            count += 1
            
    print(f"Updated {count} rows to agent 'Laura Bradford'.")
    
    df.to_excel(excel_file, index=False)
    print("Saved to excel.")
    
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from apply_jra_style import apply_styling
        apply_styling(excel_file)
        print("Styling applied.")
    except Exception as e:
        print(f"Styling error: {e}")

if __name__ == '__main__':
    update_agent()
