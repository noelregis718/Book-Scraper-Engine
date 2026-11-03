import openpyxl
import re

agency_file = r"E:\Internship\PocketFM\Kensington Agency.xlsx"
storefront_file = r"E:\Internship\PocketFM\Kensington_Storefront_Fantasy_Catalog.xlsx"

def normalize_title(t):
    if not t: return ""
    t = str(t).strip().lower()
    t = t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    t = re.sub(r'[:\-—\(].*$', '', t)
    t = re.sub(r'[^\w\s]', '', t)
    for art in ['the ', 'a ', 'an ']:
        if t.startswith(art):
            t = t[len(art):]
            break
    return re.sub(r'\s+', ' ', t).strip()

def clean_author(a):
    if not a: return set()
    a = str(a).lower()
    a = re.sub(r'[^\w\s]', '', a)
    return set(part for part in a.split() if len(part) > 2)

wb_ag = openpyxl.load_workbook(agency_file, read_only=True)
ws_ag = wb_ag[wb_ag.sheetnames[0]]
agency_data = {}
for row in ws_ag.iter_rows(min_row=2, values_only=True):
    if row and row[0]:
        t = str(row[0]).strip()
        a = str(row[1] or "").strip()
        norm_t = normalize_title(t)
        if norm_t:
            if norm_t not in agency_data:
                agency_data[norm_t] = []
            agency_data[norm_t].append((t, a))
wb_ag.close()

wb_sf = openpyxl.load_workbook(storefront_file, data_only=True)
ws_sf = wb_sf.active
sf_rows = []
for r in range(2, ws_sf.max_row + 1):
    vals = [ws_sf.cell(row=r, column=c).value for c in range(1, 8)]
    if vals[0]:
        sf_rows.append(vals)
wb_sf.close()

author_mismatches = []
confirmed_overlaps = []

for r in sf_rows:
    t = str(r[0]).strip()
    a = str(r[1] or "").strip()
    norm = normalize_title(t)
    
    if norm in agency_data:
        ag_list = agency_data[norm]
        sf_auth_tokens = clean_author(a)
        
        author_matched = False
        for ag_t, ag_a in ag_list:
            ag_auth_tokens = clean_author(ag_a)
            if sf_auth_tokens & ag_auth_tokens:
                author_matched = True
                confirmed_overlaps.append((r, ag_t, ag_a))
                break
        if not author_matched:
            author_mismatches.append((r, ag_list))

print(f"Total overlapping titles with confirmed author match: {len(confirmed_overlaps)}")
print(f"Titles matching but different author: {len(author_mismatches)}")

if author_mismatches:
    print("\nTitles where author differed:")
    for sf_item, ag_list in author_mismatches:
        print(f"  Storefront: '{sf_item[0]}' by '{sf_item[1]}' vs Agency: {ag_list}")
