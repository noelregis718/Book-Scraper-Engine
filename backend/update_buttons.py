import re

with open('docs/apps_script_drafter.js', 'r', encoding='utf-8') as f:
    content = f.read()

def get_button_html(href, text):
    return f"""<table border="0" cellspacing="0" cellpadding="0" style="margin-top: 10px; margin-bottom: 10px;">
            <tr>
              <td align="center" style="border-radius: 6px; background-color: #E51A4D;">
                <a href="{href}" target="_blank" style="font-size: 16px; font-weight: bold; color: #ffffff; text-decoration: none; border-radius: 6px; padding: 12px 24px; border: 1px solid #E51A4D; display: inline-block;">{text}</a>
              </td>
            </tr>
          </table>"""

# Regex pattern to find all anchor tags inside the cases.
# We will just do targeted replacements to be safe.

replacements = [
    (r'<a href="https://drive\.google\.com/drive/folders/1YasA2TJL27zcyin1A-Wg-eJq9_vTQnL0" style="color:#E51A4D; font-weight:bold; text-decoration:none;">Access Onboarding Documents Here</a>',
     get_button_html("https://drive.google.com/drive/folders/1YasA2TJL27zcyin1A-Wg-eJq9_vTQnL0", "Access Onboarding Documents")),
     
    (r'<a href="https://forms\.gle/3nJwBt4KgnzgTThH6" style="color:#E51A4D; font-weight:bold; text-decoration:none;">Take our quick 2-minute survey here</a>',
     get_button_html("https://forms.gle/3nJwBt4KgnzgTThH6", "Take the 2-Minute Survey")),
     
    (r'<a href="https://forms\.gle/3nJwBt4KgnzgTThH6" style="color:#E51A4D; font-weight:bold; text-decoration:none;">Share your onboarding feedback here</a>',
     get_button_html("https://forms.gle/3nJwBt4KgnzgTThH6", "Share Onboarding Feedback")),
     
    (r'<a href="https://forms\.gle/3nJwBt4KgnzgTThH6" style="color:#E51A4D; font-weight:bold; text-decoration:none;">Share your feedback here</a>',
     get_button_html("https://forms.gle/3nJwBt4KgnzgTThH6", "Share Your Feedback")),
     
    (r'<a href="\$\{link\}" style="color:#E51A4D;">\$\{link\}</a>',
     get_button_html("${link}", "Listen on Pocket FM")),
     
    (r'<a href="\$\{revHrefLaunch\}" style="color:#E51A4D; font-weight:bold; text-decoration:none;">Access Revenue Statements</a>',
     get_button_html("${revHrefLaunch}", "Access Revenue Statements")),
     
    (r'<a href="\$\{revHrefPay\}" style="color:#E51A4D; font-weight:bold; text-decoration:none;">Access Revenue Statements</a>',
     get_button_html("${revHrefPay}", "Access Revenue Statements")),
     
    (r'<a href="\$\{revHrefDidntWork\}" style="color:#E51A4D; font-weight:bold; text-decoration:none;">Access Revenue Statements</a>',
     get_button_html("${revHrefDidntWork}", "Access Revenue Statements")),
     
    (r'<a href="\[Insert RSVP Link\]" style="color:#E51A4D; font-weight:bold; text-decoration:none;">RSVP Here</a>',
     get_button_html("[Insert RSVP Link]", "RSVP Here")),
     
    (r'<a href="\[Insert Article Link\]" style="color:#E51A4D; font-weight:bold; text-decoration:none;">Read More</a>',
     get_button_html("[Insert Article Link]", "Read More"))
]

for old_regex, new_html in replacements:
    content = re.sub(old_regex, new_html, content)

with open('docs/apps_script_drafter.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Button styles applied successfully!")
