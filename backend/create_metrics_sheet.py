import pandas as pd

print("Loading Vikrant sheet LC data tab...")
# Load the specific tab from the Vikrant sheet
file_path = 'e:/Internship/PocketFM/Vikrant Sheet.xlsx'
df = pd.read_excel(file_path, sheet_name='LC data - 7.10.26')

# Define the exact columns we want to extract
# Show Name (Column C in Excel, named 'Show / Title')
# Columns R to AB (Indices 17 to 27 inclusive)
# Let's dynamically get them by index to be perfectly safe, or by name since we know them
title_col = ['Show / Title']
metric_cols = df.columns[17:28].tolist()  # Col R (17) to Col AB (27)

all_cols = title_col + metric_cols
print(f"Extracting columns: {all_cols}")

# Create the subset dataframe
metrics_df = df[all_cols].copy()

# Drop rows where 'Show / Title' is missing just to keep it clean
metrics_df = metrics_df.dropna(subset=['Show / Title'])

# Output file path
output_file = 'e:/Internship/PocketFM/GenAI_Metrics.xlsx'

# Drop all rows so the sheet is completely empty except for headers
metrics_df = metrics_df.head(0)

# Save and format beautifully with xlsxwriter
print("Saving formatted sheet...")
with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
    metrics_df.to_excel(writer, index=False, sheet_name='Metrics')
    
    workbook = writer.book
    worksheet = writer.sheets['Metrics']
    
    # Premium Header Format
    header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'center',
        'fg_color': '#D7E4BC',
        'border': 1
    })
    
    # Write headers
    for col_num, value in enumerate(metrics_df.columns.values):
        worksheet.write(0, col_num, value, header_format)
        
    # Auto-adjust column widths
    worksheet.set_column('A:A', 35)  # Show / Title
    worksheet.set_column('B:L', 20)  # Metric columns
    
    # Freeze the top row
    worksheet.freeze_panes(1, 0)

print(f"SUCCESS! Created highly formatted metrics sheet at {output_file}")
