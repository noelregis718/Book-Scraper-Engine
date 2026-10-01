import re

with open('docs/apps_script_drafter.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to find the testAllTemplates function block
pattern = r"// -------------------------------------------------------------\n// ONE-CLICK TEST GENERATOR \(FOR MANAGER REVIEW\)\n// -------------------------------------------------------------\nfunction testAllTemplates\(\) \{.*?\n\}\n"

content = re.sub(pattern, "", content, flags=re.DOTALL)

with open('docs/apps_script_drafter.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Removed testAllTemplates successfully!")
