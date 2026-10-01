import re

with open('docs/apps_script_drafter.js', 'r', encoding='utf-8') as f:
    content = f.read()

new_cases = """      case 'quarterlyStatements':
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We hope you're doing well! It's time for the quarterly update for <b>${title}</b>. Attached, you'll find your revenue statement, which includes a detailed breakdown of your earnings for the reporting period, along with a snapshot of how your show has been performing on Pocket FM.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <b>Show Snapshot</b><br>
          • Listening Hours: [Insert Listening Hours]<br>
          • Daily Active Listeners (LDAUs): [Insert LDAUs]<br>
          • Duration Produced: [Insert Duration Produced]<br>
          • Comments: [Insert Number of Comments]
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <b>Summary of Audience Comments</b><br>
          [Insert AI Summary of Audience Comments]
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We always enjoy sharing how stories are connecting with listeners, and we hope this update gives you a helpful glimpse into your show's journey this quarter. A detailed financial breakdown is included in the attached revenue statement.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          If you have any questions about the statement or would like to discuss your show's performance, simply reply to this email — we're always happy to help.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Thank you for being part of the Pocket FM community. We look forward to sharing more updates with you in the months ahead!
          </td></tr>
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;

      case 'eventMixer':
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We're hosting <b>[Event Name]</b> on <b>[Date]</b> in <b>[Location]</b>, and we'd love to have you join us.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          [Event Description]
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          It's a chance to meet fellow Pocket FM authors, connect with our editorial, production, and partnerships teams, and hear more about what's happening across the platform. Whether you're looking to exchange ideas, learn from other creators, or simply spend an evening with the Pocket FM community, we'd be delighted to see you there.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <a href="[Insert RSVP Link]" style="color:#E51A4D; font-weight:bold; text-decoration:none;">RSVP Here</a>
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          If you have any questions about the event, just reply to this email—we're happy to help.
          </td></tr>
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;

      case 'publicNews':
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We wanted to share an update from Pocket FM that we thought you might find interesting.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <b>[Insert News Headline]</b><br>
          [Insert News Summary]
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We'll continue to keep you posted whenever there are developments that we think are relevant to our authors and publishing partners.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          If you'd like to read the full announcement, you can find it here:<br>
          <a href="[Insert Article Link]" style="color:#E51A4D; font-weight:bold; text-decoration:none;">Read More</a>
          </td></tr>
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;
"""

pattern = r"(\s+case\s+'revStatement_didntWorkWell':.*?)(?=\s+}\s+})"
if re.search(pattern, content, re.DOTALL):
    content = re.sub(pattern, r"\1\n\n" + new_cases.replace('\\', '\\\\'), content, flags=re.DOTALL)
else:
    print("Could not find the target location to insert new templates.")

with open('docs/apps_script_drafter.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Added missing templates successfully!")
