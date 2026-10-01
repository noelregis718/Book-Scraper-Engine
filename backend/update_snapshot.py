
import re

with open('docs/apps_script_drafter.js', 'r', encoding='utf-8') as f:
    content = f.read()

cases = {
    'revStatement_workedWell_content': """      case 'revStatement_workedWell_content':
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We wanted to share a quick update on how <b>${title}</b> has been performing on Pocket FM. It's always exciting to see a story find its audience, and we thought you'd enjoy a snapshot of how listeners have been engaging with your show so far.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <b>Show Snapshot</b><br>
          • Duration Produced: [Insert Duration Produced]<br>
          • Plays / Daily Active Listeners (LDAUs): [Insert LDAUs]<br>
          • Comments: [Insert Number of Comments]<br>
          • Ratings: [Insert Ratings]<br>
          • Reviews: [Insert Reviews]
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We'll continue to keep you updated as your show reaches more listeners and share new milestones along the way.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          If your latest revenue statement reflects an amount payable, we'll send you a separate email with the invoice format and instructions to help you raise your invoice.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          If you have any questions about your show's performance or production, simply reply to this email—we're always happy to help.
          </td></tr>
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;""",
    'revStatement_didntWorkWell': """      case 'revStatement_didntWorkWell':
        const revHrefDidntWork = revLink ? revLink : "#";
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We're sharing the latest performance update for <b>${title}</b> on Pocket FM. Attached, you'll find your revenue statement for this quarter, which provides a breakdown of your earnings for the reporting period, along with a snapshot of how your show has been performing.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <b>Show Snapshot</b><br>
          • Duration Produced: [Insert Duration Produced]<br>
          • Plays / Daily Active Listeners (LDAUs): [Insert LDAUs]<br>
          • Comments: [Insert Number of Comments]<br>
          • Ratings: [Insert Ratings]<br>
          • Reviews: [Insert Reviews]
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Based on the show's performance and our internal benchmarks, we've decided not to produce additional episodes for <b>${title}</b> at this time. This is purely dependent on how our audience has been responding to this show and doesn't take away from the value of your story at all. We'll continue to share quarterly revenue statements for the episodes already live on Pocket FM.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          If you know other authors who may be a good fit for Pocket FM, we'd love an introduction. Our referral program offers meaningful incentives for every author you refer who signs with us. Please watch out for a separate email about the referral program.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          If you have any questions about your revenue statement or your show's performance, simply reply to this email—we're happy to help.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Click here to check your revenue statement: <br>
          <a href="${revHrefDidntWork}" style="color:#E51A4D; font-weight:bold; text-decoration:none;">Access Revenue Statements</a>
          </td></tr>
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;"""
}

for case_name, new_case in cases.items():
    pattern = r"(\s+case\s+'" + case_name + r"':.*?(?=\s+case\s+'|\s+}\s+return|\s+}\s+}))"
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, "\n" + new_case, content, flags=re.DOTALL)
    else:
        print(f"Could not find case {case_name}")

with open('docs/apps_script_drafter.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated snapshots successfully!")
