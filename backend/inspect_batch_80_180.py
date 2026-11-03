import openpyxl

wb = openpyxl.load_workbook(r"E:\Internship\PocketFM\Kensington_Storefront_Fantasy_Catalog.xlsx", data_only=True)
ws = wb.active

print(f"Total Rows in Excel: {ws.max_row}\n")

batch_enriched = 0
batch_blank = 0

print("--- Sample Enriched Books from Batch (Rows 82 to 181) ---")
samples_shown = 0
for r in range(82, 182):
    t = ws.cell(row=r, column=1).value
    a = ws.cell(row=r, column=2).value
    gr_url = ws.cell(row=r, column=8).value
    rating = ws.cell(row=r, column=9).value
    rcount = ws.cell(row=r, column=10).value
    books = ws.cell(row=r, column=11).value
    pages = ws.cell(row=r, column=12).value
    hrs = ws.cell(row=r, column=13).value
    checker = ws.cell(row=r, column=16).value
    
    if gr_url and str(gr_url).startswith("http"):
        batch_enriched += 1
        if samples_shown < 10:
            print(f"[Row {r}] '{t}' by {a}")
            print(f"   URL: {gr_url}")
            print(f"   Rating: {rating} ({rcount} ratings) | {books} bks | {pages} pgs ({hrs} hrs) | {checker}")
            samples_shown += 1
    else:
        batch_blank += 1

print(f"\nBatch 80-180 (100 Books) Summary:")
print(f"  Successfully Enriched: {batch_enriched} / 100")
print(f"  Unmatched / Blank for Retry: {batch_blank} / 100")

# Overall progress
total_in_cat = ws.max_row - 1
total_with_gr = 0
for r in range(2, ws.max_row + 1):
    val = ws.cell(row=r, column=8).value
    if val and str(val).startswith("http"):
        total_with_gr += 1

print(f"\nOverall Catalog Status:")
print(f"  Total Books in File: {total_in_cat}")
print(f"  Total Enriched So Far: {total_with_gr} / 180 (Processed)")
print(f"  Remaining Books in Catalog: {total_in_cat - 180}")

wb.close()

