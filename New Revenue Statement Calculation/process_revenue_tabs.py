import pandas as pd
import os
import re

file_path = 'e:/Internship/PocketFM/JAS Self-Pub Revenue Payouts (1).xlsx'
template_path = 'e:/Internship/PocketFM/docs/revenue_statement.html'
output_dir = 'e:/Internship/PocketFM/New Revenue Statement Calculation/Statements'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

with open(template_path, 'r', encoding='utf-8') as f:
    template_html = f.read()

xl = pd.ExcelFile(file_path)
# Skip the first 4 summary/master tabs
target_sheets = xl.sheet_names[4:]

for sheet in target_sheets:
    try:
        df = pd.read_excel(file_path, sheet_name=sheet, header=None)
        
        # Find the row and col where "Total Plays" exists
        box_row, box_col = -1, -1
        for col_idx in df.columns:
            matches = df[df[col_idx] == 'Total Plays'].index
            if len(matches) > 0:
                box_row = matches[0]
                box_col = col_idx
                break
                
        if box_row == -1:
            print(f"Skipping {sheet}: No 'Total Plays' found in any column.")
            continue
            
        box_start_idx = box_row - 2 # This should be the Title row
        val_col = box_col + 1
        
        title_full = str(df.iloc[box_start_idx, box_col]).strip()
        period = str(df.iloc[box_start_idx + 1, val_col]).strip()
        
        # Now iterate through the box to extract all variables
        data = {}
        for idx in range(box_start_idx + 2, len(df)):
            key = str(df.iloc[idx, box_col]).strip()
            val = df.iloc[idx, val_col]
            if pd.notna(key) and key != 'nan':
                data[key] = val

        # Extract values (using defaults if missing)
        total_plays = data.get('Total Plays', 0)
        total_listeners = data.get('Total Listeners', 0)
        
        # Deal type check
        is_net = any('Net' in k for k in data.keys())
        
        if is_net:
            rev_gen_key = next((k for k in data.keys() if 'Net Revenue' in k or 'Revenue Generated' in k), 'Revenue Generated $')
            rev_share_key = next((k for k in data.keys() if 'Revenue Share' in k), 'Revenue Share $')
        else:
            rev_gen_key = next((k for k in data.keys() if 'Revenue Generated (Gross)' in k or 'Revenue Generated' in k), 'Revenue Generated $')
            rev_share_key = next((k for k in data.keys() if 'Revenue Share' in k), 'Revenue Share $')
            
        rev_generated = data.get(rev_gen_key, 0)
        rev_share_amount = data.get(rev_share_key, 0)
        mg_paid = data.get('MG Paid $', 0)
        mg_recouped = data.get('MG to be recouped $', 0)
        final_payout = data.get('Final Payout $', 0)
        
        # Clean up title for filename
        safe_title = re.sub(r'[^a-zA-Z0-9_\-]', '_', sheet)
        
        # HTML replacement
        show_html = template_html
        show_html = re.sub(r'\[REPORTING_PERIOD\]', period, show_html)
        
        # Extract author from title if "by" exists
        if " by " in title_full:
            show_name, author_full = title_full.split(" by ", 1)
            author_first = author_full.split()[0]
        else:
            show_name = title_full
            author_full = ""
            author_first = ""
            
        show_html = re.sub(r'\[AUTHOR_FIRST_NAME\]', author_first, show_html)
        show_html = re.sub(r'\[SHOW_NAME\]', show_name, show_html)
        show_html = re.sub(r'\[AUTHOR_NAME\]', author_full, show_html)
        show_html = re.sub(r'26,647', f"{float(total_plays):,.0f}", show_html)
        show_html = re.sub(r'5,993', f"{float(total_listeners):,.0f}", show_html)
        
        # Remove the word 'quarterly' from the intro text as requested
        show_html = re.sub(r'quarterly revenue statement', 'revenue statement', show_html, flags=re.IGNORECASE)
        
        # Construct table
        tbody_content = f"""
                        <tr>
                            <td style="text-align: left; font-weight: 700; padding: 10px;">{rev_gen_key}</td>
                            <td style="text-align: right; padding: 10px;">{float(rev_generated):,.2f}</td>
                        </tr>
                        <tr>
                            <td style="text-align: left; padding: 10px;">{rev_share_key}</td>
                            <td style="text-align: right; padding: 10px;">{float(rev_share_amount):,.2f}</td>
                        </tr>
                        <tr>
                            <td style="color:transparent; padding: 10px;">-</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td style="text-align: left; padding: 10px;">MG Paid $</td>
                            <td style="text-align: right; padding: 10px;">{float(mg_paid):,.2f}</td>
                        </tr>
                        <tr>
                            <td style="text-align: left; padding: 10px;">MG to be recouped $</td>
                            <td style="text-align: right; padding: 10px;">{float(mg_recouped):,.2f}</td>
                        </tr>
                        <tr style="background-color: #bfbfbf; font-weight: 700;">
                            <td style="text-align: left; font-size: 15px; padding: 10px;">Final Payout $</td>
                            <td style="text-align: right; font-size: 15px; padding: 10px;">{float(final_payout):,.2f}</td>
                        </tr>
        """
        
        show_html = re.sub(r'<tbody>.*?</tbody>', f'<tbody>\n{tbody_content}\n</tbody>', show_html, flags=re.DOTALL)
        
        out_path = os.path.join(output_dir, f"Revenue_Statement_{safe_title}.html")
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(show_html)
            
        print(f"Generated: {out_path}")
        
    except Exception as e:
        print(f"Error processing sheet {sheet}: {e}")
