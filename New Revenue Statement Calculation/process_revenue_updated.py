import pandas as pd
import math
import os
import re

jas_path = "e:/Internship/PocketFM/New Revenue Statement Calculation/JAS Self-Pub Revenue Payouts.xlsx"
html_template_path = "e:/Internship/PocketFM/docs/revenue_statement.html"
output_dir = "e:/Internship/PocketFM/New Revenue Statement Calculation/statements"

os.makedirs(output_dir, exist_ok=True)

# 1. Read the US Lifecycle Deals
deals_df = pd.read_excel(jas_path, sheet_name='US Lifecycle Deals', header=2)

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

deal_lookup = {}
for _, row in deals_df.iterrows():
    show_id = str(row.iloc[7]).strip()
    title = str(row.iloc[2]).strip()
    
    is_target = False
    for t in target_series:
        if t.lower() in title.lower():
            is_target = True
            break
            
    if show_id and show_id != 'nan' and is_target:
        deal_lookup[show_id] = {
            'genre': row.iloc[0],
            'author_name': row.iloc[1],
            'title': row.iloc[2],
            'rev_share_str': str(row.iloc[4]).strip(),
            'deal_type': str(row.iloc[5]).strip()
        }

def parse_rev_share(rs_str):
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

with open(html_template_path, 'r', encoding='utf-8') as f:
    template_html = f.read()
    
generated_files = []

for _, row in data_df.iterrows():
    show_id = str(row['Show Id']).strip()
    if show_id not in deal_lookup:
        continue
    
    deal = deal_lookup[show_id]
    deal_type = deal['deal_type'].lower()
    
    # Extract raw numbers exactly from the table
    total_plays = row['Total Listeners'] # Mapped to TOTAL PLAYS
    total_listeners = row['Total LDAU'] # Mapped to TOTAL LISTENERS
    
    if pd.isna(total_plays): total_plays = 0.0
    if pd.isna(total_listeners): total_listeners = 0.0
    
    # "1st October means from july-august-September , and 1st July means april-may-June"
    quarter_date = pd.to_datetime(row['Quarterly'])
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
    
    rev_share_pct = parse_rev_share(deal['rev_share_str'])
    mg_paid = row['Licensce Fee $']
    if pd.isna(mg_paid): mg_paid = 0.0

    show_html = template_html
    author_first_name = str(deal['author_name']).split()[0] if deal['author_name'] else ""
    
    show_html = re.sub(r'\[REPORTING_PERIOD\]', period, show_html)
    show_html = re.sub(r'\[AUTHOR_FIRST_NAME\]', author_first_name, show_html)
    show_html = re.sub(r'\[SHOW_NAME\]', deal['title'], show_html)
    show_html = re.sub(r'\[AUTHOR_NAME\]', deal['author_name'], show_html)
    show_html = re.sub(r'26,647', f"{total_plays:,.0f}", show_html)
    show_html = re.sub(r'5,993', f"{total_listeners:,.0f}", show_html)
    
    # Remove 'quarterly' from the statement intro text
    show_html = re.sub(r'quarterly revenue statement', 'revenue statement', show_html, flags=re.IGNORECASE)
    
    # Construct the dynamic tbody based on deal type
    if 'net' in deal_type:
        revenue_pg_exc = row['Revenue (PG Exc) $']
        if pd.isna(revenue_pg_exc): revenue_pg_exc = 0.0
        
        prod_costs = row['Production Cost $']
        if pd.isna(prod_costs): prod_costs = 0.0
            
        ad_costs = row['Marketing Cost $']
        if pd.isna(ad_costs): ad_costs = 0.0
            
        net_revenue = revenue_pg_exc - prod_costs - ad_costs
        rev_share_amount = net_revenue * rev_share_pct
        mg_recouped = mg_paid - rev_share_amount
        
        final_payout = row['Payable Amount $ (Net)']
        if pd.isna(final_payout): final_payout = 0.0
        
        tbody_content = f"""
                        <tr>
                            <td style="text-align: left; padding: 10px;">Revenue Generated (Gross Exc Distribution Costs) $</td>
                            <td style="text-align: right; padding: 10px;">{revenue_pg_exc:,.2f}</td>
                        </tr>
                        <tr>
                            <td style="text-align: left; padding: 10px;">Production Costs $</td>
                            <td style="text-align: right; padding: 10px;">{prod_costs:,.2f}</td>
                        </tr>
                        <tr>
                            <td style="text-align: left; padding: 10px;">Advertising & Marketing Costs $</td>
                            <td style="text-align: right; padding: 10px;">{ad_costs:,.2f}</td>
                        </tr>
                        <tr>
                            <td style="color:transparent; padding: 10px;">-</td>
                            <td></td>
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
        revenue_pg_exc = row['Revenue (PG Exc) $']
        if pd.isna(revenue_pg_exc): revenue_pg_exc = 0.0
            
        rev_share_amount = revenue_pg_exc * rev_share_pct
        mg_recouped = mg_paid - rev_share_amount
        
        final_payout = row['Payable Amount $ (Gross)']
        if pd.isna(final_payout): final_payout = 0.0
        
        tbody_content = f"""
                        <tr>
                            <td style="text-align: left; font-weight: 700; padding: 10px;">Revenue Generated (Gross) $</td>
                            <td style="text-align: right; padding: 10px;">{revenue_pg_exc:,.2f}</td>
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
                            <td style="text-align: right; padding: 10px;">{mg_paid:,.0f}</td>
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
        
    show_html = re.sub(r'<tbody>.*?</tbody>', f'<tbody>\n{tbody_content}\n</tbody>', show_html, flags=re.DOTALL)

    safe_title = re.sub(r'[^a-zA-Z0-9]', '_', deal['title'])
    html_filename = f"Revenue_Statement_{safe_title}.html"
    html_filepath = os.path.join(output_dir, html_filename)
    
    with open(html_filepath, 'w', encoding='utf-8') as f:
        f.write(show_html)
        
    generated_files.append(html_filename)

print("Done! Processed", len(generated_files), "shows.")
