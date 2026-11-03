import openpyxl
import re

agency_file = r"E:\Internship\PocketFM\Kensington Agency.xlsx"
storefront_file = r"E:\Internship\PocketFM\Kensington_Storefront_Fantasy_Catalog.xlsx"

print(f"Loading {agency_file}...")
wb_agency = openpyxl.load_workbook(agency_file, read_only=True)
ws_agency = wb_agency[wb_agency.sheetnames[0]]

print(f"Agency Sheet Name: {ws_agency.title}")
agency_headers = [c for c in next(ws_agency.iter_rows(max_row=1, values_only=True))]
print(f"Agency Headers: {agency_headers}")

def normalize_title(t):
    if not t: return ""
    t = str(t).strip().lower()
    t = t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    # Strip subtitles like ": Deluxe Limited Edition", ": A Novel", etc.
    t = re.sub(r'[:\-—\(].*$', '', t)
    t = re.sub(r'[^\w\s]', '', t)
    for art in ['the ', 'a ', 'an ']:
        if t.startswith(art):
            t = t[len(art):]
            break
    return re.sub(r'\s+', ' ', t).strip()

agency_titles = set()
agency_raw_titles = {}
for r_idx, row in enumerate(ws_agency.iter_rows(min_row=2, values_only=True), start=2):
    if row and row[0]:
        raw_t = str(row[0]).strip()
        norm = normalize_title(raw_t)
        if norm:
            agency_titles.add(norm)
            if norm not in agency_raw_titles:
                agency_raw_titles[norm] = raw_t

wb_agency.close()
print(f"Total Unique Normalized Titles in Agency: {len(agency_titles)}")

print(f"\nLoading {storefront_file}...")
wb_sf = openpyxl.load_workbook(storefront_file, data_only=True)
ws_sf = wb_sf.active

sf_headers = [cell.value for cell in ws_sf[1]]
print(f"Storefront Headers: {sf_headers}")

sf_rows = []
for r in range(2, ws_sf.max_row + 1):
    vals = [ws_sf.cell(row=r, column=c).value for c in range(1, len(sf_headers) + 1)]
    if vals[0]:
        sf_rows.append(vals)

wb_sf.close()
print(f"Total Books in Storefront Catalog: {len(sf_rows)}")

# Find overlaps
overlap_books = []
unique_sf_books = []

for row_vals in sf_rows:
    t = str(row_vals[0]).strip()
    norm = normalize_title(t)
    
    if norm in agency_titles:
        overlap_books.append((row_vals, agency_raw_titles[norm]))
    else:
        unique_sf_books.append(row_vals)

print(f"\n--- Comparison Results ---")
print(f"Total Storefront Books Evaluated: {len(sf_rows)}")
print(f"Overlapping / Common Titles Found: {len(overlap_books)}")
print(f"Unique Storefront Titles Remaining: {len(unique_sf_books)}")

print(f"\nSample Overlapping Titles (Removed):")
for item, ag_t in overlap_books[:10]:
    print(f"  - Storefront: '{item[0]}' by {item[1]} == Agency: '{ag_t}'")

print(f"\nSample Unique Titles Remaining:")
for item in unique_sf_books[:10]:
    print(f"  + Storefront: '{item[0]}' by {item[1]} [{item[3]}]")

