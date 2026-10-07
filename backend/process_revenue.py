import pandas as pd
import math
import os
import re

jas_path = "e:/Internship/PocketFM/New Revenue Statement Calculation/JAS Self-Pub Revenue Payouts.xlsx"
html_template_path = "e:/Internship/PocketFM/docs/revenue_statement.html"
output_dir = "e:/Internship/PocketFM/New Revenue Statement Calculation/statements"
output_excel = "e:/Internship/PocketFM/New Revenue Statement Calculation/JAS Self-Pub Revenue Payouts_Processed.xlsx"

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

# 2. Read the JAS Consolidated data
data_df = pd.read_excel(jas_path, sheet_name='JAS Consolidated All Shows Reve')

# Sort by Quarterly descending and drop duplicates by Show Id to keep the most recent quarter
data_df['Quarterly_DT'] = pd.to_datetime(data_df['Quarterly'], errors='coerce')
data_df = data_df.sort_values('Quarterly_DT', ascending=False).drop_duplicates(subset=['Show Id'])


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
    
    # Extract raw numbers exactly from the table
    total_plays = row['Total Listeners'] # Mapped to TOTAL PLAYS
    total_listeners = row['Total LDAU'] # Mapped to UNIQUE LISTENERS (LDAU)
    revenue_pg_exc = row['Revenue (PG Exc) $']
    net_revenue_col = row['Net Revenue (Exc PG & Misc Cost)']
    mg_paid = row['Licensce Fee $']
    
    if pd.isna(revenue_pg_exc): revenue_pg_exc = 0.0
    if pd.isna(net_revenue_col): net_revenue_col = 0.0
    if pd.isna(mg_paid): mg_paid = 0.0
    
    # Calculate and map based on Deal Type
    if 'net' in deal_type:
        calc_type = 'Net'
        rev_share_amount = row['Author Share Net $ ']
        author_payout = row['Author Payout Net $']
        final_payout = row['Payable Amount $ (Net)']
    else:
        calc_type = 'Gross'
        rev_share_amount = row['Author Share Gross $']
        author_payout = row['Author Payout Gross $']
        final_payout = row['Payable Amount $ (Gross)']
        
    if pd.isna(rev_share_amount): rev_share_amount = 0.0
    if pd.isna(author_payout): author_payout = 0.0
    if pd.isna(final_payout): final_payout = 0.0
    
    # MG to be recouped logic based on table values
    mg_recouped = 0.0
    if author_payout < 0:
        mg_recouped = abs(author_payout)
        
    if mg_recouped == 0:
        final_payout = 0.0

    # Add to consolidated list
    consolidated_rows.append({
        'Show ID': show_id,
        'Title': deal['title'],
        'Author': deal['author_name'],
        'Deal Type': deal['deal_type'],
        'Rev Share %': deal['rev_share_str'],
        'Total Plays': total_plays,
        'Total Listeners': total_listeners,
        'Revenue Generated $': revenue_pg_exc,
        'Net Revenue $ (If Net)': net_revenue_col if calc_type == 'Net' else None,
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
    
    # Determine the reporting period based on Slack instructions
    title_lower = deal['title'].lower()
    author_lower = deal['author_name'].lower()
    group_1_keywords = ['blake', 'st. martin', 'st. marin', 'sweet tea witch', 'lattes and levitation', 'psychic seasons']
    is_group_1 = any(kw in title_lower or kw in author_lower for kw in group_1_keywords)
    
    if is_group_1:
        reporting_period = "April-May-June & July-August-September 2026"
    else:
        reporting_period = "July-August-September 2026"
        
    show_html = re.sub(r'\[REPORTING_PERIOD\]', reporting_period, show_html)
    show_html = re.sub(r'\[AUTHOR_FIRST_NAME\]', author_first_name, show_html)
    show_html = re.sub(r'\[SHOW_NAME\]', deal['title'], show_html)
    show_html = re.sub(r'\[AUTHOR_NAME\]', deal['author_name'], show_html)
    show_html = re.sub(r'26,647', f"{total_plays:,.0f}", show_html)
    show_html = re.sub(r'5,993', f"{total_listeners:,.0f}", show_html)
    
    # Remove 'quarterly' from the statement intro text
    show_html = re.sub(r'quarterly revenue statement', 'revenue statement', show_html, flags=re.IGNORECASE)
    
    # Construct the dynamic tbody based on deal type
    if calc_type == 'Net':
        tbody_content = f"""
                        <tr>
                            <td style="text-align: left; font-weight: 700; padding: 10px;">Revenue Generated Gross - Distribution Costs $</td>
                            <td style="text-align: right; padding: 10px;">{revenue_pg_exc:,.2f}</td>
                        </tr>
                        <tr>
                            <td style="text-align: left; padding: 10px;">Net Revenue (Exc Advertising & Marketing Costs) $</td>
                            <td style="text-align: right; padding: 10px;">{net_revenue_col:,.2f}</td>
                        </tr>
                        <tr>
                            <td style="text-align: left; padding: 10px;">Revenue Share (Net) at {deal['rev_share_str']} $</td>
                            <td style="text-align: right; padding: 10px;">{rev_share_amount:,.2f}</td>
                        </tr>
                        <tr>
                            <td style="color:transparent; padding: 10px;">-</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td style="text-align: left; padding: 10px;">MG Paid (License Fee) $</td>
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
                            <td style="text-align: left; font-weight: 700; padding: 10px;">Revenue Generated Gross - Distribution Costs $</td>
                            <td style="text-align: right; padding: 10px;">{revenue_pg_exc:,.2f}</td>
                        </tr>
                        <tr>
                            <td style="text-align: left; padding: 10px;">Revenue Share (Gross) at {deal['rev_share_str']} $</td>
                            <td style="text-align: right; padding: 10px;">{rev_share_amount:,.2f}</td>
                        </tr>
                        <tr>
                            <td style="color:transparent; padding: 10px;">-</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td style="text-align: left; padding: 10px;">MG Paid (License Fee) $</td>
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
