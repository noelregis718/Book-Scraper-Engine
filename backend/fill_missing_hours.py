import pandas as pd

EXCEL_FILE = r"e:\Internship\PocketFM\book_details_from_email_rechecked_filled.xlsx"

def fill_missing_hours():
    print(f"Loading {EXCEL_FILE}...")
    try:
        df = pd.read_excel(EXCEL_FILE)
    except Exception as e:
        print(f"Failed to load Excel file: {e}")
        return

    updates = 0
    for index, row in df.iterrows():
        pages = row.get("Total_Page_Count_of_Primary_Books")
        hours = row.get("Approx Length (Hrs)")
        
        # If we have a valid page count
        if pd.notna(pages) and str(pages).strip() != '' and float(pages) > 0:
            # If hours is missing or NaN
            if pd.isna(hours) or str(hours).strip() == '':
                # Calculate hours: (pages * 250) / 10000
                calculated_hours = round((float(pages) * 250) / 10000, 1)
                df.at[index, "Approx Length (Hrs)"] = calculated_hours
                updates += 1
                
                # Optional: Print what we fixed so the user sees it working
                book_name = row.get("Book Name", row.get("Series Name", "Unknown Book"))
                print(f"Row {index + 2}: Fixed '{book_name}' -> {pages} pages = {calculated_hours} hours")

    if updates > 0:
        print(f"\nFound and fixed {updates} missing hour calculations. Saving to Excel...")
        try:
            df.to_excel(EXCEL_FILE, index=False)
            print("Save complete!")
            
            # Apply styling after save to make sure it looks nice
            import format_excel
            format_excel.apply_styling(EXCEL_FILE)
        except Exception as e:
            print(f"Failed to save to Excel: {e}")
    else:
        print("No missing hour calculations found.")

if __name__ == "__main__":
    fill_missing_hours()
