import pandas as pd
import openpyxl

file1 = r"E:\Internship\PocketFM\Romantasy New Keywords Scraping.xlsx"
file2 = r"E:\Internship\PocketFM\All-Genre Licensing Tracker.xlsx"

def extract_visible_data(wb, sheet_name):
    ws = wb[sheet_name]
    data = []
    headers = []
    
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        # Check if row is hidden by an Excel filter
        row_dim = ws.row_dimensions.get(i + 1)
        if row_dim is not None and row_dim.hidden:
            continue
            
        if not headers:
            # Check if this row looks like a real header row
            row_values = [str(c).strip().lower() for c in row if c is not None]
            if 'title' in row_values or 'book title' in row_values or 'series name' in row_values:
                headers = [cell for cell in row]
            else:
                continue # Skip this row, it's not the headers (e.g. Row 1 of Romantasy v2)
        else:
            # Create dict matching headers
            row_data = {}
            has_data = False
            for j, cell in enumerate(row):
                if j < len(headers):
                    header = headers[j]
                    if header is not None and str(header).strip() != '':
                        # Standardize common column names for better merging
                        header_str = str(header).strip()
                        if header_str == 'Title': header_str = 'Book Title'
                        if header_str == 'GR Series Link': header_str = 'GoodReads_Series_URL'
                        
                        row_data[header_str] = cell
                        if cell is not None and str(cell).strip() != '':
                            has_data = True
            if has_data:
                data.append(row_data)
                
    return pd.DataFrame(data)

def main():
    print(f"Loading {file1} with data_only=True to evaluate formulas...")
    wb1 = openpyxl.load_workbook(file1, data_only=True)

    print("Extracting from 'Series only - Priority Keywords'...")
    try:
        df1 = extract_visible_data(wb1, 'Series only - Priority Keywords')
        print(f"  -> Extracted {len(df1)} visible rows.")
    except Exception as e:
        print(f"  -> Error extracting tab: {e}")
        df1 = pd.DataFrame()

    print("Extracting from 'Cut 1 Unique Series of 12.3k Ti'...")
    try:
        df2 = extract_visible_data(wb1, 'Cut 1 Unique Series of 12.3k Ti')
        print(f"  -> Extracted {len(df2)} visible rows.")
    except Exception as e:
        print(f"  -> Error extracting tab: {e}")
        df2 = pd.DataFrame()

    print(f"\nLoading {file2} with data_only=True to evaluate formulas...")
    wb2 = openpyxl.load_workbook(file2, data_only=True)

    print("Extracting from 'Romantasy v2'...")
    try:
        df3 = extract_visible_data(wb2, 'Romantasy v2')
        print(f"  -> Extracted {len(df3)} visible rows.")
    except Exception as e:
        print(f"  -> Error extracting tab: {e}")
        df3 = pd.DataFrame()

    print("\nMerging extracted sheets vertically...")
    dfs_to_merge = []
    if not df1.empty: dfs_to_merge.append(df1)
    if not df2.empty: dfs_to_merge.append(df2)
    if not df3.empty: dfs_to_merge.append(df3)
    
    if len(dfs_to_merge) > 0:
        merged_df = pd.concat(dfs_to_merge, ignore_index=True)
        out_file = r"E:\Internship\PocketFM\Merged_Romantasy_Master.xlsx"
        merged_df.to_excel(out_file, index=False)
        print(f"\nMerge complete! Final dataset saved to {out_file} with {len(merged_df)} total rows.")
    else:
        print("\nNo data was extracted from any tabs.")

if __name__ == "__main__":
    main()
