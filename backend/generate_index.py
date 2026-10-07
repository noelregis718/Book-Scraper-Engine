import os

links = [f for f in os.listdir('e:/Internship/PocketFM/New Revenue Statement Calculation/statements') if f.endswith('.html') and f != 'index.html']

html = '<html><body style="font-family: Arial, sans-serif; padding: 20px;">'
html += '<h1>Revenue Statements (Filtered)</h1><ul>'

for f in links:
    display_name = f.replace("Revenue_Statement_", "").replace(".html", "").replace("_", " ").strip()
    html += f'<li style="margin-bottom: 10px;"><a href="{f}" style="font-size: 18px; text-decoration: none; color: #0066cc;">{display_name}</a></li>'

html += '</ul>'
html += '</body></html>'

with open('e:/Internship/PocketFM/New Revenue Statement Calculation/Statements/index.html', 'w') as f:
    f.write(html)
