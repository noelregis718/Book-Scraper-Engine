import openpyxl

filepath = "e:/Internship/PocketFM/JAS Self-Pub Revenue Payouts (1).xlsx"
wb = openpyxl.load_workbook(filepath, data_only=False)
sheet = wb['Calculations formats (reference']

print("--- Formulas in row 3 (which corresponds to index 2 in pandas) ---")
headers = [cell.value for cell in sheet[2]]
for i, cell in enumerate(sheet[3]):
    if i < len(headers):
        print(f"{headers[i]}: {cell.value}")
