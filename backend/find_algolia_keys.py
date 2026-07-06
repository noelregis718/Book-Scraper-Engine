import re

with open('e:/Internship/PocketFM/backend/harlequin_dump.html', encoding='utf-8') as f:
    html = f.read()

app_id = re.findall(r'applicationId\s*:\s*[\'\"]([^\'\"]+)[\'\"]', html)
api_key = re.findall(r'apiKey\s*:\s*[\'\"]([^\'\"]+)[\'\"]', html)

print('AppID:', app_id)
print('APIKey:', api_key)

# Also check for Shopify.algolia variables
algolia_vars = re.findall(r'Shopify\.algolia\s*=\s*({[^}]+})', html)
if algolia_vars:
    print('Found Shopify.algolia object!')
