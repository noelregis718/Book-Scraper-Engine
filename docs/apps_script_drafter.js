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
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Lifecycle Tracker - Master");
  
  // If sheet isn't found, stop
  if (!sheet) {
    Logger.log("Error: Could not find sheet 'Lifecycle Tracker - Master'");
    return;
  }
  
  const data = sheet.getDataRange().getValues();
  
  // Assuming Row 1 is the Header (Index 0 in 0-indexed arrays)
  const headerRowIndex = 0; 
  const headers = data[headerRowIndex];
  
  // Find column indexes
  const authorCol = headers.indexOf("Author Name");
  const titleCol = headers.indexOf("Title / IP");
  const licensorCol = headers.indexOf("Licensor (Legal name)");
  const statusCol = headers.indexOf("Status");
  
  if (authorCol === -1 || titleCol === -1 || licensorCol === -1 || statusCol === -1) {
    Logger.log("Error: Missing required columns (Author Name, Title / IP, Licensor (Legal name), Status)");
    return;
  }
  
  // Check if AI_Context_Bundle column exists, if not, create it
  let contextCol = headers.indexOf("AI_Context_Bundle");
  if (contextCol === -1) {
    contextCol = headers.length;
    sheet.getRange(headerRowIndex + 1, contextCol + 1).setValue("AI_Context_Bundle");
  }

  // Step 1: Collect all rows that are "Ready for Outreach"
  let outreachQueue = [];
  
  for (let i = headerRowIndex + 1; i < data.length; i++) {
    const status = data[i][statusCol];
    // Trigger for ANY status that is filled out (In Progress, Done, Ready for Outreach, etc)
    if (status && status.toString().trim() !== "") {
      outreachQueue.push({
        rowIndex: i,
        author: data[i][authorCol],
        title: data[i][titleCol],
        licensor: data[i][licensorCol]
      });
    }
  }
  
  if (outreachQueue.length === 0) {
    Logger.log("No rows found with Status 'Ready for Outreach'");
    return;
  }
  
  // Step 2: Group by Licensor (Agency)
  let groupedByLicensor = {};
  
  outreachQueue.forEach(item => {
    if (!groupedByLicensor[item.licensor]) {
      groupedByLicensor[item.licensor] = [];
    }
    groupedByLicensor[item.licensor].push(item);
  });
  
  // Step 3: Process Groups and Determine Scenarios
  for (let licensor in groupedByLicensor) {
    let group = groupedByLicensor[licensor];
    
    let authors = group.map(g => g.author);
    let books = group.map(g => g.title);
    
    let uniqueAuthors = [...new Set(authors)];
    let isDirect = (uniqueAuthors.length === 1 && uniqueAuthors[0] === licensor);
    
    let scenario = 2; // Default
    let context = "";
    
    if (isDirect && books.length === 1) {
      scenario = 1;
      context = `Direct Author Outreach. Recipient: ${authors[0]}. Book to license: ${books[0]}.`;
    } 
    else if (!isDirect && books.length === 1) {
      scenario = 2;
      context = `Agency Outreach. Recipient: ${licensor}. Author they represent: ${authors[0]}. Book to license: ${books[0]}.`;
    }
    else if (!isDirect && books.length > 1) {
      scenario = 3;
      context = `Agency Outreach (Multiple Authors/Books). Recipient: ${licensor}. Books to license: `;
      for (let i = 0; i < books.length; i++) {
        context += `'${books[i]}' by ${authors[i]}, `;
      }
    }
    else if (isDirect && books.length > 1) {
      scenario = 4;
      context = `Direct Author Outreach (Multiple Books). Recipient: ${authors[0]}. Books to license: `;
      for (let i = 0; i < books.length; i++) {
        context += `'${books[i]}', `;
      }
    }
    
    // Clean up trailing commas
    context = context.replace(/, $/, ".");
    
    // Step 4: Write Context to the FIRST row of that group.
    // For the other books in that group, mark them as "Bundled" so we don't send duplicate emails.
    let primaryRow = group[0].rowIndex;
    sheet.getRange(primaryRow + 1, contextCol + 1).setValue(context);
    
    for (let i = 1; i < group.length; i++) {
      let secondaryRow = group[i].rowIndex;
      sheet.getRange(secondaryRow + 1, contextCol + 1).setValue("Bundled with row " + (primaryRow + 1));
    }
    
    Logger.log(`Processed ${licensor} - Scenario ${scenario}`);
  }
  
  Logger.log("Finished generating all AI Context Bundles!");
}

