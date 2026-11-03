import openpyxl

wb = openpyxl.load_workbook(r"E:\Internship\PocketFM\Kensington_Unique_Fantasy_Fiction_Catalog.xlsx", data_only=True)
ws = wb.active

for r in range(2, 7):
    row_vals = [ws.cell(row=r, column=c).value for c in range(1, 12)]
    print(f"\n--- Row {r}: {row_vals[0]} by {row_vals[1]} ---")
    print(f"  Series/Book URL: {row_vals[3]}")
    print(f"  Primary Books:   {row_vals[4]}")
    print(f"  Rating (out/5):  {row_vals[5]}")
    print(f"  Ratings Count:   {row_vals[6]}")
    print(f"  Synopsis (50ch): {str(row_vals[7])[:60]}...")
    print(f"  Romantasy (Y/N): {row_vals[8]}")
    print(f"  Subgenre:        {row_vals[9]}")
wb.close()

