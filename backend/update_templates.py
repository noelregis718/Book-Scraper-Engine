import re

with open('docs/apps_script_drafter.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Define the new cases
cases = {
    'welcome': """      case 'welcome':
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Welcome to Pocket FM! We couldn't be more excited to have you join the platform. It's always a good day when a new story (and a new author) becomes part of the community.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Here's a quick walkthrough of what happens next:
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <b>Onboarding & Documentation</b><br>
          Within 1 business day of this email, you'll receive a follow-up from us with the vendor onboarding documents, manuscript submission instructions, and invoice requirements to kick off the formal onboarding process.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <b>MG Payment</b><br>
          Once all documentation is submitted from your end, we'll initiate your Minimum Guarantee (MG) payment. As per your contract, this is paid out within 30 days of the contract signing date. We'll send you a confirmation once the payment has been processed.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <b>Production & Launch</b><br>
          Once onboarding is complete, we'll move into production. The typical timeline for production and launching your show on Pocket FM is around 3 months. We'll keep you updated as we reach key milestones throughout the process, including when your show goes live.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <b>Revenue Statements</b><br>
          As outlined in the contract, we share revenue statements on a quarterly basis. You'll need to raise an invoice against each statement to receive your payment.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <b>Support</b><br>
          Our Relationship Management team is always here if you have any questions along the way. Just reply to this email.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We're genuinely glad to be starting this journey with you, and we look forward to bringing your story to listeners around the world.
          </td></tr>
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;""",
    'vendor': """      case 'vendor':
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Now the exciting part begins: let's get everything in place so we can start bringing your story to life on Pocket FM!
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Please share the manuscript(s) for your licensed series with us in DOC or PDF format.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          As the next step, we'll onboard you as a vendor in our systems so we can disburse your Minimum Guarantee (MG) payment and any subsequent revenue-linked payouts.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <b>Required Documents for Vendor Onboarding</b><br>
          Please share the following documents as separate attachments/PDFs:<br>
          • W-9 (if you're a US citizen) or W-8BEN (if you're a non-US citizen) (attached). If you would like to be onboarded as an entity, please complete the W-8BEN-E form instead.<br>
          • Signed Vendor Registration Form (VRF) (attached)<br>
          • Conflict of Interest (COI) Declaration (attached)<br>
          • Bank letter or void cheque, along with your bank account details.<br>
          • Invoice for the Minimum Guarantee / Advance (details below).
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <b>Important:</b> Please ensure that the legal name mentioned on the bank letter / void cheque or bank account details matches the name you provide on the invoice, W-9, VRF and COI declaration. Whatever name appears on your bank cheque or bank proof must match across all documents. This consistency is critical to avoid payment delays.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <b>Invoice for the Minimum Guarantee / Advance</b><br>
          Along with the documents above, please share an invoice for the minimum guarantee / advance amount. The invoice must include the following details:
          </td></tr>
          <tr><td align="center" style="padding:10px 35px;">
            <table width="100%" border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse; border-color:#e0e0e0; font-size:14px; text-align:left;">
              <tr style="background-color:#f8f8f8;"><th>Field</th><th>Applicability</th><th>Description</th></tr>
              <tr><td><b>Heading</b></td><td>Mandatory</td><td>Must be titled “Tax Invoice,” “Invoice,” or “Sales Invoice.” Proforma invoices and quotations cannot be accepted.</td></tr>
              <tr><td><b>Date</b></td><td>Mandatory</td><td>Invoice date</td></tr>
              <tr><td><b>Invoice No.</b></td><td>Mandatory</td><td>Must be unique</td></tr>
              <tr><td><b>Vendor Name</b></td><td>Mandatory</td><td>Complete legal name, as provided in the onboarding form</td></tr>
              <tr><td><b>Address</b></td><td>Mandatory</td><td>Complete registered address, including city, state, and pin/ZIP code</td></tr>
              <tr><td><b>Phone & Email</b></td><td>Optional</td><td>—</td></tr>
              <tr><td><b>PO Number</b></td><td>Optional</td><td>—</td></tr>
              <tr><td><b>VAT</b></td><td>If applicable</td><td>VAT number is mandatory where applicable</td></tr>
              <tr><td><b>Pocket Entertainment Corp Details</b></td><td>Mandatory</td><td>POCKET ENTERTAINMENT SERVICES LLC, 13 W Main Street, PO Box 953, Felton, DE 19943, County of Kent</td></tr>
              <tr><td><b>Product / Service Description</b></td><td>Mandatory</td><td>Clear description of the product or service</td></tr>
              <tr><td><b>Service Period</b></td><td>Mandatory</td><td>Should match the term specified in the agreement</td></tr>
              <tr><td><b>Amount</b></td><td>Mandatory</td><td>Clear bifurcation of base amount and VAT (if applicable)</td></tr>
              <tr><td><b>Bank Details</b></td><td>Mandatory</td><td>Beneficiary name, account number / IBAN, SWIFT code, routing number (mandatory for US vendors), local transit number, and bank name</td></tr>
              <tr><td><b>Signature</b></td><td>Mandatory</td><td>Digital or wet signature</td></tr>
            </table>
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <a href="https://drive.google.com/drive/folders/1YasA2TJL27zcyin1A-Wg-eJq9_vTQnL0" style="color:#E51A4D; font-weight:bold; text-decoration:none;">Access Onboarding Documents Here</a>
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Let us know if you have any questions — happy to help.
          </td></tr>
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;""",
    'mgInitiated': """      case 'mgInitiated':
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Great news—your Minimum Guarantee (MG) payment has now been initiated from our end for <b>${title}</b>.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          The amount should reflect in your account once your bank completes the processing. If you don't receive it within the usual banking timeline (7-10 days), please let us know and we'll be happy to look into it.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          With this milestone complete, we're one step closer to bringing your story to listeners around the world.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Thank you once again for partnering with Pocket FM.
          </td></tr>
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;""",
    'mgConfirmed': """      case 'mgConfirmed':
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We're happy to let you know that the Minimum Guarantee (MG) payment for <b>${title}</b> has been successfully processed and credited to your registered bank account.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          As we wrap up the onboarding process, we'd love to hear about your experience working with us. Your feedback helps us improve the experience for future authors and partners.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <a href="https://forms.gle/3nJwBt4KgnzgTThH6" style="color:#E51A4D; font-weight:bold; text-decoration:none;">Take our quick 2-minute survey here</a>
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          If you have any questions regarding your payment or anything else along the way, simply reply to this email; we're always happy to help.
          </td></tr>
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;""",
    'checkIn1': """      case 'checkIn1':
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We hope you're doing well!
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          As <b>${title}</b> continues its journey with Pocket FM, we'd love to learn a little more about the world you've created. While production is already underway, there are often small details, character nuances, or creative insights that don't always make it onto the page but can be incredibly valuable for our teams as we continue building and promoting the adaptation.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We have just two quick questions—it should take less than two minutes.<br><br>
          1. Is there a character, relationship, or recurring theme from <b>${title}</b> that you feel readers connect with the most, and that you'd like us to know?<br>
          2. Is there anything about the world, tone, or characters of <b>${title}</b> that you'd want our team to keep in mind as the adaptation evolves?
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          While we may not be able to incorporate every suggestion into the current production, your perspective helps us better understand your story and informs future creative, marketing, and audience engagement decisions.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          In case the creative team has any questions for you, we might reach out again for clarifications.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          If you haven't already had a chance to do so, we'd also appreciate your feedback on your onboarding experience. It helps us improve the experience for future authors and partners.<br>
          <a href="https://forms.gle/3nJwBt4KgnzgTThH6" style="color:#E51A4D; font-weight:bold; text-decoration:none;">Share your onboarding feedback here</a>
          </td></tr>
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;""",
    'checkIn2': """      case 'checkIn2':
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We hope you're doing well!
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          It's been about a month since we completed the onboarding process, so we wanted to share a quick update on <b>${title}</b>.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          The show is currently under production, and our team is actively working on bringing your story to life. Producing a high-quality audio adaptation involves several stages, and we're making steady progress behind the scenes. We'll continue to keep you updated as we reach key milestones along the way.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          If you haven't already had a chance to do so, we'd also love to hear about your onboarding experience. Your feedback helps us improve the experience for future authors and partners.<br>
          <a href="https://forms.gle/3nJwBt4KgnzgTThH6" style="color:#E51A4D; font-weight:bold; text-decoration:none;">Share your feedback here</a>
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We'll be in touch with more updates on <b>${title}</b> as production progresses.
          </td></tr>
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;""",
    'launch': """      case 'launch':
        const revHrefLaunch = revLink ? revLink : "#";
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Exciting news! Your work <b>${title}</b> is now live on Pocket FM!
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Congratulations on reaching this milestone. Feel free to check out the show here on the app: <a href="${link}" style="color:#E51A4D;">${link}</a>
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Over the coming weeks, we'll closely track the show's performance. From listener engagement to audience feedback, and we'll keep you updated as it finds its audience.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Please also find attached your quarterly revenue statement, which includes a breakdown of your show's performance for the reporting period.<br>
          <a href="${revHrefLaunch}" style="color:#E51A4D; font-weight:bold; text-decoration:none;">Access Revenue Statements</a>
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          The Amount Due for this quarter is $0.00, as the show is still recouping the Minimum Guarantee (MG) advance paid under the agreement. We've also attached the revenue calculation for your reference. Once the MG has been fully recouped, any subsequent revenue due will be payable in accordance with the agreement.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          If you'd like to help spread the word, we'd love for you to share the show with your readers, followers, friends, and family. Every new listener helps your story reach even more people.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Thank you for trusting Pocket FM with your story. We can't wait to see where this journey takes us!
          </td></tr>
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;""",
    'revStatement_workedWell_content': """      case 'revStatement_workedWell_content':
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We wanted to share a quick update on how <b>${title}</b> has been performing on Pocket FM. It's always exciting to see a story find its audience, and we thought you'd enjoy a snapshot of how listeners have been engaging with your show so far.
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
    'revStatement_workedWell_payment': """      case 'revStatement_workedWell_payment':
        const revHrefPay = revLink ? revLink : "#";
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We're excited to share the latest performance update for <b>${title}</b> on Pocket FM. Attached, you'll find your revenue statement for this quarter, which provides a detailed breakdown of your earnings for the reporting period, along with a snapshot of how your show has been performing on the platform.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <b>Invoice template for the revenue share payment</b><br>
          Please share an invoice for the due amount for us to process the payout. The invoice must include the details provided in your onboarding guidelines.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          If you have any questions about the attached revenue statement or your show's performance, simply reply to this email - we're happy to help.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Click here to check your revenue statement: <br>
          <a href="${revHrefPay}" style="color:#E51A4D; font-weight:bold; text-decoration:none;">Access Revenue Statements</a>
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

# Use regex to find and replace each case block
for case_name, new_case in cases.items():
    # Regex to match from "case 'NAME':" up to the next "case" or the end of the switch block
    # It safely captures everything including the return statement
    pattern = r"(\s+case\s+'" + case_name + r"':.*?(?=\s+case\s+'|\s+}\s+return|\s+}\s+}))"
    
    # Check if the case exists
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, "\n" + new_case, content, flags=re.DOTALL)
    else:
        print(f"Could not find case {case_name}")

with open('docs/apps_script_drafter.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated templates successfully!")