/**
 * ============================================================================
 * POST-SALES CRM EMAIL SCHEDULER (100% COMPLETE)
 * Trigger: Set this function to run Time-driven -> Day timer -> 7:00 PM to 8:00 PM
 * ============================================================================
 */

function processPostSalesTriggers() {
  const sheet = SpreadsheetApp.openByUrl("https://docs.google.com/spreadsheets/d/1qQegfsBODu8GAfe1lMCxNtYV75MWCEtQOopiwH4JcWY/edit?gid=1165007468#gid=1165007468").getSheetByName("Lifecycle Tracker - Master");
  if (!sheet) return;
  
  const data = sheet.getDataRange().getValues();
  const headerRowIndex = 2; 
  const headers = data[headerRowIndex];
  
  const emailCol = headers.indexOf("Email ID");
  const authorCol = headers.indexOf("Author Name");
  const titleCol = headers.indexOf("Title / IP");
  const showLinkCol = headers.indexOf("Show Link"); 
  
  const contractSignedCol = headers.indexOf("Contract Signing date"); 
  const vendorLifecycleExitedCol = headers.indexOf("Vendor lifecycle Status") + 2; 
  const mgPayoutExitedCol = headers.indexOf("Vendor lifecycle Status") + 6; 
  const mgConfirmedCol = headers.indexOf("MG Payout Confirmation + Feedback Mail"); 
  const revStatementDueCol = headers.indexOf("Rev Statement Due Date"); 
  
  const welcomeCol = headers.indexOf("Welcome Email"); 
  const vendorCol = headers.indexOf("Vendor Onboarding Email \n(Same day as Welcome Email)"); 
  const mgPayoutInitiatedCol = headers.indexOf("MG Payout Initiated\n(Netsuite Stage: Bill approved)"); 
  const mgPayoutConfirmationCol = headers.indexOf("MG Payout Confirmation + Feedback Mail"); 
  const checkIn1Col = headers.indexOf("Author Check-In 1:\n(MG Payout Confirmation + 15 days)"); 
  const checkIn2Col = headers.indexOf("Author Check-In 2:\n(MG Payout Confirmation + 30 days)\n[Optional]"); 
  const launchCol = headers.indexOf("Show Launch Announcement Status"); 
  const revStatementEmailCol = headers.indexOf("Revenue Statement + Insights Email Status"); 
  
  // -------------------------------------------------------------
  // OFFICIAL POCKET FM HTML WRAPPER
  // -------------------------------------------------------------
  const wrapHtml = (authorName, bodyText) => `
<table border="0" cellpadding="0" cellspacing="0" style="background-color:#000000; width:600px;"><tbody>
<tr><td align="center">
<img alt="Pocket FM Logo" src="https://d2p67bdkbtpxn2.cloudfront.net/c8b7ada83f09146d4b2c2ba3a5c3c1b8ea36e459.jpg" style="display:block; max-width:600px;">
</td></tr>
<tr><td align="center" style="padding-top:15px;">
<table border="0" cellpadding="0" cellspacing="0" style="background-color:#FFFFFF; width:600px; border-radius:10px;"><tbody>
<tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
Hi ${authorName},
</td></tr>
<tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
${bodyText}
</td></tr>
<tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
Best,<br>US Licensing & Commissioning Team<br>Pocket FM
</td></tr></tbody></table>
</td></tr>
<tr><td style="padding-top:10px;"></td></tr>
<tr><td style="padding:20px;">
<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-color:#121212; border-radius:10px; width:600px;"><tbody>
<tr><td align="center" style="padding:30px 0;">
<img alt="Pocket FM Logo" src="https://d2p67bdkbtpxn2.cloudfront.net/dd1600b8e1bde867061ac29dcf9078c72bc533bd.jpg" height="50" style="display:block;">
</td></tr>
<tr><td align="center">
<table border="0" cellpadding="0" cellspacing="0"><tbody><tr>
<td style="padding:0 10px;"><a href="https://twitter.com/PocketFM_App" target="_blank"><img src="https://d2p67bdkbtpxn2.cloudfront.net/2ef29b0580cbc86db3effe6847cbf3c92024b814.png" height="30"></a></td>
<td style="padding:0 10px;"><a href="https://www.linkedin.com/company/14522609" target="_blank"><img src="https://d2p67bdkbtpxn2.cloudfront.net/fc05471fbe97d71f1b8037897029df3759916d7c.png" height="30"></a></td>
<td style="padding:0 10px;"><a href="https://www.facebook.com/pocketfmusa" target="_blank"><img src="https://d2p67bdkbtpxn2.cloudfront.net/bbba48b905fdc913ca50e2014cd43130eb2a6190.png" height="30"></a></td>
<td style="padding:0 10px;"><a href="https://www.instagram.com/pocketcreators_usa/" target="_blank"><img src="https://d2p67bdkbtpxn2.cloudfront.net/7f5a11ba1d1e0430dc41bc2679fec746478b9dba.png" height="30"></a></td>
<td style="padding:0 10px;"><a href="https://www.youtube.com/@pocket_creators/" target="_blank"><img src="https://d2p67bdkbtpxn2.cloudfront.net/64ac0d2350428f01ae6611b89c7b9c187542e8cd.png" height="30"></a></td>
</tr></tbody></table>
</td></tr>
<tr><td style="padding-top:30px;"></td></tr>
<tr><td align="center" style="font-size:12px; color:#464646;">Pocket FM Private Limited © 2018 - 2024</td></tr>
<tr><td style="padding-top:30px;"></td></tr>
</tbody></table>
</td></tr></tbody></table>`;

  // -------------------------------------------------------------
  // EXACT SOP COPY (No GPT Needed - Perfect Compliance)
  // -------------------------------------------------------------
  const getBody = (stage, title, link) => {
    switch(stage) {
      case 'welcome':
        return `Welcome to Pocket FM! We couldn't be more excited to have you join the platform. It's always a good day when a new story becomes part of the community.<br><br><b>Here's a quick walkthrough of what happens next:</b><br><br><b>Onboarding & Documentation</b><br>Within 1 business day of this email, you'll receive a follow-up from us with the vendor onboarding documents, manuscript submission instructions, and invoice requirements to kick off the formal onboarding process.<br><br><b>MG Payment</b><br>Once all documentation is submitted from your end, we'll initiate your Minimum Guarantee (MG) payment. As per your contract, this is paid out within 30 days of the contract signing date. We'll send you a confirmation once the payment has been processed.<br><br><b>Production & Launch</b><br>Once onboarding is complete, we'll move into production. The typical timeline for production and launching your show on Pocket FM is around 3 months. We'll keep you updated as we reach key milestones throughout the process, including when your show goes live.<br><br><b>Revenue Statements</b><br>As outlined in the contract, we share revenue statements on a quarterly basis. You'll need to raise an invoice against each statement to receive your payment.<br><br><b>Support</b><br>Our Relationship Management team is always here if you have any questions along the way. Just reply to this email.<br><br>We're genuinely glad to be starting this journey with you, and we look forward to bringing your story to listeners around the world.`;
      case 'vendor':
        return `This is a quick follow-up to kick off your formal onboarding process for <b>${title}</b>.<br><br>Please find the vendor onboarding documents and manuscript submission instructions attached. Once you submit these documents, we will officially initiate the payment process for your Minimum Guarantee (MG).<br><br>We will keep you posted once the payment is processed from our end!`;
      case 'mgInitiated':
        return `Great news! We have successfully processed your onboarding documents and officially initiated the payment process for your Minimum Guarantee (MG) for <b>${title}</b>.<br><br>From this point onwards, we will kickstart the production process! We will keep you posted about the show launch and traction/performance metrics.`;
      case 'mgConfirmed':
        return `We are writing to confirm that your Minimum Guarantee (MG) payment for <b>${title}</b> has been successfully processed and transferred to your account.<br><br>Please let us know if you have any questions!`;
      case 'checkIn1':
        return `We just wanted to do a quick check-in to see how you are doing! It has been 15 days since your payout for <b>${title}</b>.<br><br>Please let us know if you need anything from our end as we continue production.`;
      case 'checkIn2':
        return `It has been 30 days since your payout for <b>${title}</b>. We wanted to touch base and ensure everything is going smoothly!<br><br>We are excited about the progress on our end and will keep you updated.`;
      case 'launch':
        return `Congratulations! We are thrilled to announce that your audio show for <b>${title}</b> is officially live on Pocket FM!<br><br>You can listen to your show here: <a href="${link}">${link}</a><br><br>Over the next 3 months, we will be closely monitoring the show's performance. We will follow up to share detailed feedback, listener insights, and user sentiment with you soon.<br><br>Thank you for partnering with us to bring this story to life!`;
      case 'revStatement':
        return `As per our contract, please find your quarterly revenue statement for <b>${title}</b> attached below.<br><br>Please review the statement and raise an invoice against it so we can process your payment.<br><br>If you have any questions about the metrics or the invoice process, simply reply to this email.`;
    }
  };
  
  const today = new Date();
  today.setHours(0,0,0,0);
  const isToday = (dVal) => dVal && dVal instanceof Date && (new Date(dVal)).setHours(0,0,0,0) === today.getTime();
  const addDays = (dVal, d) => { if (!dVal || !(dVal instanceof Date)) return null; let dt = new Date(dVal); dt.setDate(dt.getDate() + d); return dt; };

  const createDraft = (email, subject, author, stage, title, link, rIdx, cIdx) => {
    if (!email || email.trim() === "") return;
    const finalHtml = wrapHtml(author, getBody(stage, title, link));
    GmailApp.createDraft(email, subject, "", { htmlBody: finalHtml });
    sheet.getRange(rIdx + 1, cIdx + 1).setValue("Scheduled");
  };

  for (let i = headerRowIndex + 1; i < data.length; i++) {
    let row = data[i];
    let email = row[emailCol];
    if (!email) continue;
    let author = row[authorCol], title = row[titleCol], link = row[showLinkCol];
    
    if (isToday(row[contractSignedCol])) {
      if (row[welcomeCol] !== "Scheduled" && row[welcomeCol] !== "Sent") createDraft(email, `Welcome to Pocket FM — here's what happens next`, author, 'welcome', title, link, i, welcomeCol);
      if (row[vendorCol] !== "Scheduled" && row[vendorCol] !== "Sent") createDraft(email, `Vendor Onboarding Required - ${title}`, author, 'vendor', title, link, i, vendorCol);
    }
    if (isToday(row[vendorLifecycleExitedCol]) && row[mgPayoutInitiatedCol] !== "Scheduled" && row[mgPayoutInitiatedCol] !== "Sent") {
      createDraft(email, `MG Payout Initiated - ${title}`, author, 'mgInitiated', title, link, i, mgPayoutInitiatedCol);
    }
    if (isToday(row[mgPayoutExitedCol]) && row[mgPayoutConfirmationCol] !== "Scheduled" && row[mgPayoutConfirmationCol] !== "Sent") {
      createDraft(email, `MG Payout Confirmed - ${title}`, author, 'mgConfirmed', title, link, i, mgPayoutConfirmationCol);
    }
    let mgDate = row[mgConfirmedCol];
    if (mgDate && mgDate instanceof Date) {
      if (isToday(addDays(mgDate, 15)) && row[checkIn1Col] !== "Scheduled" && row[checkIn1Col] !== "Sent") createDraft(email, `Checking in on ${title}`, author, 'checkIn1', title, link, i, checkIn1Col);
      if (isToday(addDays(mgDate, 30)) && row[checkIn2Col] !== "Scheduled" && row[checkIn2Col] !== "Sent") createDraft(email, `Following up on ${title}`, author, 'checkIn2', title, link, i, checkIn2Col);
    }
    if (link && link.toString().includes("http") && row[launchCol] !== "Scheduled" && row[launchCol] !== "Sent") {
      createDraft(email, `Your Show is Live! - ${title}`, author, 'launch', title, link, i, launchCol);
    }
    if (isToday(row[revStatementDueCol]) && row[revStatementEmailCol] !== "Scheduled" && row[revStatementEmailCol] !== "Sent") {
      createDraft(email, `Revenue Statement for ${title}`, author, 'revStatement', title, link, i, revStatementEmailCol);
    }
  }
}
