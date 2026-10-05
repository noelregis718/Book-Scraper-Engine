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

# Load US Lifecycle Deals
lifecycle_df = pd.read_excel(file_path, sheet_name='US Lifecycle Deals', header=2) # Row 2 is header

# Load JAS Sheet
jas_df = pd.read_excel(file_path, sheet_name='Oct 1, 2026')

target_series = [
    "Vital Secrets",
    "Mrs. Lillywhite Investigates Mysteries",
    "Liz Talbot Mystery Series",
    "Carolina Tales",
    "Detective Emilia Cruz",
    "Fatal Series",
    "Gansett Series",
    "Fate Weaver Series",
    "The Witches of Wheeler Park"
]

generated_files = []

for index, row in lifecycle_df.iterrows():
    title = str(row.get('Title / IP', '')).strip()
    
    # Check if this title is in our target list (partial match for safety)
    is_target = False
    for t in target_series:
        if t.lower() in title.lower():
            is_target = True
            break
            
    if not is_target:
        continue
        
    show_id = str(row.get('Show ID (after show creation)', '')).strip()
    if not show_id or show_id == 'nan':
        print(f"Skipping {title}: No Show ID in US Lifecycle Deals.")
        continue
        
    author_full = str(row.get('Author Name', '')).strip()
    author_first = author_full.split()[0] if author_full else ""
    deal_type = str(row.get('Gross / Net Deal', '')).strip()
    mg_paid = row.get('MG Paid', 0)
    rev_share_pct_raw = str(row.get('Rev share %', '')).strip()
    
    # Find in JAS Sheet
    jas_rows = jas_df[jas_df['Show Id'] == show_id]
    
    if len(jas_rows) == 0:
        print(f"Skipping {title}: Show ID {show_id} not found in JAS Sheet.")
        continue
        
    # Get the most recent quarter for this show
    jas_row = jas_rows.sort_values(by='Quarterly', ascending=False).iloc[0]
    
    quarter_date = pd.to_datetime(jas_row['Quarterly'])
    
    # "1st October means from july-august-September , and 1st July means april-may-June"
    if quarter_date.month == 10:
        period = f"July-August-September {quarter_date.year}"
    elif quarter_date.month == 7:
        period = f"April-May-June {quarter_date.year}"
    elif quarter_date.month == 4:
        period = f"January-February-March {quarter_date.year}"
    elif quarter_date.month == 1:
        period = f"October-November-December {quarter_date.year - 1}"
    else:
        period = f"Q{quarter_date.quarter} {quarter_date.year}"
        
    total_plays = jas_row.get('Total Listeners', 0)
    total_listeners = jas_row.get('Total LDAU', 0)
    
    if deal_type.lower() == 'net':
        rev_gen_key = 'Net Revenue (Exc PG & Misc Cost) $'
        rev_share_key = f'Revenue Share at {rev_share_pct_raw} $'
        rev_generated = jas_row.get('Net Revenue (Exc PG & Misc Cost)', 0)
        rev_share_amount = jas_row.get('Author Share Net $ ', 0)
        payout_gross_or_net = jas_row.get('Author Payout Net $', 0)
        final_payout = jas_row.get('Payable Amount $ (Net)', 0)
    else:
        rev_gen_key = 'Revenue Generated (Gross) $'
        rev_share_key = f'Revenue Share at {rev_share_pct_raw} $'
        rev_generated = jas_row.get('Total Revenue Gross $', 0)
        rev_share_amount = jas_row.get('Author Share Gross $', 0)
        payout_gross_or_net = jas_row.get('Author Payout Gross $', 0)
        final_payout = jas_row.get('Payable Amount $ (Gross)', 0)
        
    # Calculate MG to be recouped
    # If Author Payout is negative, that means MG is unrecouped by that amount.
    if pd.isna(payout_gross_or_net):
        mg_recouped = mg_paid
    elif payout_gross_or_net < 0:
        mg_recouped = abs(payout_gross_or_net)
    else:
        mg_recouped = 0
        
    if pd.isna(final_payout):
        final_payout = 0
        
    # HTML replacement
    show_html = template_html
    show_html = re.sub(r'\[REPORTING_PERIOD\]', period, show_html)
    show_html = re.sub(r'\[AUTHOR_FIRST_NAME\]', author_first, show_html)
    show_html = re.sub(r'\[SHOW_NAME\]', title, show_html)
    show_html = re.sub(r'\[AUTHOR_NAME\]', author_full, show_html)
    show_html = re.sub(r'26,647', f"{float(total_plays):,.0f}", show_html)
    show_html = re.sub(r'5,993', f"{float(total_listeners):,.0f}", show_html)
    
    show_html = re.sub(r'quarterly revenue statement', 'revenue statement', show_html, flags=re.IGNORECASE)
    
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
    
    safe_title = re.sub(r'[^a-zA-Z0-9_\-]', '_', title)
    out_path = os.path.join(output_dir, f"Revenue_Statement_{safe_title}.html")
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(show_html)
        
    print(f"Generated: {out_path}")
    generated_files.append(f"Revenue_Statement_{safe_title}.html")

# Now generate index.html only for these successful ones
html = '<html><body style="font-family: Arial, sans-serif; padding: 20px;">'
html += '<h1>Revenue Statements</h1><ul>'

for f in generated_files:
    display_name = f.replace("Revenue_Statement_", "").replace(".html", "").replace("_", " ").strip()
    html += f'<li style="margin-bottom: 10px;"><a href="{f}" style="font-size: 18px; text-decoration: none; color: #0066cc;">{display_name}</a></li>'

html += '</ul>'
if len(generated_files) < len(target_series):
    html += '<p style="color: red; margin-top: 20px;">* Note: Some requested series (like Gansett) are missing from the raw data and were skipped.</p>'
html += '</body></html>'

with open(os.path.join(output_dir, 'index.html'), 'w') as f:
    f.write(html)
