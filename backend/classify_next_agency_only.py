import pandas as pd
import os
import sys

# Import our AI classifier
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ai_classifier import identify_subgenre
from apply_jra_style import apply_styling

def run_classifier():
    target_excel = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Next_Agency.xlsx")
    
    print(f"Loading Excel file: {target_excel}")
    if not os.path.exists(target_excel):
        print("Excel file not found!")
        return

    df = pd.read_excel(target_excel)
    
    updates = 0
    for index, row in df.iterrows():
        # Get existing synopsis or title as text context
        synopsis = str(row.get("Synopsis (if available)", "")).strip()
        title = str(row.get("Name of Series", "")).strip()
        
        # Avoid passing literal "nan"
        if synopsis.lower() == 'nan': synopsis = ""
        if title.lower() == 'nan': title = ""
            
        # We don't have separate genre columns saved in this sheet, so we use the title as tags if needed
        # Or just pass the title into the synopsis body for the classifier
        full_text = f"{title} {synopsis}".strip()
        
        if not full_text:
            continue
            
        # Pass to the AI taxonomy classifier
        detected_subgenre = identify_subgenre(full_text, [])
        
        # Update the row
        if detected_subgenre != "N/A":
            df.at[index, "Romantasy = Yes or No?"] = "Yes"
            df.at[index, "Romantasy Sub-Genre of series"] = detected_subgenre
            print(f"[{index}] Classified '{title}' as -> {detected_subgenre}")
            updates += 1
        else:
            # Leave existing or default to No if not already classified
            current_romantasy = str(df.at[index, "Romantasy = Yes or No?"])
            if current_romantasy.lower() == "nan" or current_romantasy == "":
                df.at[index, "Romantasy = Yes or No?"] = "No"

    print(f"\nClassification complete. {updates} books were successfully identified as Romantasy based on their Synopsis!")
    
    # Save and style
    df.to_excel(target_excel, index=False)
    try:
        apply_styling(target_excel)
        print("Styling applied successfully.")
    except Exception as e:
        print(f"Styling error: {e}")

if __name__ == "__main__":
    run_classifier()
