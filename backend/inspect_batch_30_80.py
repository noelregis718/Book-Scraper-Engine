import openpyxl

wb = openpyxl.load_workbook(r"E:\Internship\PocketFM\Kensington_Storefront_Fantasy_Catalog.xlsx", data_only=True)
ws = wb.active

print(f"Total Rows in Excel: {ws.max_row}\n")

enriched_count = 0
not_found_count = 0

print("--- Sample Enriched Rows from Batch 30 to 80 ---")
for r in range(32, 82):
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
        enriched_count += 1
        if enriched_count <= 8 or enriched_count in [15, 25, 35]:
            print(f"[Row {r}] '{t}' by {a}")
            print(f"   URL: {gr_url}")
            print(f"   Rating: {rating} ({rcount} ratings) | {books} bks | {pages} pgs ({hrs} hrs) | {checker}")
    else:
        not_found_count += 1

print(f"\nBatch 30-80 Summary:")
print(f"  Enriched with Goodreads Data: {enriched_count} / 50")
print(f"  Not Found on Goodreads (Blank for retry): {not_found_count} / 50")

# Total catalog overall status
total_in_cat = ws.max_row - 1
total_with_gr = 0
for r in range(2, ws.max_row + 1):
    val = ws.cell(row=r, column=8).value
    if val and str(val).startswith("http"):
        total_with_gr += 1

print(f"\nOverall Catalog Status:")
print(f"  Total Books in File: {total_in_cat}")
print(f"  Total Successfully Enriched So Far: {total_with_gr}")

wb.close()

