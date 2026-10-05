import pandas as pd
import math
import os
import re

jas_path = "e:/Internship/PocketFM/JAS Self-Pub Revenue Payouts (1).xlsx"
html_template_path = "e:/Internship/PocketFM/docs/revenue_statement.html"
output_dir = "e:/Internship/PocketFM/docs/statements"
output_excel = "e:/Internship/PocketFM/JAS Self-Pub Revenue Payouts (1)_Processed.xlsx"

os.makedirs(output_dir, exist_ok=True)

# 1. Read the US Lifecycle Deals
# Header is at row index 2 (0-indexed)
deals_df = pd.read_excel(jas_path, sheet_name='US Lifecycle Deals', header=2)

# Create a lookup dictionary by Show ID
# Column H is index 7: 'Show ID (after show creation)'
# Column F is index 5: 'Gross / Net Deal'
# Column E is index 4: 'Rev share %'
deal_lookup = {}
for _, row in deals_df.iterrows():
    show_id = str(row.iloc[7]).strip()
    if show_id and show_id != 'nan':
        deal_lookup[show_id] = {
            'genre': row.iloc[0],
            'author_name': row.iloc[1],
            'title': row.iloc[2],
            'rev_share_str': str(row.iloc[4]).strip(),
            'deal_type': str(row.iloc[5]).strip()
        }

def parse_rev_share(rs_str):
    # E.g., '15%', '15% of gross', '23.5% -( 20% on Gross)'
    # Just extract the first floating number and divide by 100
    if not rs_str or rs_str == 'nan':
        return 0.0
    match = re.search(r'([\d\.]+)', rs_str)
    if match:
        return float(match.group(1)) / 100.0
    return 0.0

# 2. Read the Oct 1, 2026 data
data_df = pd.read_excel(jas_path, sheet_name='Oct 1, 2026')

# 3. Process each show
consolidated_rows = []

# To update the US Lifecycle Deals with HTML links later
# We'll map Show ID -> link
html_links = {}

with open(html_template_path, 'r', encoding='utf-8') as f:
    template_html = f.read()

