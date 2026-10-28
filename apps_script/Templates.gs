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
    if (bodyContent && (bodyContent.includes("<!-- POCKET_EDIT_NEWSLETTER -->") || bodyContent.trim().startsWith("<!DOCTYPE html"))) {
        return bodyContent.replace("{{QUEUE_ID}}", queueId ? `Ref${queueId.replace(/-/g, "")}` : "");
    }
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
          • Plays: ${argus.plays || argus.ldau}<br>
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
      case 'contentBad':
      case 'revStatement_didntWorkWell':
        const revHrefDidntWork = revLink ? revLink : "#";
        const durRaw = (argus && argus.duration) ? argus.duration.toString().trim() : "";
        const durText = (durRaw && durRaw !== "N/A")
          ? (durRaw.toLowerCase().includes("hour") ? durRaw : `${durRaw} hours`)
          : "N/A";
        const playsRaw = (argus && (argus.plays || argus.ldau)) ? (argus.plays || argus.ldau).toString().trim() : "";
        const playsText = (playsRaw && playsRaw !== "N/A")
          ? (playsRaw.toLowerCase().includes("play") ? playsRaw : `${playsRaw} plays`)
          : "N/A";
        const commentsText = (argus && argus.comments && argus.comments.toString().trim() !== "")
          ? argus.comments.toString().trim()
          : "No comments";
        const ratingsText = (argus && argus.ratings && argus.ratings.toString().trim() !== "")
          ? argus.ratings.toString().trim()
          : "No ratings";
        const reviewsText = (argus && argus.reviews && argus.reviews.toString().trim() !== "")
          ? argus.reviews.toString().trim()
          : "No reviews";

        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          ${firstName ? `Hi ${firstName},` : `Hi,`}
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We're sharing the latest performance update for <b>${title}</b> on Pocket FM. Attached, you'll find your <b>revenue statement for this quarter</b>, which provides a breakdown of your earnings for the reporting period, along with a snapshot of how your show has been performing.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <b>Show Snapshot</b>
          <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-top: 8px; margin-bottom: 8px;">
            <tr><td style="border-top: 1px solid #d3d3d3; padding-top: 8px;"></td></tr>
            <tr>
              <td style="font-size:15px; color:#121212; line-height:26px; padding-left: 15px;">
                • &nbsp;<b>Duration Produced:</b> ${durText}<br>
                • &nbsp;<b>Plays:</b> ${playsText}<br>
                • &nbsp;<b>Comments:</b> ${commentsText}<br>
                • &nbsp;<b>Ratings:</b> ${ratingsText}<br>
                • &nbsp;<b>Reviews:</b> ${reviewsText}
              </td>
            </tr>
            <tr><td style="border-bottom: 1px solid #d3d3d3; padding-bottom: 8px;"></td></tr>
          </table>
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          As part of our content evaluation process, we initially tested <b>${title}</b> with a small group of listeners to understand audience engagement and response. Based on the feedback and performance observed during this testing phase, along with our internal benchmarks, we've decided not to move forward with producing additional episodes at this time.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          This decision is based solely on the show's performance with the test audience and does not take away from the value of your story. We truly appreciate the opportunity to bring your work to Pocket FM and will continue sharing quarterly revenue statements for the episodes already available on the platform.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          If you have any questions about your revenue statement or your show's performance, simply reply to this email; we're always happy to help.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <b>Click here to view your revenue statement:</b> ${revLink && revLink !== '#' ? `<a href="${revHrefDidntWork}" target="_blank" style="color: #1a73e8; text-decoration: underline; word-break: break-all;">${revLink}</a>` : `<span style="color: #666666;">{{Revenue Statement Drive}}</span>`}
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          <b>US Licensing & Commissioning Team</b><br>
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
          • Plays: ${argus.plays || argus.ldau}<br>
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
        return `<!DOCTYPE html><!-- POCKET_EDIT_NEWSLETTER -->
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width,initial-scale=1" name="viewport"/>
<meta content="light only" name="color-scheme"/>
<title>The Pocket Edit | Pocket FM Creator Newsletter</title>
<style>
*{box-sizing:border-box}
body{margin:0;padding:0;background-color:#e9e5df;color:#191919;font-family:Arial,Helvetica,sans-serif;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;}
table{border-collapse:separate;}
a{color:#c51d47;text-decoration:none;}
p{font-size:13px;line-height:1.58;margin:10px 0;color:#191919;}
@media only screen and (max-width: 700px) {
  .page-padding { padding: 20px 16px !important; }
  .brand-h1 { font-size: 34px !important; line-height: 1.05 !important; }
  .listener-h1 { font-size: 30px !important; line-height: 1.05 !important; }
}
</style>
</head>
<body style="margin:0;padding:0;background-color:#e9e5df;color:#191919;font-family:Arial,Helvetica,sans-serif;">

<table border="0" cellpadding="0" cellspacing="0" width="100%" bgcolor="#e9e5df" style="background-color:#e9e5df;margin:0;padding:24px 0;width:100%;">
  <tr>
    <td align="center" bgcolor="#e9e5df" style="background-color:#e9e5df;padding:0 8px;">

      <!-- CONTAINER TABLE (Up to 1380px for side-by-side spread on wide screens, stacked on email) -->
      <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width:1380px;margin:0 auto;">
        <tr>
          <td align="center" style="font-size:0;text-align:center;padding:0;">

            <!--[if mso]>
            <table border="0" cellpadding="0" cellspacing="0" width="100%"><tr><td width="50%" valign="top" style="padding:0 6px;">
            <![endif]-->

            <!-- ======================================================== -->
            <!-- PAGE 1 COLUMN -->
            <!-- ======================================================== -->
            <div class="page-col" style="display:inline-block;width:100%;max-width:670px;vertical-align:top;text-align:left;margin:0 6px 20px 6px;">
              <table border="0" cellpadding="0" cellspacing="0" width="100%" bgcolor="#fffefa" style="background-color:#fffefa;border-top:6px solid #e51a4d;border-radius:6px;box-shadow:0 8px 28px rgba(0,0,0,0.08);width:100%;">
                <tr>
                  <td class="page-padding" bgcolor="#fffefa" style="padding:30px 34px;background-color:#fffefa;border-radius:6px;vertical-align:top;">

                    <!-- ISSUE HEADER -->
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="border-bottom:1px solid #dddddd;padding-bottom:12px;margin-bottom:18px;">
                      <tr>
                        <td align="left" style="font-size:9px;letter-spacing:1.1px;font-weight:700;color:#59504e;text-transform:uppercase;font-family:Arial,sans-serif;">
                          THE POCKET EDIT &nbsp;/&nbsp; CREATOR NEWSLETTER
                        </td>
                        <td align="right" style="font-size:9px;letter-spacing:1.1px;font-weight:700;color:#59504e;text-transform:uppercase;font-family:Arial,sans-serif;">
                          ISSUE 01 · OCT 2026
                        </td>
                      </tr>
                    </table>

                    <!-- BRAND HERO BANNER -->
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" bgcolor="#171717" style="background-color:#171717;color:#ffffff;margin-bottom:20px;border-radius:4px;overflow:hidden;">
                      <tr>
                        <td bgcolor="#171717" style="padding:0;background-color:#171717;">
                          <img src="https://d2p67bdkbtpxn2.cloudfront.net/c8b7ada83f09146d4b2c2ba3a5c3c1b8ea36e459.jpg" alt="Pocket FM" width="100%" style="display:block;width:100%;max-height:115px;object-fit:cover;border:0;" />
                        </td>
                      </tr>
                      <tr>
                        <td bgcolor="#171717" style="padding:22px 26px 24px;background-color:#171717;">
                          <table border="0" cellpadding="0" cellspacing="0" width="100%">
                            <tr>
                              <td valign="top">
                                <div style="font-size:10px;font-weight:800;letter-spacing:2px;color:#ff7b9e;text-transform:uppercase;font-family:Arial,sans-serif;">THE POCKET EDIT</div>
                                <h1 class="brand-h1" style="font-family:Georgia,serif;font-size:44px;line-height:0.98;letter-spacing:-1.5px;margin:12px 0;color:#ffffff;font-weight:normal;">Stories worth<br/><em style="color:#f44e79;font-style:italic;">sharing.</em></h1>
                                <div style="font-size:13px;color:#e9e9e9;line-height:1.5;font-family:Arial,sans-serif;">What’s new at Pocket FM + a few things worth knowing</div>
                              </td>
                              <td align="right" valign="bottom" style="font-size:28px;color:#ffbb56;padding-bottom:6px;font-family:Georgia,serif;">✳</td>
                            </tr>
                          </table>
                        </td>
                      </tr>
                    </table>

                    <!-- GREETING / INTRO BOX -->
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" bgcolor="#fff0f3" style="background-color:#fff0f3;border-left:4px solid #e51a4d;border-radius:0 6px 6px 0;margin:16px 0 22px;">
                      <tr>
                        <td bgcolor="#fff0f3" style="padding:16px 18px;font-size:13px;line-height:1.6;color:#191919;background-color:#fff0f3;font-family:Arial,sans-serif;">
                          Hi <strong>${firstName || "Author"}</strong>,<br/><br/>
                          We wanted to keep you in the loop with a few things happening across Pocket FM: from what listeners are responding to, to what we’re learning about stories that work particularly well in audio.
                        </td>
                      </tr>
                    </table>

                    <!-- SECTION 01: WHAT'S HAPPENING AT POCKET FM -->
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="border-top:2px solid #171717;margin-top:24px;padding-top:12px;margin-bottom:10px;">
                      <tr>
                        <td width="34" valign="middle">
                          <div style="background-color:#e51a4d;color:#ffffff;border-radius:7px;width:25px;height:25px;line-height:25px;text-align:center;font-size:10px;font-weight:900;font-family:Arial,sans-serif;">01</div>
                        </td>
                        <td valign="middle" style="font-size:10px;font-weight:800;letter-spacing:1.2px;color:#191919;font-family:Arial,sans-serif;text-transform:uppercase;">
                          WHAT’S HAPPENING AT POCKET FM
                        </td>
                        <td align="right" valign="middle" style="font-size:18px;color:#e51a4d;">✦</td>
                      </tr>
                    </table>

                    <h2 style="font-family:Georgia,serif;font-size:26px;line-height:1.12;margin:10px 0 12px;letter-spacing:-0.5px;color:#191919;font-weight:normal;">A legendary storyteller meets Sherpa</h2>
                    <div style="color:#c5224e;font-size:10px;letter-spacing:1.2px;font-weight:800;text-transform:uppercase;margin-bottom:10px;font-family:Arial,sans-serif;">THE BIG MOMENT <span style="font-size:15px;">✦</span></div>

                    <p style="font-size:13px;line-height:1.58;color:#191919;margin:10px 0;font-family:Arial,sans-serif;"><strong>We had the absolute honour of having the legendary Ruskin Bond spend time exploring Sherpa and share his experience with us.</strong></p>
                    <p style="font-size:13px;line-height:1.58;color:#191919;margin:10px 0;font-family:Arial,sans-serif;">For someone who has spent a lifetime telling stories and inspired generations of people to read, imagine and write, experiencing something we have built is incredibly special. This is a proud moment for everyone who has worked on Sherpa across product, engineering, content, design, marketing and so many other teams.</p>
                    <p style="font-size:13px;line-height:1.58;color:#191919;margin:10px 0;font-family:Arial,sans-serif;">Thank you, Mr. Bond. Truly an honour for all of us at Pocket FM.</p>

                    <!-- LINK PANEL (DO WATCH & SHARE) -->
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" bgcolor="#f5eafa" style="background-color:#f5eafa;border:1px solid #e6d5ef;border-radius:8px;margin:16px 0 22px;">
                      <tr>
                        <td bgcolor="#f5eafa" style="padding:14px 16px;background-color:#f5eafa;border-radius:8px;">
                          <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom:10px;">
                            <tr>
                              <td align="left" style="font-size:10px;letter-spacing:1px;font-weight:800;color:#191919;font-family:Arial,sans-serif;text-transform:uppercase;">DO WATCH &amp; SHARE</td>
                              <td align="right" style="font-size:12px;font-weight:800;color:#191919;">↗</td>
                            </tr>
                          </table>
                          <div>
                            <a href="https://lnkd.in/p/g6rd7Zta" target="_blank" style="background-color:#ffffff;border:1px solid #decde9;padding:6px 12px;font-size:11px;border-radius:20px;color:#c51d47;font-weight:bold;text-decoration:none;display:inline-block;margin-right:6px;margin-bottom:6px;font-family:Arial,sans-serif;">Founder’s LinkedIn post ↗</a>
                            <a href="https://www.instagram.com/reel/Dd0vnVwqoML/?stkn=dG1jcTd4YWM3czBu" target="_blank" style="background-color:#ffffff;border:1px solid #decde9;padding:6px 12px;font-size:11px;border-radius:20px;color:#c51d47;font-weight:bold;text-decoration:none;display:inline-block;margin-right:6px;margin-bottom:6px;font-family:Arial,sans-serif;">▶ Instagram Reel</a>
                            <a href="https://youtube.com/shorts/1IpKrpoAoWs?si=MjKK00iT4JaICsvJ" target="_blank" style="background-color:#ffffff;border:1px solid #decde9;padding:6px 12px;font-size:11px;border-radius:20px;color:#c51d47;font-weight:bold;text-decoration:none;display:inline-block;margin-bottom:6px;font-family:Arial,sans-serif;">▶ YouTube Short</a>
                          </div>
                        </td>
                      </tr>
                    </table>

                    <!-- SECTION 02: A STORY WORTH KNOWING -->
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="border-top:2px solid #171717;margin-top:24px;padding-top:12px;margin-bottom:10px;">
                      <tr>
                        <td width="34" valign="middle">
                          <div style="background-color:#e51a4d;color:#ffffff;border-radius:7px;width:25px;height:25px;line-height:25px;text-align:center;font-size:10px;font-weight:900;font-family:Arial,sans-serif;">02</div>
                        </td>
                        <td valign="middle" style="font-size:10px;font-weight:800;letter-spacing:1.2px;color:#191919;font-family:Arial,sans-serif;text-transform:uppercase;">
                          A STORY WORTH KNOWING
                        </td>
                        <td align="right" valign="middle" style="font-size:18px;color:#e51a4d;">✦</td>
                      </tr>
                    </table>

                    <div style="display:inline-block;font-size:10px;font-weight:800;letter-spacing:.6px;padding:5px 9px;border:1px dashed #b57e9a;border-radius:3px;color:#8f4668;background-color:#fff8fa;margin:3px 0 7px;font-family:Arial,sans-serif;">✎ CREATOR NOTEBOOK</div>
                    <h2 style="font-family:Georgia,serif;font-size:26px;line-height:1.12;margin:6px 0 6px;letter-spacing:-0.5px;color:#191919;font-weight:normal;">Meet Steven Ade</h2>
                    <div style="font-size:15px;line-height:1.3;font-family:Georgia,serif;font-style:italic;color:#555555;margin-bottom:12px;">The writer who kept writing even when writing didn’t look like a career.</div>

                    <p style="font-size:13px;line-height:1.58;color:#191919;margin:10px 0;font-family:Arial,sans-serif;">For years, Steven’s creative life existed alongside the jobs that paid the bills. He worked in a youth facility, supported children on the spectrum, and later delivered pizzas - all while carrying a love for storytelling that went back to his school days.</p>
                    <p style="font-size:13px;line-height:1.58;color:#191919;margin:10px 0;font-family:Arial,sans-serif;">He had once been told that writing wasn’t a practical career. But when he began publishing on Pocket FM, the audience for his stories started growing. What began alongside his day job eventually became the work he could do full-time.</p>
                    <p style="font-size:13px;line-height:1.58;color:#191919;margin:10px 0;font-family:Arial,sans-serif;">Today, Steven is the writer behind <em>The System Creation: Intergalactic Entry</em>, which has reached nearly <strong>8 million plays, holds a 4.6-star rating</strong>, and has received over a thousand reviews on Pocket FM.</p>

                    <!-- MILESTONE BOX -->
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" bgcolor="#fff1e6" style="background-color:#fff1e6;border-left:4px solid #ef9d4e;border-radius:0 9px 9px 0;margin:14px 0;">
                      <tr>
                        <td bgcolor="#fff1e6" style="padding:14px 16px;background-color:#fff1e6;border-radius:0 9px 9px 0;">
                          <table border="0" cellpadding="0" cellspacing="0">
                            <tr>
                              <td valign="middle" style="padding-right:12px;">
                                <div style="border-radius:50%;background-color:#e51a4d;color:#ffffff;width:30px;height:30px;line-height:30px;text-align:center;font-size:11px;font-weight:bold;">▶</div>
                              </td>
                              <td valign="middle">
                                <strong style="font-size:15px;color:#191919;font-family:Arial,sans-serif;display:block;">Nearly 8 million plays</strong>
                                <small style="font-size:11px;color:#5d5255;margin-top:2px;display:block;font-family:Arial,sans-serif;">★ 4.6 rating &nbsp;·&nbsp; 1,000+ reviews</small>
                              </td>
                            </tr>
                          </table>
                        </td>
                      </tr>
                    </table>

                    <p style="font-size:13px;line-height:1.58;color:#191919;margin:10px 0;font-family:Arial,sans-serif;"><strong>For any author who has ever had to fit writing around work, responsibilities, or doubts about whether it could become something more, Steven’s journey may feel familiar.</strong></p>

                    <!-- CTA BUTTONS -->
                    <table border="0" cellpadding="0" cellspacing="0" style="margin:16px 0 20px;">
                      <tr>
                        <td style="padding-right:10px;">
                          <table border="0" cellpadding="0" cellspacing="0">
                            <tr>
                              <td align="center" bgcolor="#e51a4d" style="border-radius:20px;background-color:#e51a4d;">
                                <a href="https://youtu.be/IO2XWbTNafY?si=dOzc2ZTD0IxZSQpk" target="_blank" style="font-size:12px;font-weight:800;color:#ffffff;text-decoration:none;padding:10px 18px;border-radius:20px;display:inline-block;font-family:Arial,sans-serif;">▶ Watch Steven’s Story</a>
                              </td>
                            </tr>
                          </table>
                        </td>
                        <td>
                          <table border="0" cellpadding="0" cellspacing="0">
                            <tr>
                              <td align="center" bgcolor="#34283b" style="border-radius:20px;background-color:#34283b;">
                                <a href="https://pocketfm.com/show/a6268ee1800866a09bab6b47c61f885556992b45" target="_blank" style="font-size:12px;font-weight:800;color:#ffffff;text-decoration:none;padding:10px 18px;border-radius:20px;display:inline-block;font-family:Arial,sans-serif;">Explore the show ↗</a>
                              </td>
                            </tr>
                          </table>
                        </td>
                      </tr>
                    </table>

                    <!-- PAGE 1 FOOTER -->
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-top:32px;border-top:1px solid #bbbbbb;padding-top:8px;">
                      <tr>
                        <td align="left" style="font-size:9px;letter-spacing:1.3px;color:#888888;font-weight:800;font-family:Arial,sans-serif;">POCKET FM</td>
                        <td align="right" style="font-size:9px;letter-spacing:1.3px;color:#888888;font-weight:800;font-family:Arial,sans-serif;">01 / 02</td>
                      </tr>
                    </table>

                  </td>
                </tr>
              </table>
            </div>

            <!--[if mso]>
            </td><td width="50%" valign="top" style="padding:0 6px;">
            <![endif]-->

            <!-- ======================================================== -->
            <!-- PAGE 2 COLUMN (WITH 100% INLINED MINT, PEACH & LAVENDER CARDS) -->
            <!-- ======================================================== -->
            <div class="page-col" style="display:inline-block;width:100%;max-width:670px;vertical-align:top;text-align:left;margin:0 6px 20px 6px;">
              <table border="0" cellpadding="0" cellspacing="0" width="100%" bgcolor="#fffefa" style="background-color:#fffefa;border-top:6px solid #252525;border-radius:6px;box-shadow:0 8px 28px rgba(0,0,0,0.08);width:100%;">
                <tr>
                  <td class="page-padding" bgcolor="#fffefa" style="padding:30px 34px;background-color:#fffefa;border-radius:6px;vertical-align:top;">

                    <!-- ISSUE HEADER -->
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="border-bottom:1px solid #dddddd;padding-bottom:12px;margin-bottom:18px;">
                      <tr>
                        <td align="left" style="font-size:9px;letter-spacing:1.1px;font-weight:700;color:#59504e;text-transform:uppercase;font-family:Arial,sans-serif;">
                          THE POCKET EDIT &nbsp;/&nbsp; STORYTELLING NOTES
                        </td>
                        <td align="right" style="font-size:9px;letter-spacing:1.1px;font-weight:700;color:#59504e;text-transform:uppercase;font-family:Arial,sans-serif;">
                          ISSUE 01 · OCT 2026
                        </td>
                      </tr>
                    </table>

                    <!-- PAGE TWO HEADER BANNER -->
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" bgcolor="#251e2b" style="background-color:#251e2b;color:#ffffff;margin-bottom:20px;border-radius:4px;overflow:hidden;">
                      <tr>
                        <td bgcolor="#251e2b" style="padding:26px 28px;background-color:#251e2b;">
                          <table border="0" cellpadding="0" cellspacing="0" width="100%">
                            <tr>
                              <td valign="top">
                                <div style="font-size:10px;font-weight:800;letter-spacing:2px;color:#ff7b9e;text-transform:uppercase;font-family:Arial,sans-serif;">THE LISTENER EDIT</div>
                                <h1 class="listener-h1" style="font-family:Georgia,serif;font-size:39px;line-height:0.98;letter-spacing:-1.5px;margin:12px 0;color:#ffffff;font-weight:normal;">Romance.<br/>Magic. <em style="color:#f44e79;font-style:italic;">Momentum.</em></h1>
                                <div style="font-size:12px;color:#f0f0f0;font-family:Arial,sans-serif;">Genre in Spotlight: Romantasy</div>
                              </td>
                              <td align="right" valign="top" style="font-size:32px;color:#f7bd68;padding-top:4px;font-family:Georgia,serif;">✧</td>
                            </tr>
                          </table>
                        </td>
                      </tr>
                    </table>

                    <!-- SECTION 03: WHAT WE'RE SEEING FROM LISTENERS -->
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="border-top:2px solid #171717;margin-top:24px;padding-top:12px;margin-bottom:10px;">
                      <tr>
                        <td width="34" valign="middle">
                          <div style="background-color:#e51a4d;color:#ffffff;border-radius:7px;width:25px;height:25px;line-height:25px;text-align:center;font-size:10px;font-weight:900;font-family:Arial,sans-serif;">03</div>
                        </td>
                        <td valign="middle" style="font-size:10px;font-weight:800;letter-spacing:1.2px;color:#191919;font-family:Arial,sans-serif;text-transform:uppercase;">
                          WHAT WE’RE SEEING FROM LISTENERS
                        </td>
                        <td align="right" valign="middle" style="font-size:18px;color:#e51a4d;">✦</td>
                      </tr>
                    </table>

                    <div style="display:inline-block;font-size:10px;font-weight:800;letter-spacing:.6px;padding:5px 9px;border:1px dashed #b57e9a;border-radius:3px;color:#8f4668;background-color:#fff8fa;margin:3px 0 7px;font-family:Arial,sans-serif;">✧ THE AUDIO STORYTELLING PLAYBOOK</div>
                    <h2 style="font-family:Georgia,serif;font-size:26px;line-height:1.12;margin:6px 0 10px;letter-spacing:-.5px;color:#191919;font-weight:normal;">What makes Romantasy stronger in audio?</h2>
                    <p style="font-size:13px;line-height:1.58;color:#191919;margin:8px 0 14px;font-family:Arial,sans-serif;">Across the Romantasy titles we’ve been reviewing, a few patterns come up repeatedly:</p>

                    <!-- ============================================== -->
                    <!-- TIP 01: CHOICE OVER CHEMISTRY (PURPLE / LAVENDER CARD) -->
                    <!-- ============================================== -->
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="border-top:1px dashed #cfc9c2;padding-top:14px;margin-top:14px;">
                      <tr>
                        <td width="42" valign="top">
                          <span style="font-family:Georgia,serif;color:#9c61b8;font-size:28px;line-height:1;font-weight:bold;display:block;">01</span>
                        </td>
                        <td valign="top">
                          <h3 style="font-family:Georgia,serif;font-size:19px;line-height:1.2;margin:0;color:#191919;display:inline;font-weight:bold;">Let the romance build through choice, not just chemistry.</h3>
                          <span style="font-family:Georgia,serif;font-weight:bold;display:inline-block;color:#b34f7d;font-size:16px;margin-left:6px;">♡</span>
                        </td>
                      </tr>
                    </table>
                    <p style="font-size:13px;line-height:1.58;color:#191919;margin:10px 0;font-family:Arial,sans-serif;">Supernatural bonds, instant attraction, and physical pull can create intrigue, but they shouldn’t do all the emotional work. Give the leads shared experiences, moments of vulnerability, conflict, and trust-building so the relationship feels earned rather than predetermined.</p>

                    <!-- CARD 1: LAVENDER (#f0ecfa) WITH PURPLE BORDER (#9c78c8) -->
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" bgcolor="#f0ecfa" style="background-color:#f0ecfa;border-left:4px solid #9c78c8;border-radius:0 9px 9px 0;margin:14px 0;">
                      <tr>
                        <td bgcolor="#f0ecfa" style="padding:14px 18px;background-color:#f0ecfa;border-radius:0 9px 9px 0;">
                          <div style="font-size:10px;color:#7a4d8f;letter-spacing:1.2px;font-weight:800;text-transform:uppercase;margin-bottom:6px;font-family:Arial,sans-serif;">✦ SEE IT IN ACTION</div>
                          <strong style="font-size:15px;color:#191919;font-family:Arial,sans-serif;display:block;margin-bottom:6px;">The Alpha She Chose</strong>
                          <p style="font-size:13px;line-height:1.55;color:#191919;margin:6px 0 10px;font-family:Arial,sans-serif;">What makes this premise interesting is the emphasis on <strong>choice rather than predestination</strong>. In a genre where fated-mate bonds can bring two characters together automatically, the heroine’s decision becomes part of the relationship itself. The supernatural connection may create the pull, but choosing what to do with that connection gives the romance its emotional stakes.</p>
                          <a href="https://pocketfm.com/show/the-alpha-she-chose/69e2eb3772b49e749fed57ae96a86147dde154cb" target="_blank" style="font-size:13px;font-weight:bold;color:#c51d47;text-decoration:none;display:inline-block;font-family:Arial,sans-serif;">▶ Explore The Alpha She Chose</a>
                        </td>
                      </tr>
                    </table>

                    <!-- ============================================== -->
                    <!-- TIP 02: GOAL BEYOND RELATIONSHIP (EXACTLY MATCHING IMAGE 2!) -->
                    <!-- ============================================== -->
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="border-top:1px dashed #cfc9c2;padding-top:16px;margin-top:16px;">
                      <tr>
                        <td width="42" valign="top">
                          <span style="font-family:Georgia,serif;color:#e51a4d;font-size:28px;line-height:1;font-weight:bold;display:block;">02</span>
                        </td>
                        <td valign="top">
                          <h3 style="font-family:Georgia,serif;font-size:19px;line-height:1.2;margin:0;color:#191919;display:inline;font-weight:bold;">Give the protagonist a goal beyond the relationship.</h3>
                          <span style="font-family:Georgia,serif;font-weight:bold;display:inline-block;color:#66a28a;font-size:18px;margin-left:6px;">✳</span>
                        </td>
                      </tr>
                    </table>
                    <p style="font-size:13px;line-height:1.58;color:#191919;margin:10px 0;font-family:Arial,sans-serif;">A strong Romantasy lead should actively shape the plot. Give her something she wants, investigate, protect, or fight for outside the romance, so the love story complicates her journey rather than becoming the whole journey.</p>

                    <!-- CARD 2: MINT GREEN (#eaf4ef) WITH FOREST GREEN BORDER (#66a28a) -->
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" bgcolor="#eaf4ef" style="background-color:#eaf4ef;border-left:4px solid #66a28a;border-radius:0 9px 9px 0;margin:14px 0;">
                      <tr>
                        <td bgcolor="#eaf4ef" style="padding:14px 18px;background-color:#eaf4ef;border-radius:0 9px 9px 0;">
                          <div style="font-size:10px;color:#437d68;letter-spacing:1.2px;font-weight:800;text-transform:uppercase;margin-bottom:6px;font-family:Arial,sans-serif;">✦ SEE IT IN ACTION</div>
                          <strong style="font-size:15px;color:#191919;font-family:Arial,sans-serif;display:block;margin-bottom:6px;">Last Witch of Swendel</strong>
                          <p style="font-size:13px;line-height:1.55;color:#191919;margin:6px 0 10px;font-family:Arial,sans-serif;">The protagonist is defined first by <strong>who she is and what is at stake for her</strong>, rather than by her relationship to a romantic partner. Being the “last witch” creates a larger story around survival, identity, power, and what she stands to protect. That gives the romance another narrative arc to intersect with and complicate.</p>
                          <a href="https://pocketfm.com/show/96f6721dc499b730f42b02d86e640d682f4f665d" target="_blank" style="font-size:13px;font-weight:bold;color:#c51d47;text-decoration:none;display:inline-block;font-family:Arial,sans-serif;">▶ Explore Last Witch of Swendel</a>
                        </td>
                      </tr>
                    </table>

                    <!-- ============================================== -->
                    <!-- TIP 03: FANTASY WORLD PRESSURE (PURPLE NUMBER & PEACH/GOLD CARD) -->
                    <!-- ============================================== -->
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="border-top:1px dashed #cfc9c2;padding-top:16px;margin-top:16px;">
                      <tr>
                        <td width="42" valign="top">
                          <span style="font-family:Georgia,serif;color:#7a4d8f;font-size:28px;line-height:1;font-weight:bold;display:block;">03</span>
                        </td>
                        <td valign="top">
                          <h3 style="font-family:Georgia,serif;font-size:19px;line-height:1.2;margin:0;color:#191919;display:inline;font-weight:bold;">Make the fantasy world put pressure on the romance.</h3>
                          <span style="font-family:Georgia,serif;font-weight:bold;display:inline-block;color:#e8a351;font-size:18px;margin-left:6px;">✦</span>
                        </td>
                      </tr>
                    </table>
                    <p style="font-size:13px;line-height:1.58;color:#191919;margin:10px 0;font-family:Arial,sans-serif;">The magic, politics, rules, and antagonists should create real obstacles for the couple. A forbidden bond, dangerous power, faction conflict, or recurring antagonist can make the relationship harder in a way that is specific to that world, which is what makes the fantasy feel essential rather than decorative.</p>

                    <!-- CARD 3: WARM PEACH (#fff3e4) WITH GOLD BORDER (#e8a351) -->
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" bgcolor="#fff3e4" style="background-color:#fff3e4;border-left:4px solid #e8a351;border-radius:0 9px 9px 0;margin:14px 0;">
                      <tr>
                        <td bgcolor="#fff3e4" style="padding:14px 18px;background-color:#fff3e4;border-radius:0 9px 9px 0;">
                          <div style="font-size:10px;color:#a46927;letter-spacing:1.2px;font-weight:800;text-transform:uppercase;margin-bottom:6px;font-family:Arial,sans-serif;">✦ SEE IT IN ACTION</div>
                          <strong style="font-size:15px;color:#191919;font-family:Arial,sans-serif;display:block;margin-bottom:6px;">Bride of a Dragon</strong>
                          <p style="font-size:13px;line-height:1.55;color:#191919;margin:6px 0 10px;font-family:Arial,sans-serif;">Here, the fantasy premise itself shapes the relationship. The heroine isn’t simply falling for someone who happens to exist in a magical world — becoming the bride of a dragon brings questions of power, obligation, and danger directly into the romantic dynamic. Remove the fantasy setup, and you fundamentally change the relationship and its conflict.</p>
                          <a href="https://pocketfm.com/show/bride-of-a-dragon/514efd834428337923e640a1254ea9d7477b18b3" target="_blank" style="font-size:13px;font-weight:bold;color:#c51d47;text-decoration:none;display:inline-block;font-family:Arial,sans-serif;">▶ Explore Bride of a Dragon</a>
                        </td>
                      </tr>
                    </table>

                    <!-- SECTION 04: BEFORE YOU GO -->
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="border-top:2px solid #171717;margin-top:24px;padding-top:12px;margin-bottom:10px;">
                      <tr>
                        <td width="34" valign="middle">
                          <div style="background-color:#e51a4d;color:#ffffff;border-radius:7px;width:25px;height:25px;line-height:25px;text-align:center;font-size:10px;font-weight:900;font-family:Arial,sans-serif;">04</div>
                        </td>
                        <td valign="middle" style="font-size:10px;font-weight:800;letter-spacing:1.2px;color:#191919;font-family:Arial,sans-serif;text-transform:uppercase;">
                          BEFORE YOU GO
                        </td>
                        <td align="right" valign="middle" style="font-size:18px;color:#e51a4d;">✦</td>
                      </tr>
                    </table>

                    <h2 style="font-family:Georgia,serif;font-size:26px;line-height:1.12;margin:6px 0 12px;letter-spacing:-.5px;color:#191919;font-weight:normal;">Over to you</h2>

                    <!-- FEEDBACK CARD (MINT GREEN #eaf4ef) -->
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" bgcolor="#eaf4ef" style="background-color:#eaf4ef;border-left:4px solid #66a28a;border-radius:0 8px 8px 0;margin:14px 0 18px;">
                      <tr>
                        <td bgcolor="#eaf4ef" style="padding:16px 20px;background-color:#eaf4ef;border-radius:0 8px 8px 0;">
                          <strong style="font-size:14px;color:#191919;font-family:Arial,sans-serif;display:block;margin-bottom:8px;">What would help you most as an author working in audio?</strong>
                          <ul style="padding-left:18px;margin:8px 0 0;font-size:13px;line-height:1.6;color:#191919;font-family:Arial,sans-serif;">
                            <li style="margin:4px 0;">Understanding what listeners respond to</li>
                            <li style="margin:4px 0;">Learning how stories translate to audio</li>
                            <li style="margin:4px 0;">Seeing examples of stories that performed well</li>
                            <li style="margin:4px 0;">Understanding new opportunities at Pocket FM</li>
                          </ul>
                        </td>
                      </tr>
                    </table>

                    <p style="font-size:13px;line-height:1.58;color:#191919;margin:10px 0;font-family:Arial,sans-serif;">Lastly…working on something new?<br/>We’d love to hear about it.</p>

                    <!-- CTA BUTTON ROW -->
                    <table border="0" cellpadding="0" cellspacing="0" style="margin:16px 0 20px;">
                      <tr>
                        <td>
                          <table border="0" cellpadding="0" cellspacing="0">
                            <tr>
                              <td align="center" bgcolor="#e51a4d" style="border-radius:20px;background-color:#e51a4d;">
                                <a href="mailto:us-licensing@pocketfm.com?subject=Sharing%20a%20Story" target="_blank" style="font-size:12px;font-weight:800;color:#ffffff;text-decoration:none;padding:10px 18px;border-radius:20px;display:inline-block;font-family:Arial,sans-serif;">Share a Story →</a>
                              </td>
                            </tr>
                          </table>
                        </td>
                      </tr>
                    </table>

                    <p style="font-size:13px;line-height:1.58;color:#191919;margin:12px 0 22px;font-family:Arial,sans-serif;">Until next time,<br/><strong>Team Pocket FM</strong></p>

                    <!-- FOOTER BLOCK -->
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" bgcolor="#171717" style="background-color:#171717;color:#aaaaaa;border-radius:8px;padding:24px 20px;text-align:center;margin-top:20px;">
                      <tr>
                        <td align="center" bgcolor="#171717" style="padding:24px 20px;background-color:#171717;border-radius:8px;">
                          <img src="https://d2p67bdkbtpxn2.cloudfront.net/dd1600b8e1bde867061ac29dcf9078c72bc533bd.jpg" alt="Pocket FM" height="42" style="display:block;margin:0 auto 16px;max-width:180px;border:0;" />
                          <table border="0" cellpadding="0" cellspacing="0" align="center" style="margin:12px auto;">
                            <tr>
                              <td style="padding:0 8px;"><a href="https://twitter.com/PocketFM_App" target="_blank"><img src="https://d2p67bdkbtpxn2.cloudfront.net/2ef29b0580cbc86db3effe6847cbf3c92024b814.png" width="26" height="26" style="display:block;border:0;" alt="X" /></a></td>
                              <td style="padding:0 8px;"><a href="https://www.linkedin.com/company/14522609" target="_blank"><img src="https://d2p67bdkbtpxn2.cloudfront.net/fc05471fbe97d71f1b8037897029df3759916d7c.png" width="26" height="26" style="display:block;border:0;" alt="LinkedIn" /></a></td>
                              <td style="padding:0 8px;"><a href="https://www.facebook.com/pocketfmusa" target="_blank"><img src="https://d2p67bdkbtpxn2.cloudfront.net/bbba48b905fdc913ca50e2014cd43130eb2a6190.png" width="26" height="26" style="display:block;border:0;" alt="Facebook" /></a></td>
                              <td style="padding:0 8px;"><a href="https://www.instagram.com/pocketcreators_usa/" target="_blank"><img src="https://d2p67bdkbtpxn2.cloudfront.net/7f5a11ba1d1e0430dc41bc2679fec746478b9dba.png" width="26" height="26" style="display:block;border:0;" alt="Instagram" /></a></td>
                              <td style="padding:0 8px;"><a href="https://www.youtube.com/@pocket_creators/" target="_blank"><img src="https://d2p67bdkbtpxn2.cloudfront.net/64ac0d2350428f01ae6611b89c7b9c187542e8cd.png" width="26" height="26" style="display:block;border:0;" alt="YouTube" /></a></td>
                            </tr>
                          </table>
                          <div style="font-size:10px;color:#888888;margin-top:12px;font-family:Arial,sans-serif;">
                            © 2026 Pocket FM · Creator Newsletter<br/>
                            <span style="font-size:8px;color:#555555;">{{QUEUE_ID}}</span>
                          </div>
                        </td>
                      </tr>
                    </table>

                    <!-- PAGE 2 FOOTER -->
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-top:32px;border-top:1px solid #bbbbbb;padding-top:8px;">
                      <tr>
                        <td align="left" style="font-size:9px;letter-spacing:1.3px;color:#888888;font-weight:800;font-family:Arial,sans-serif;">POCKET FM</td>
                        <td align="right" style="font-size:9px;letter-spacing:1.3px;color:#888888;font-weight:800;font-family:Arial,sans-serif;">02 / 02</td>
                      </tr>
                    </table>

                  </td>
                </tr>
              </table>
            </div>

            <!--[if mso]>
            </td></tr></table>
            <![endif]-->

          </td>
        </tr>
      </table>

    </td>
  </tr>
</table>

</body>
</html>



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
