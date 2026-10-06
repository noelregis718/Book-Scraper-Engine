import os

links = [
    'Revenue_Statement_Vital_Secrets.html',
    'Revenue_Statement_Mrs__Lillywhite_Investigates_Mysteries.html',
    'Revenue_Statement_Liz_Talbot_Mystery_Series.html',
    'Revenue_Statement_Carolina_Tales.html',
    'Revenue_Statement_Detective_Emilia_Cruz.html',
    'Revenue_Statement_Fatal_Series.html',
    'Revenue_Statement_Fate_Weaver_Series.html',
    'Revenue_Statement_The_Witches_of_Wheeler_Park.html',
    'Revenue_Statement_Jackal_Among_Snakes.html',
    'Revenue_Statement_Redemption_Arc.html',
    'Revenue_Statement_Gansett_Series.html'
]

html = '<html><body style="font-family: Arial, sans-serif; padding: 20px;">'
html += '<h1>Revenue Statements (Filtered)</h1><ul>'

for f in links:
    display_name = f.replace("Revenue_Statement_", "").replace(".html", "").replace("_", " ").strip()
    html += f'<li style="margin-bottom: 10px;"><a href="{f}" style="font-size: 18px; text-decoration: none; color: #0066cc;">{display_name}</a></li>'

html += '</ul>'
html += '</body></html>'

with open('e:/Internship/PocketFM/New Revenue Statement Calculation/Statements/index.html', 'w') as f:
    f.write(html)
