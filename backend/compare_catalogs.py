import openpyxl
import re

def normalize_title(t):
    if not t:
        return ""
    t = str(t).strip().lower()
    # Strip leading/trailing quotes and punctuation
    t = re.sub(r'^[\'"“‘\s]+|[\'"”’\s]+$', '', t)
    # Normalize multiple whitespace
    t = re.sub(r'\s+', ' ', t)
    return t

def analyze_catalogs():
    # 1. Load Kensington Agency
    wb_agency = openpyxl.load_workbook("Kensington Agency.xlsx", read_only=True)
    ws_agency = wb_agency[wb_agency.sheetnames[0]]
    agency_titles = set()
    agency_rows = 0
    for row in ws_agency.iter_rows(min_row=2, values_only=True):
        if row and row[0]:
            agency_rows += 1
            norm = normalize_title(row[0])
            if norm:
                agency_titles.add(norm)
    wb_agency.close()

    # 2. Load Kensington Old List
    wb_old = openpyxl.load_workbook("Kensington Old List.xlsx", read_only=True)
    ws_old = wb_old[wb_old.sheetnames[0]]
    old_titles = set()
    old_rows = 0
    for row in ws_old.iter_rows(min_row=2, values_only=True):
        if row and row[0]:
            old_rows += 1
            norm = normalize_title(row[0])
            if norm:
                old_titles.add(norm)
    wb_old.close()

    # Union of all existing titles from both old sheets
    combined_existing = agency_titles | old_titles

    print(f"Kensington Agency.xlsx rows: {agency_rows} (Unique normalized titles: {len(agency_titles)})")
    print(f"Kensington Old List.xlsx rows: {old_rows} (Unique normalized titles: {len(old_titles)})")
    print(f"Combined unique titles across Agency & Old List: {len(combined_existing)}")

    # 3. Load New Kensington Fantasy Fiction Catalog
    wb_new = openpyxl.load_workbook("Kensington_Fantasy_Fiction_Catalog.xlsx", data_only=True)
    ws_new = wb_new[wb_new.sheetnames[0]]
    
    new_rows_total = 0
    internal_duplicates = {} # title -> list of row numbers
    matched_in_agency = []
    matched_in_old = []
    matched_in_either = []
    unique_new_rows = []

    seen_in_new = {}

    for r_idx, row in enumerate(ws_new.iter_rows(min_row=2, values_only=True), start=2):
        if not row or not row[0]:
            continue
        new_rows_total += 1
        raw_title = str(row[0]).strip()
        norm_title = normalize_title(raw_title)

        # Check internal duplicate within new catalog
        if norm_title in seen_in_new:
            seen_in_new[norm_title].append(r_idx)
            internal_duplicates[norm_title] = seen_in_new[norm_title]
        else:
            seen_in_new[norm_title] = [r_idx]

        in_agency = norm_title in agency_titles
        in_old = norm_title in old_titles
        in_either = in_agency or in_old

        if in_agency:
            matched_in_agency.append((r_idx, raw_title, str(row[1])))
        if in_old:
            matched_in_old.append((r_idx, raw_title, str(row[1])))
        if in_either:
            matched_in_either.append((r_idx, raw_title, str(row[1])))
        else:
            unique_new_rows.append((r_idx, row))

    wb_new.close()

    print(f"\n=======================================================")
    print(f"NEW CATALOG ANALYSIS (Kensington_Fantasy_Fiction_Catalog.xlsx)")
    print(f"=======================================================")
    print(f"Total rows in new catalog: {new_rows_total}")
    print(f"Internal duplicate titles in new catalog: {len(internal_duplicates)}")
    for t, rows in list(internal_duplicates.items())[:10]:
        print(f"   Duplicate '{t}' at rows {rows}")

    print(f"\n--- Overlap with Old Lists ---")
    print(f"Titles found in Kensington Agency.xlsx:     {len(matched_in_agency)}")
    print(f"Titles found in Kensington Old List.xlsx:   {len(matched_in_old)}")
    print(f"Titles found in EITHER old sheet (Doubles): {len(matched_in_either)}")
    print(f"BRAND NEW UNIQUE TITLES (Not in either):   {len(unique_new_rows)}")

    print(f"\nSample of Double Titles (already in old sheets):")
    for r_idx, t, a in matched_in_either[:15]:
        print(f"  Row {r_idx}: '{t}' by {a}")

    print(f"\nSample of Brand New Unique Titles:")
    for r_idx, row in unique_new_rows[:15]:
        print(f"  Row {r_idx}: '{row[0]}' by {row[1]}")

if __name__ == "__main__":
    analyze_catalogs()

