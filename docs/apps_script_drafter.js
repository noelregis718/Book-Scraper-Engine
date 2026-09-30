/**
 * POCKETFM AUTOMATED EMAIL BUNDLER
 * 
 * Instructions:
 * 1. Open your Google Sheet ("Lifecycle Tracker - Master")
 * 2. Click on "Extensions" in the top menu, then click "Apps Script"
 * 3. Delete any code there, and paste this entire file.
 * 4. Click the "Save" icon (the floppy disk).
 * 5. Click the "Run" button at the top!
 */

function processOutreachQueue() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = spreadsheet.getSheetByName("Lifecycle Tracker - Master");
  const queueSheet = spreadsheet.getSheetByName("Queue"); // The new database tab for GMass
  
  // If sheet isn't found, stop
  if (!sheet) {
    Logger.log("Could not find a tab named 'Lifecycle Tracker - Master'");
    return;
  }
  
  const data = sheet.getDataRange().getValues();
  
  // A helper function to check if a date is exactly 'days' ago
  function isDaysAgo(dateVal, days) {
    if (!dateVal || !(dateVal instanceof Date)) return false;
    const today = new Date();
    today.setHours(0,0,0,0);
    const targetDate = new Date(dateVal);
    targetDate.setHours(0,0,0,0);
    const diffTime = Math.abs(today - targetDate);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)); 
    return diffDays === days;
  }
  
  // A helper function to check if a date is exactly today
  function isToday(dateVal) {
    if (!dateVal || !(dateVal instanceof Date)) return false;
    const today = new Date();
    const target = new Date(dateVal);
    return today.getDate() === target.getDate() &&
           today.getMonth() === target.getMonth() &&
           today.getFullYear() === target.getFullYear();
  }
  
  // Define header row (Row 3, which is index 2)
  const headerRowIndex = 2; 
  const headers = data[headerRowIndex];
  
  const findCol = (name) => headers.findIndex(h => h.toString().toLowerCase().includes(name.toLowerCase()));
  
  const emailCol = findCol("Email ID");
  const authorCol = findCol("Author Name");
  const firstNameCol = findCol("First Name"); 
  const titleCol = findCol("Title / IP");
  const showLinkCol = findCol("Show Link"); 
  const ccCol = findCol("cc"); // For CC mail
  const revLinkCol = findCol("Revenue Statement Drive"); // Revenue Statement Drive Link
  
  const contractSignedCol = findCol("Contract Signing date"); 
  const vendorLifecycleExitedCol = findCol("Vendor lifecycle Status") + 2; 
  const mgPayoutExitedCol = findCol("Vendor lifecycle Status") + 6; 
  const revStatementDueCol = findCol("Rev Statement Due Date"); 
  
  const welcomeCol = findCol("Welcome Email"); 
  const vendorCol = findCol("Vendor Onboarding Email"); 
  const mgPayoutInitiatedCol = findCol("MG Payout Initiated"); 
  const mgPayoutConfirmationCol = findCol("MG Payout Confirmation"); 
  const checkIn1Col = findCol("Check-In 1"); 
  const checkIn2Col = findCol("Check-In 2"); 
  const launchCol = findCol("Show Launch Announcement"); 
  const revStatementEmailCol = findCol("Revenue Statement + Insights Email"); 
  const launchStatusCol = findCol("Launch Status"); 

  // -------------------------------------------------------------
  // OFFICIAL POCKET FM HTML WRAPPER
  // -------------------------------------------------------------
  function wrapHtml(bodyContent) {
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
<td style="padding:0 10px;"><a href="https://www.instagram.com/pocketcreators_usa/" target="_blank"><img src="https://d2p67bdkbtpxn2.cloudfront.net/7f5a11ba1d1e0430dc41bc2679fec746478b9dba.png" height="30"></a></td>
<td style="padding:0 10px;"><a href="https://www.youtube.com/@pocket_creators/" target="_blank"><img src="https://d2p67bdkbtpxn2.cloudfront.net/64ac0d2350428f01ae6611b89c7b9c187542e8cd.png" height="30"></a></td></tr></tbody></table>
</td></tr>

<tr><td style="padding-top:30px;"></td></tr>

<tr><td align="center" style="font-size:12px; color:#464646;">
Pocket FM Private Limited © 2018 - 2026
</td></tr>

<tr><td style="padding-top:30px;"></td></tr></tbody></table>
</td></tr></tbody></table>
</td></tr></tbody></table>
</body></html>`;
  }

  // -------------------------------------------------------------
  // EMAIL BODIES
  // -------------------------------------------------------------
  function getBody(type, firstName, title, link, grammar, revLink) {
    switch(type) {
      case 'welcome':
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Welcome to Pocket FM! We couldn't be more excited to have you join the platform. It's always a good day when a new story (and a new author) becomes part of the community. It is a pleasure having <b>${title}</b> feature on our platform!
          </td></tr>
          
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Here's a quick walkthrough of what happens next:
          </td></tr>
          
          <tr><td align="left" style="font-size:17px; font-weight:600; color:#E51A4D; padding:20px 35px 5px; line-height:24px;">
          Onboarding & Documentation
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:0px 35px 10px; line-height:24px;">
          Within 1 business day of this email, you'll receive a follow-up from us with the vendor onboarding documents, manuscript submission instructions, and invoice requirements to kick off the formal onboarding process.
          </td></tr>
          
          <tr><td align="left" style="font-size:17px; font-weight:600; color:#E51A4D; padding:20px 35px 5px; line-height:24px;">
          MG Payment
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:0px 35px 10px; line-height:24px;">
          Once all documentation is submitted from your end, we'll initiate your Minimum Guarantee (MG) payment. As per your contract, this is paid out within 30 days of the contract signing date. We'll send you a confirmation once the payment has been processed.
          </td></tr>
          
          <tr><td align="left" style="font-size:17px; font-weight:600; color:#E51A4D; padding:20px 35px 5px; line-height:24px;">
          Production & Launch
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:0px 35px 10px; line-height:24px;">
          Once onboarding is complete, we'll move into production. The typical timeline for production and launching your show on Pocket FM is around 3 months. We'll keep you updated as we reach key milestones throughout the process, including when your show goes live.
          </td></tr>
          
          <tr><td align="left" style="font-size:17px; font-weight:600; color:#E51A4D; padding:20px 35px 5px; line-height:24px;">
          Revenue Statements
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:0px 35px 10px; line-height:24px;">
          As outlined in the contract, we share revenue statements on a quarterly basis. You'll need to raise an invoice against each statement to receive your payment.
          </td></tr>
          
          <tr><td align="left" style="font-size:17px; font-weight:600; color:#E51A4D; padding:20px 35px 5px; line-height:24px;">
          Support
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:0px 35px 20px; line-height:24px;">
          Our Relationship Management team is always here if you have any questions along the way. Just reply to this email!
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
          Please find attached the vendor onboarding documents for <b>${title}</b>. Kindly fill these out and return ${grammar.it} so we can process your MG payment.
          </td></tr>

          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <a href="..." style="color:#E51A4D; font-weight:bold; text-decoration:none;">Access Onboarding Documents</a>
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
          Great news! The MG payment for <b>${title}</b> has been officially approved in our system and the transfer has been initiated.
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
          We are confirming that your MG payment for <b>${title}</b> has been fully processed. It should reflect in your account shortly. 
          </td></tr>
          
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We'd love to hear your feedback on the onboarding process so far!
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
          I'm just checking in to see how everything is going with <b>${title}</b>. We are so thrilled to have ${grammar.it} on the platform!
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
          I wanted to quickly check in on <b>${title}</b>. Have you had a chance to share ${grammar.it} with your readers yet?
          </td></tr>
          
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;
        
      case 'launch':
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          I am so excited to announce that <b>${title}</b> ${grammar.is} now officially live on Pocket FM!
          </td></tr>
          
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          You can check ${grammar.it} out here: <a href="${link}" style="color:#E51A4D;">${link}</a>
          </td></tr>
          
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;
        
      case 'revStatement':
        const revHref = revLink ? revLink : "#";
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          As per our contract, please find your quarterly revenue statement for <b>${title}</b> attached below.
          </td></tr>
          
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <a href="${revHref}" style="color:#E51A4D; font-weight:bold; text-decoration:none;">Access Revenue Statement</a>
          </td></tr>

          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Please review the statement and raise an invoice against it so we can process your payment.
          </td></tr>
          
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          If you have any questions about the metrics or the invoice process, simply reply to this email.
          </td></tr>
          
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;
    }
  }

  // -------------------------------------------------------------
  // DRAFTING LOGIC WITH VARIABLE MAPPING & QUEUE INJECTION
  // -------------------------------------------------------------
  function createDraft(email, subject, firstName, type, title, link, rIdx, cIdx, customSendTime, ccMail, revLink) {
    // 1. Variable Mapping (Singular vs Plural logic from 'Variable Mapping' tab)
    const isMulti = title.includes(",");
    const grammar = {
      work: isMulti ? "works" : "work",
      is: isMulti ? "are" : "is",
      has: isMulti ? "have" : "has",
      title: isMulti ? "titles" : "title",
      this: isMulti ? "these" : "this",
      it: isMulti ? "them" : "it",
      its: isMulti ? "their" : "its"
    };

    const body = getBody(type, firstName, title, link, grammar, revLink);
    const wrappedBody = wrapHtml(body);
    
    // 2. Map 'type' to the exact Automation Rule Template Name
    let templateName = type;
    if (type === "welcome") templateName = "Welcome Email";
    if (type === "vendor") templateName = "Vendor Onboarding Email";
    if (type === "mgInitiated") templateName = "MG Payment Initiated";
    if (type === "mgConfirmed") templateName = "MG Payment Processed";
    if (type === "checkIn1") templateName = "Personal Check In 1";
    if (type === "checkIn2") templateName = "Personal Check In 2";
    if (type === "launch") templateName = "AI Allowed - Show Launch Announcement";
    if (type === "revStatement") templateName = "Revenue Statement";

    // 3. Generate Data for Queue
    const queueId = Utilities.getUuid();
    const sendDate = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy-MM-dd");
    const sendTime = customSendTime ? customSendTime : "9:30 AM IST"; 
    const ccValue = ccMail ? ccMail : "";
    
    // 4. Append to Queue Tab (Queue ID, Recipient, Sender, Template, Subject, HTML Body, Send Date, Send Time, Status, Row IDs, Approved, CC)
    if (queueSheet) {
      queueSheet.appendRow([
        queueId,
        email, 
        Session.getActiveUser().getEmail(), 
        templateName, 
        subject,
        wrappedBody,
        sendDate,
        sendTime,
        "Ready", 
        rIdx + 1, 
        "Yes",
        ccValue // Appended CC to queue for GMass
      ]);
    }

    // (Optional) We keep the traditional draft creation just in case you want to manually verify in Gmail
    let draftOptions = { htmlBody: wrappedBody };
    if (ccMail && ccMail !== "") {
      draftOptions.cc = ccMail;
    }
    GmailApp.createDraft(email, subject, "", draftOptions);
    
    // Update main tracker sheet to "Queued" instead of "Sent"
    sheet.getRange(rIdx + 1, cIdx + 1).setValue("Queued");
  }

  // Iterate over all rows starting from row 4 (index 3)
  for (let i = 3; i < data.length; i++) {
    let row = data[i];
    
    let email = row[emailCol];
    let author = row[authorCol];
    let title = row[titleCol];
    let link = row[showLinkCol];
    let ccMail = ccCol > -1 ? row[ccCol] : "";
    let revLink = revLinkCol > -1 ? row[revLinkCol] : "";
    let launchStatus = row[launchStatusCol] ? row[launchStatusCol].toString().toLowerCase() : "";
    
    // Graceful fallback: If First Name is missing, use Author Name
    let firstName = (firstNameCol > -1 && row[firstNameCol] && row[firstNameCol].toString().trim() !== "") 
                    ? row[firstNameCol] 
                    : author;
    
    if (!email) continue; 
    
    // BLOCKING RULE: If Launch Status is "bad" or "dropped", completely skip processing any further emails for this author
    if (launchStatus.includes("bad") || launchStatus.includes("dropped")) {
      continue;
    }
    
    const isReady = (status) => status !== "Scheduled" && status !== "Sent" && status !== "Queued";
    
    // Welcome Email (Today)
    if (isToday(row[contractSignedCol]) && isReady(row[welcomeCol])) {
      createDraft(email, `Welcome to Pocket FM – here's what happens next`, firstName, 'welcome', title, link, i, welcomeCol, null, ccMail, revLink);
    }
    
    // Vendor Onboarding Email (Today - 6 Hours After Welcome)
    if (isToday(row[contractSignedCol]) && isReady(row[vendorCol])) {
      // Changed subject from 'Action Required: Vendor...' to 'Vendor...'
      createDraft(email, `Vendor Onboarding for ${title}`, firstName, 'vendor', title, link, i, vendorCol, "3:30 PM IST", ccMail, revLink);
    }
    
    // MG Payout Initiated (Today based on vendor lifecycle exit)
    if (isToday(row[vendorLifecycleExitedCol]) && isReady(row[mgPayoutInitiatedCol])) {
      createDraft(email, `Payment Initiated: Minimum Guarantee for ${title}`, firstName, 'mgInitiated', title, link, i, mgPayoutInitiatedCol, null, ccMail, revLink);
    }
    
    // MG Payout Confirmation (Today based on MG payout exit)
    if (isToday(row[mgPayoutExitedCol]) && isReady(row[mgPayoutConfirmationCol])) {
      createDraft(email, `Payment Processed: Minimum Guarantee for ${title}`, firstName, 'mgConfirmed', title, link, i, mgPayoutConfirmationCol, null, ccMail, revLink);
    }
    
    // 15 Day Check-In (15 Days Ago AND Show Link must be BLANK)
    let isShowLinkBlank = (link === "" || link === null || link === undefined);
    if (isDaysAgo(row[mgPayoutExitedCol], 15) && isShowLinkBlank && isReady(row[checkIn1Col])) {
      createDraft(email, `Checking in on ${title}`, firstName, 'checkIn1', title, link, i, checkIn1Col, null, ccMail, revLink);
    }
    
    // 30 Day Check-In (30 Days Ago AND Show Link must be BLANK)
    if (isDaysAgo(row[mgPayoutExitedCol], 30) && isShowLinkBlank && isReady(row[checkIn2Col])) {
      createDraft(email, `Checking in on ${title}`, firstName, 'checkIn2', title, link, i, checkIn2Col, null, ccMail, revLink);
    }
    
    // Show Launch Announcement Status (Any time Show Link is filled)
    if (link && link !== "" && isReady(row[launchCol])) {
      createDraft(email, `Congratulations! ${title} is Live on Pocket FM`, firstName, 'launch', title, link, i, launchCol, null, ccMail, revLink);
    }
    
    // Revenue Statement Email (Today)
    if (isToday(row[revStatementDueCol]) && isReady(row[revStatementEmailCol])) {
      createDraft(email, `Revenue Statement for ${title}`, firstName, 'revStatement', title, link, i, revStatementEmailCol, null, ccMail, revLink);
    }
  }
}
