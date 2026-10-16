/**
 * =============================================================
 * POCKET FM LIFECYCLE CRM AUTOMATION - MODULE 2: EMAIL TEMPLATES
 * File: Templates.gs (or Templates.js)
 * =============================================================
 * Responsive Pocket FM HTML Email Design System.
 * Contains wrapHtml() and getBody() for all 12 outreach stages.
 */

// -------------------------------------------------------------
// HELPER FUNCTIONS (MOVED TO GLOBAL SCOPE)
// -------------------------------------------------------------
function wrapHtml(bodyContent, queueId = "") {
    return `<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="color-scheme" content="light only"><meta name="supported-color-schemes" content="light only"><link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&display=swap" rel="stylesheet"><title>Pocket FM Email</title></head><body aria-disabled="false" style='margin: 0px; font-family: Poppins, "Noto Sans", "Helvetica Neue", Helvetica, Arial, sans-serif;'>


<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-color:#ffffff; width:600px;"><tbody><tr><td align="center">
<table border="0" cellpadding="0" cellspacing="0" style="background-color:#000000; width:600px;"><tbody><!-- Header -->
<tr><td align="center">
<img alt="Pocket FM Logo" src="https://d2p67bdkbtpxn2.cloudfront.net/c8b7ada83f09146d4b2c2ba3a5c3c1b8ea36e459.jpg" style="display:block; max-width:600px;">
</td></tr>

<tr><td align="center" style="padding-top:15px;">
<table border="0" cellpadding="0" cellspacing="0" style="background-color:#FFFFFF; width:600px; border-radius:10px;"><tbody>
${bodyContent}
</tbody></table>
</td></tr>

<!-- Footer spacing -->
<tr><td style="padding-top:10px;"></td></tr>

<!-- Footer -->
<tr><td style="padding:20px;">
<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-color:#121212; border-radius:10px; width:600px;"><tbody><tr><td align="center" style="padding:30px 0;">
<img alt="Pocket FM Logo" src="https://d2p67bdkbtpxn2.cloudfront.net/dd1600b8e1bde867061ac29dcf9078c72bc533bd.jpg" height="50" style="display:block;">
</td></tr>

<!-- Social icons -->
<tr><td align="center">
<table border="0" cellpadding="0" cellspacing="0"><tbody><tr><td style="padding:0 10px;"><a href="https://twitter.com/PocketFM_App" target="_blank"><img src="https://d2p67bdkbtpxn2.cloudfront.net/2ef29b0580cbc86db3effe6847cbf3c92024b814.png" height="30"></a></td>
<td style="padding:0 10px;"><a href="https://www.linkedin.com/company/14522609" target="_blank"><img src="https://d2p67bdkbtpxn2.cloudfront.net/fc05471fbe97d71f1b8037897029df3759916d7c.png" height="30"></a></td>
<td style="padding:0 10px;"><a href="https://www.facebook.com/pocketfmusa" target="_blank"><img src="https://d2p67bdkbtpxn2.cloudfront.net/bbba48b905fdc913ca50e2014cd43130eb2a6190.png" height="30"></a></td>
<td style="padding:0 10px;"><a href="https://www.instagram.com/pocketfm_usa/?hl=en" target="_blank"><img src="https://d2p67bdkbtpxn2.cloudfront.net/7f5a11ba1d1e0430dc41bc2679fec746478b9dba.png" height="30"></a></td>
<td style="padding:0 10px;"><a href="https://www.youtube.com/@PocketFM.Official" target="_blank"><img src="https://d2p67bdkbtpxn2.cloudfront.net/64ac0d2350428f01ae6611b89c7b9c187542e8cd.png" height="30"></a></td></tr></tbody></table>
</td></tr>

<tr><td style="padding-top:30px;"></td></tr>

<tr><td align="center" style="font-size:12px; color:#464646;">
Pocket FM Private Limited © 2018 - 2026
</td></tr>

<tr><td align="center" style="font-size:8px; color:#121212; padding-top:10px;">
Ref${queueId.replace(/-/g, "")}
</td></tr>

<tr><td style="padding-top:30px;"></td></tr></tbody></table>
</td></tr></tbody></table>
</td></tr></tbody></table>
</body></html>`;
}