for _, row in data_df.iterrows():
    show_id = str(row['Show Id']).strip()
    if show_id not in deal_lookup:
        continue
    
    deal = deal_lookup[show_id]
    deal_type = deal['deal_type'].lower()
    rev_share = parse_rev_share(deal['rev_share_str'])
    
    # Extract raw numbers
    total_plays = row['Total Listeners'] # Column index 4
    total_listeners = row['Total LDAU'] # Column index 5
    revenue_pg_exc = row['Revenue (PG Exc) $']
    marketing_cost = row['Marketing Cost $']
    production_cost = row['Production Cost $']
    mg_paid = row['Licensce Fee $']
    
    if pd.isna(revenue_pg_exc): revenue_pg_exc = 0.0
    if pd.isna(marketing_cost): marketing_cost = 0.0
    if pd.isna(production_cost): production_cost = 0.0
    if pd.isna(mg_paid): mg_paid = 0.0
    
    # Calculate
    if 'net' in deal_type:
        calc_type = 'Net'
        rev_generated = revenue_pg_exc
        net_revenue = rev_generated - marketing_cost - production_cost
        rev_share_amount = net_revenue * rev_share
    else:
        calc_type = 'Gross'
        rev_generated = revenue_pg_exc
        net_revenue = rev_generated # same for gross
        rev_share_amount = rev_generated * rev_share
        
    mg_recouped = mg_paid - rev_share_amount
    if mg_recouped < 0: mg_recouped = 0.0 # Standard recoup logic
    
    final_payout = rev_share_amount - mg_paid
    if final_payout < 0: final_payout = 0.0
    
    # Add to consolidated list
    consolidated_rows.append({
        'Show ID': show_id,
        'Title': deal['title'],
        'Author': deal['author_name'],
        'Deal Type': deal['deal_type'],
        'Rev Share %': deal['rev_share_str'],
        'Total Plays': total_plays,
        'Total Listeners': total_listeners,
        'Revenue Generated $': rev_generated,
        'Net Revenue $ (If Net)': net_revenue if calc_type == 'Net' else None,
        'Rev Share Amount $': rev_share_amount,
        'MG Paid $': mg_paid,
        'MG to be recouped $': mg_recouped,
        'Final Payout $': final_payout
    })
    
    # --- Generate HTML ---
    # Create a copy of template
    show_html = template_html
    
    # Replace the title and metrics
    author_first_name = deal['author_name'].split()[0] if deal['author_name'] else ""
    show_html = re.sub(r'\[AUTHOR_FIRST_NAME\]', author_first_name, show_html)
    show_html = re.sub(r'\[SHOW_NAME\]', deal['title'], show_html)
    show_html = re.sub(r'\[AUTHOR_NAME\]', deal['author_name'], show_html)
    show_html = re.sub(r'26,647', f"{total_plays:,.0f}", show_html)
    show_html = re.sub(r'5,993', f"{total_listeners:,.0f}", show_html)
    
    # Construct the dynamic tbody based on deal type
    if calc_type == 'Net':
        tbody_content = f"""
                        <tr>
                            <td style="text-align: left; font-weight: 700; padding: 10px;">Revenue Generated (Gross Exc Distribution Costs) $</td>
                            <td style="text-align: right; padding: 10px;">{rev_generated:,.2f}</td>
                        </tr>
                        <tr>
                            <td style="text-align: left; padding: 10px;">Production Costs $</td>
                            <td style="text-align: right; padding: 10px;">{production_cost:,.2f}</td>
                        </tr>
                        <tr>
                            <td style="text-align: left; padding: 10px;">Advertising & Marketing Costs $</td>
                            <td style="text-align: right; padding: 10px;">{marketing_cost:,.2f}</td>
                        </tr>
                        <tr>
                            <td style="text-align: left; font-weight: 700; padding: 10px;">Net Revenue $</td>
                            <td style="text-align: right; font-weight: 700; padding: 10px;">{net_revenue:,.2f}</td>
                        </tr>
                        <tr>
                            <td style="text-align: left; padding: 10px;">Revenue Share at {deal['rev_share_str']} $</td>
                            <td style="text-align: right; padding: 10px;">{rev_share_amount:,.2f}</td>
                        </tr>
                        <tr>
                            <td style="color:transparent; padding: 10px;">-</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td style="text-align: left; padding: 10px;">MG Paid $</td>
                            <td style="text-align: right; padding: 10px;">{mg_paid:,.2f}</td>
                        </tr>
                        <tr>
                            <td style="text-align: left; padding: 10px;">MG to be recouped $</td>
                            <td style="text-align: right; padding: 10px;">{mg_recouped:,.2f}</td>
                        </tr>
                        <tr style="background-color: #bfbfbf; font-weight: 700;">
                            <td style="text-align: left; font-size: 15px; padding: 10px;">Final Payout $</td>
                            <td style="text-align: right; font-size: 15px; padding: 10px;">{final_payout:,.2f}</td>
                        </tr>
        """
    else:
        tbody_content = f"""
                        <tr>
                            <td style="text-align: left; font-weight: 700; padding: 10px;">Revenue Generated (Gross) $</td>
                            <td style="text-align: right; padding: 10px;">{rev_generated:,.2f}</td>
                        </tr>
                        <tr>
                            <td style="text-align: left; padding: 10px;">Revenue Share at {deal['rev_share_str']} $</td>
                            <td style="text-align: right; padding: 10px;">{rev_share_amount:,.2f}</td>
                        </tr>
                        <tr>
                            <td style="color:transparent; padding: 10px;">-</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td style="text-align: left; padding: 10px;">MG Paid $</td>
                            <td style="text-align: right; padding: 10px;">{mg_paid:,.2f}</td>
                        </tr>
                        <tr>
                            <td style="color:transparent; padding: 10px;">-</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td style="text-align: left; padding: 10px;">MG to be recouped $</td>
                            <td style="text-align: right; padding: 10px;">{mg_recouped:,.2f}</td>
                        </tr>
                        <tr style="background-color: #bfbfbf; font-weight: 700;">
                            <td style="text-align: left; font-size: 15px; padding: 10px;">Final Payout $</td>
                            <td style="text-align: right; font-size: 15px; padding: 10px;">{final_payout:,.2f}</td>
                        </tr>
        """
        
    # Replace everything between <tbody> and </tbody>
    show_html = re.sub(r'<tbody>.*?</tbody>', f'<tbody>\n{tbody_content}\n</tbody>', show_html, flags=re.DOTALL)

    # Save HTML
    safe_title = re.sub(r'[^a-zA-Z0-9]', '_', deal['title'])
    html_filename = f"Revenue_Statement_{safe_title}.html"
    html_filepath = os.path.join(output_dir, html_filename)
    
    with open(html_filepath, 'w', encoding='utf-8') as f:
        f.write(show_html)
        
    # Store link
    html_links[show_id] = html_filepath

# 4. Write back to Excel
print("Writing data to Excel...")
consolidated_df = pd.DataFrame(consolidated_rows)

# Load workbook to preserve other sheets and update
with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
    # Copy original sheets
    xls = pd.ExcelFile(jas_path)
    for sheet_name in xls.sheet_names:
        df_sheet = pd.read_excel(jas_path, sheet_name=sheet_name, header=None)
        
        # If it's US Lifecycle Deals, update the links
        if sheet_name == 'US Lifecycle Deals':
            # Row index 2 is header. Column I is index 8.
            # We need to insert the links
            for i in range(3, len(df_sheet)):
                sid = str(df_sheet.iloc[i, 7]).strip()
                if sid in html_links:
                    df_sheet.iloc[i, 8] = html_links[sid]
        
        df_sheet.to_excel(writer, sheet_name=sheet_name, index=False, header=False)

    # Write the new Consolidated sheet
    consolidated_df.to_excel(writer, sheet_name='JAS Consolidated All Shows Reve', index=False)

print("Done! Processed", len(consolidated_rows), "shows.")
