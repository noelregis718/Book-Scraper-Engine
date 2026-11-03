import openpyxl

for fname in ["Kensington Agency.xlsx", "Kensington Old List.xlsx", "Kensington_Fantasy_Fiction_Catalog.xlsx"]:
    print(f"\n==========================================")
    print(f"File: {fname}")
    wb = openpyxl.load_workbook(fname, read_only=True)
    print(f"Sheets: {wb.sheetnames}")
    ws = wb[wb.sheetnames[0]]
    first_rows = []
    for idx, row in enumerate(ws.iter_rows(values_only=True)):
        first_rows.append(row)
        if idx >= 4:
            break
    if first_rows:
        print("Header Row:", first_rows[0][:15])
        print("Sample Row 1:", first_rows[1][:15] if len(first_rows) > 1 else "None")
    wb.close()