function getBody(type, firstName, title, link, grammar, revLink, argus, showName = "") {
    switch(type) {
      case 'welcome':
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
        `;
      case 'vendor':
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
          <table border="0" cellspacing="0" cellpadding="0" style="margin-top: 10px; margin-bottom: 10px;">
            <tr>
              <td align="center" style="border-radius: 6px; background-color: #E51A4D;">
                <a href="https://drive.google.com/drive/folders/1YasA2TJL27zcyin1A-Wg-eJq9_vTQnL0" target="_blank" style="font-size: 16px; font-weight: bold; color: #ffffff; text-decoration: none; border-radius: 6px; padding: 12px 24px; border: 1px solid #E51A4D; display: inline-block;">Access Onboarding Documents</a>
              </td>
            </tr>
          </table>
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Let us know if you have any questions — happy to help.
          </td></tr>
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;
      case 'mgInitiated':
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
        `;
      case 'mgConfirmed':
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
          <table border="0" cellspacing="0" cellpadding="0" style="margin-top: 10px; margin-bottom: 10px;">
            <tr>
              <td align="center" style="border-radius: 6px; background-color: #E51A4D;">
                <a href="https://forms.gle/3nJwBt4KgnzgTThH6" target="_blank" style="font-size: 16px; font-weight: bold; color: #ffffff; text-decoration: none; border-radius: 6px; padding: 12px 24px; border: 1px solid #E51A4D; display: inline-block;">Take our quick 2-minute survey here</a>
              </td>
            </tr>
          </table>
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          If you have any questions regarding your payment or anything else along the way, simply reply to this email; we're always happy to help.
          </td></tr>
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;
      case 'checkIn1':
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
          <table border="0" cellspacing="0" cellpadding="0" style="margin-top: 10px; margin-bottom: 10px;">
            <tr>
              <td align="center" style="border-radius: 6px; background-color: #E51A4D;">
                <a href="https://forms.gle/3nJwBt4KgnzgTThH6" target="_blank" style="font-size: 16px; font-weight: bold; color: #ffffff; text-decoration: none; border-radius: 6px; padding: 12px 24px; border: 1px solid #E51A4D; display: inline-block;">Share your onboarding feedback here</a>
              </td>
            </tr>
          </table>
          </td></tr>
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;
      case 'checkIn2':
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
          <table border="0" cellspacing="0" cellpadding="0" style="margin-top: 10px; margin-bottom: 10px;">
            <tr>
              <td align="center" style="border-radius: 6px; background-color: #E51A4D;">
                <a href="https://forms.gle/3nJwBt4KgnzgTThH6" target="_blank" style="font-size: 16px; font-weight: bold; color: #ffffff; text-decoration: none; border-radius: 6px; padding: 12px 24px; border: 1px solid #E51A4D; display: inline-block;">Share your feedback here</a>
              </td>
            </tr>
          </table>
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We'll be in touch with more updates on <b>${title}</b> as production progresses.
          </td></tr>
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;
      case 'launch':
        const actualShowName = (showName && showName.toString().trim() !== "") ? showName.toString().trim() : "";
        const workDisplay = actualShowName 
          ? `<b>${title}</b> as <b>${actualShowName}</b>` 
          : `<b>${title}</b>`;
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Exciting news! Your ${grammar.work} ${workDisplay} ${grammar.is} now live on Pocket FM!
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Congratulations on reaching this milestone. Feel free to check out the show here on the app: <table border="0" cellspacing="0" cellpadding="0" style="margin-top: 10px; margin-bottom: 10px;">
            <tr>
              <td align="center" style="border-radius: 6px; background-color: #E51A4D;">
                <a href="${link}" target="_blank" style="font-size: 16px; font-weight: bold; color: #ffffff; text-decoration: none; border-radius: 6px; padding: 12px 24px; border: 1px solid #E51A4D; display: inline-block;">Listen on Pocket FM</a>
              </td>
            </tr>
          </table>
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Over the coming weeks, we'll closely track the show's performance. From listener engagement to audience feedback, and we'll keep you updated as it finds its audience.
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
        `;
      case 'launch_no_ai':
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Exciting news - your show has been picked up by our creative teams for deeper evaluation!
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Over the next few weeks, we'll be working closely to shape how the story lands, and we might come back with questions, or creative insights once this process is through.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Once the show is launched, we'll closely track how the show performs—from listener engagement to audience feedback—and we'll keep you updated as it finds its audience.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          As outlined in your agreement, you'll receive revenue statements on a quarterly basis, with a detailed breakdown of your earnings for the reporting period. If any revenue is due, you can raise an invoice against the statement for payment.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          If you have any questions in the meantime, just reply to this email.
          </td></tr>
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;
      case 'revStatement_workedWell_content':
        const revHrefContent = revLink ? revLink : "#";
        const actualRevShowName = (showName && showName.toString().trim() !== "") ? showName.toString().trim() : "";
        const appNameDisplay = actualRevShowName ? actualRevShowName : title;
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We're sharing the latest performance update for your licensed series, <b>${title}</b>, on Pocket FM. (Pocket FM App Name: <b>${appNameDisplay}</b>) Attached, you'll find your revenue statement for this quarter, which provides a breakdown of your earnings for the reporting period, along with a snapshot of how your show has been performing.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <b>Show Snapshot</b><br>
          • Duration Produced: ${argus.duration}<br>
          • Plays / Daily Active Listeners (LDAUs): ${argus.ldau}<br>
          • Comments: ${argus.comments}<br>
          • Ratings: ${argus.ratings}<br>
          • Reviews: ${argus.reviews}
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We'll continue to keep you updated as your show reaches more listeners and share new milestones along the way.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <table border="0" cellspacing="0" cellpadding="0" style="margin-top: 10px; margin-bottom: 10px;">
            <tr>
              <td align="center" style="border-radius: 6px; background-color: #E51A4D;">
                <a href="${revHrefContent}" target="_blank" style="font-size: 16px; font-weight: bold; color: #ffffff; text-decoration: none; border-radius: 6px; padding: 12px 24px; border: 1px solid #E51A4D; display: inline-block;">Access Revenue Statement</a>
              </td>
            </tr>
          </table>
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          If your latest revenue statement reflects an amount payable, we'll send you a separate email with the invoice format and instructions to help you raise your invoice.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          If the statement shows no amount payable (for example, while your Minimum Guarantee is still being recouped), no further action is required from your end, and we won't be sending an invoice request for that period.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          If you have any questions about your show's performance or production, simply reply to this email—we're always happy to help.
          </td></tr>
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;
      case 'revStatement_workedWell_payment':
        const revHrefPay = revLink ? revLink : "#";
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We're excited to share the latest performance update for <b>${title}</b> on Pocket FM. Attached, you'll find your revenue statement for this quarter, which provides a detailed breakdown of your earnings for the reporting period, along with a snapshot of how your show has been performing on the platform.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <b>Invoice template for the Revenue share payment</b><br>
          Please share an invoice for the due amount for us to process the payout. The invoice must include the following details:
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
              <tr><td><b>Product / Service Description</b></td><td>Mandatory</td><td>Clear description of the product or service (Mention duration for which revenue statement is valid)</td></tr>
              <tr><td><b>Service Period</b></td><td>Mandatory</td><td>Should match the term specified in the agreement</td></tr>
              <tr><td><b>Amount</b></td><td>Mandatory</td><td>Clear bifurcation of base amount and VAT (if applicable)</td></tr>
              <tr><td><b>Bank Details</b></td><td>Mandatory</td><td>Beneficiary name, account number / IBAN, SWIFT code, routing number (mandatory for US vendors), local transit number, and bank name</td></tr>
              <tr><td><b>Signature</b></td><td>Mandatory</td><td>Digital or wet signature</td></tr>
            </table>
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          If you have any questions about the attached revenue statement or your show's performance, simply reply to this email - we're happy to help.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Click here to check your revenue statement: <br>
          <table border="0" cellspacing="0" cellpadding="0" style="margin-top: 10px; margin-bottom: 10px;">
            <tr>
              <td align="center" style="border-radius: 6px; background-color: #E51A4D;">
                <a href="${revHrefPay}" target="_blank" style="font-size: 16px; font-weight: bold; color: #ffffff; text-decoration: none; border-radius: 6px; padding: 12px 24px; border: 1px solid #E51A4D; display: inline-block;">Access Revenue Statements</a>
              </td>
            </tr>
          </table>
          </td></tr>
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;
      case 'revStatement_didntWorkWell':
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
          • Duration Produced: ${argus.duration}<br>
          • Plays / Daily Active Listeners (LDAUs): ${argus.ldau}<br>
          • Comments: ${argus.comments}<br>
          • Ratings: ${argus.ratings}<br>
          • Reviews: ${argus.reviews}
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
          <table border="0" cellspacing="0" cellpadding="0" style="margin-top: 10px; margin-bottom: 10px;">
            <tr>
              <td align="center" style="border-radius: 6px; background-color: #E51A4D;">
                <a href="${revHrefDidntWork}" target="_blank" style="font-size: 16px; font-weight: bold; color: #ffffff; text-decoration: none; border-radius: 6px; padding: 12px 24px; border: 1px solid #E51A4D; display: inline-block;">Access Revenue Statements</a>
              </td>
            </tr>
          </table>
          </td></tr>
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;

      case 'quarterlyStatements':
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We hope you're doing well! It's time for the quarterly update for <b>${title}</b>. Attached, you'll find your revenue statement, which includes a detailed breakdown of your earnings for the reporting period, along with a snapshot of how your show has been performing on Pocket FM.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <b>Show Snapshot</b><br>
          • Listening Hours: ${argus.hours}<br>
          • Daily Active Listeners (LDAUs): ${argus.ldau}<br>
          • Duration Produced: ${argus.duration}<br>
          • Comments: ${argus.comments}
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
          <table border="0" cellspacing="0" cellpadding="0" style="margin-top: 10px; margin-bottom: 10px;">
            <tr>
              <td align="center" style="border-radius: 6px; background-color: #E51A4D;">
                <a href="[Insert RSVP Link]" target="_blank" style="font-size: 16px; font-weight: bold; color: #ffffff; text-decoration: none; border-radius: 6px; padding: 12px 24px; border: 1px solid #E51A4D; display: inline-block;">RSVP Here</a>
              </td>
            </tr>
          </table>
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

      case 'authorEdit':
      case 'newsletter':
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We wanted to keep you in the loop with a few things happening across Pocket FM: from what listeners are responding to, to what we're learning about stories that work particularly well in audio.
          </td></tr>

          <!-- Section 1: What's Happening -->
          <tr><td align="left" style="font-size:17px; font-weight:700; color:#E51A4D; padding:20px 35px 5px; line-height:24px; text-transform:uppercase; letter-spacing:0.5px;">
          1. WHAT'S HAPPENING AT POCKET FM
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:5px 35px 10px; line-height:24px;">
          We had the absolute honour of having the legendary Ruskin Bond spend time exploring Sherpa and share his experience with us. For someone who has spent a lifetime telling stories and inspired generations of people to read, imagine and write, experiencing something we have built is incredibly special.
          </td></tr>
          <tr><td align="left" style="padding:5px 35px 15px;">
            <table border="0" cellspacing="0" cellpadding="0">
              <tr>
                <td align="center" style="border-radius: 6px; background-color: #E51A4D;">
                  <a href="https://lnkd.in/p/g6rd7Zta" target="_blank" style="font-size: 14px; font-weight: bold; color: #ffffff; text-decoration: none; border-radius: 6px; padding: 10px 20px; border: 1px solid #E51A4D; display: inline-block;">See What's New →</a>
                </td>
              </tr>
            </table>
          </td></tr>

          <!-- Section 2: A Story Worth Knowing -->
          <tr><td align="left" style="font-size:17px; font-weight:700; color:#E51A4D; padding:20px 35px 5px; line-height:24px; text-transform:uppercase; letter-spacing:0.5px;">
          2. A STORY WORTH KNOWING
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:5px 35px 10px; line-height:24px;">
          <b>Meet Steven Ade: the writer who kept writing even when writing didn't look like a career.</b><br>
          For years, Steven worked jobs that paid the bills—supporting children on the spectrum and delivering pizzas—all while carrying a love for storytelling. When he began publishing on Pocket FM, his audience took off. Today, Steven is the writer behind <i>The System Creation: Intergalactic Entry</i>, which has reached nearly <b>8 million plays</b> with a <b>4.6-star rating</b>!
          </td></tr>
          <tr><td align="left" style="padding:5px 35px 15px;">
            <table border="0" cellspacing="0" cellpadding="0">
              <tr>
                <td align="center" style="border-radius: 6px; background-color: #121212;">
                  <a href="https://youtu.be/IO2XWbTNafY?si=dOzc2ZTD0IxZSQpk" target="_blank" style="font-size: 14px; font-weight: bold; color: #ffffff; text-decoration: none; border-radius: 6px; padding: 10px 20px; border: 1px solid #121212; display: inline-block;">Watch Steven's Story →</a>
                </td>
              </tr>
            </table>
          </td></tr>

          <!-- Section 3: What We're Seeing From Listeners -->
          <tr><td align="left" style="font-size:17px; font-weight:700; color:#E51A4D; padding:20px 35px 5px; line-height:24px; text-transform:uppercase; letter-spacing:0.5px;">
          3. WHAT WE'RE SEEING FROM LISTENERS
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:5px 35px 5px; line-height:24px;">
          <b>Genre in Spotlight: Romantasy in Audio</b><br>
          Across Romantasy titles, three storytelling patterns consistently drive higher listener engagement:
          <ol style="margin: 8px 0; padding-left: 20px; line-height: 24px;">
            <li><b>Romance built on choice, not just chemistry:</b> Shared vulnerability and earned trust keep listeners invested beyond instinctual attraction.</li>
            <li><b>Protagonists with goals beyond romance:</b> Active agency, survival stakes, and independent ambitions make character arcs compelling.</li>
            <li><b>Fantasy worlds that pressure the relationship:</b> Magic rules and political conflict create obstacles specific to that world.</li>
          </ol>
          </td></tr>

          <!-- Section 4: Before You Go -->
          <tr><td align="left" style="font-size:17px; font-weight:700; color:#E51A4D; padding:20px 35px 5px; line-height:24px; text-transform:uppercase; letter-spacing:0.5px;">
          4. BEFORE YOU GO
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:5px 35px 10px; line-height:24px;">
          Working on something new? We'd love to hear about it.
          </td></tr>
          <tr><td align="left" style="padding:5px 35px 20px;">
            <table border="0" cellspacing="0" cellpadding="0">
              <tr>
                <td align="center" style="border-radius: 6px; background-color: #E51A4D;">
                  <a href="mailto:us-licensing@pocketfm.com?subject=Story%20Pitch" target="_blank" style="font-size: 14px; font-weight: bold; color: #ffffff; text-decoration: none; border-radius: 6px; padding: 10px 20px; border: 1px solid #E51A4D; display: inline-block;">Share a Story →</a>
                </td>
              </tr>
            </table>
          </td></tr>

          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Until next time,<br>
          Team Pocket FM
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
          <table border="0" cellspacing="0" cellpadding="0" style="margin-top: 10px; margin-bottom: 10px;">
            <tr>
              <td align="center" style="border-radius: 6px; background-color: #E51A4D;">
                <a href="[Insert Article Link]" target="_blank" style="font-size: 16px; font-weight: bold; color: #ffffff; text-decoration: none; border-radius: 6px; padding: 12px 24px; border: 1px solid #E51A4D; display: inline-block;">Read More</a>
              </td>
            </tr>
          </table>
          </td></tr>
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;

      default:
        Logger.log(`[RECOMMENDED NOTIFICATION] Email template not selected: No template definition found for stage type '${type}' (Title: '${title}').`);
        return "";
    }
  }
