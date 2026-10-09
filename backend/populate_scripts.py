import os
import re
import pandas as pd

# Folders to check
folders = [
    'e:/Internship/PocketFM/Goodnovel_6th_August_2025_data-20261008T113428Z-1-001',
    'e:/Internship/PocketFM/Goodnovel_28May_data_drive-20261008T113437Z-1-001',
    'e:/Internship/PocketFM/Joyread_Data_9June_2025_with_file_name-20261008T113448Z-1-001'
]

script_names = set()

# Iterate through folders and extract names
for folder in folders:
    if os.path.exists(folder):
        for root, dirs, files in os.walk(folder):
            for file in files:
                # Remove extension to get the clean name
                name = os.path.splitext(file)[0]
                
                # Remove all numerical digits completely (e.g. '6876' or trailing '_31000731965')
                name = re.sub(r'\d+', '', name)
                
                # Replace dashes and remaining underscores with spaces
                name = name.replace('-', ' ').replace('_', ' ')
                
                # Convert the entire name to lowercase as requested
                name = name.lower()
                
                # Strip out 'joyread' and 'goodnovel' entirely from any part of the string
                name = name.replace('joyread', '').replace('goodnovel', '')
                
                # Collapse any double/triple spaces into a single space and strip outer spaces
                name = re.sub(r'\s+', ' ', name).strip()
                
                # Only add if there's an actual name left
                if name:
                    script_names.add(name)

print(f"Found {len(script_names)} unique scripts across the 3 folders.")

# Load the existing empty metrics sheet
metrics_file = 'e:/Internship/PocketFM/GenAI_Metrics.xlsx'
print("Loading GenAI_Metrics.xlsx...")
metrics_df = pd.read_excel(metrics_file)

# We want to insert these names into the 'Show / Title' column
# Since the sheet is empty, we can just create a new dataframe with these names and the existing columns
# or concatenate.
new_data = pd.DataFrame({'Show / Title': list(script_names)})

# Merge with the empty metrics_df to keep the column structure
final_df = pd.concat([metrics_df, new_data], ignore_index=True)

# Reorder columns to match original
final_df = final_df[metrics_df.columns]

# Save with formatting
with pd.ExcelWriter(metrics_file, engine='xlsxwriter') as writer:
    final_df.to_excel(writer, index=False, sheet_name='Metrics')
    
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
    for col_num, value in enumerate(final_df.columns.values):
        worksheet.write(0, col_num, value, header_format)
        
    # Auto-adjust column widths
    worksheet.set_column('A:A', 35)  # Show / Title
    worksheet.set_column('B:L', 20)  # Metric columns
    
    # Freeze the top row
    worksheet.freeze_panes(1, 0)

print("Successfully populated GenAI_Metrics.xlsx with script names!")
