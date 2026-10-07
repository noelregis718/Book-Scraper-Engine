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

function processOutreachQueue(isDelayedRun = false) {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  const allSheets = spreadsheet.getSheets();
  let mainSheet = null;
  let psSheet = null;
  let queueSheet = null;
  
  for (let s of allSheets) {
    let sName = s.getName().toLowerCase().trim();
    sName = sName.replace("–", "-").replace("—", "-"); // Standardize dashes
    
    // 1. Exact match takes top priority
    if (sName === "lifecycle tracker - master") { mainSheet = s; }
    else if (sName === "post-sales tracker" || sName === "post sales tracker") { psSheet = s; }
    else if (sName === "queue") { queueSheet = s; }
  }
  
  // 2. Fallback to Post Sale Comms Tracker (exact match) if Post-Sales Tracker doesn't exist
  if (!psSheet) {
    for (let s of allSheets) {
      let sName = s.getName().toLowerCase().trim();
      if (sName === "post sale comms tracker") { psSheet = s; break; }
    }
  }
  
  // 3. Last resort partial matches
  if (!mainSheet) {
    for (let s of allSheets) {
      let sName = s.getName().toLowerCase().trim();
      if (sName.includes("lifecycle tracker - master")) { mainSheet = s; break; }
    }
  }
  if (!psSheet) {
    for (let s of allSheets) {
      let sName = s.getName().toLowerCase().trim();
      if (sName.includes("post-sales tracker") || sName.includes("post sale comms tracker")) { psSheet = s; break; }
    }
  }
  
  Logger.log('Selected Main Sheet: ' + (mainSheet ? mainSheet.getName() : 'None'));
  Logger.log('Selected PS Sheet: ' + (psSheet ? psSheet.getName() : 'None'));
  
  
  if (queueSheet) {
    queueSheet.getRange(1, 12).setValue("CC");
    let headerRange = queueSheet.getRange(1, 1, 1, 12);
    headerRange.setBackground("#1155cc"); 
    headerRange.setFontColor("#ffffff");
    headerRange.setFontWeight("bold");
    headerRange.setHorizontalAlignment("center");
    headerRange.setVerticalAlignment("middle");
    queueSheet.setRowHeight(1, 40); 
    queueSheet.hideColumns(1);
    queueSheet.hideColumns(6);
    queueSheet.setColumnWidth(2, 200);
    queueSheet.setColumnWidth(4, 220);
    queueSheet.setColumnWidth(5, 350);
    queueSheet.getRange("B:E").setWrap(true);
    queueSheet.getRange("G:I").setHorizontalAlignment("center");
  }
  
  if (!mainSheet || !psSheet) {
    Logger.log("Could not find required tracking tabs. Main Sheet found: " + (mainSheet !== null) + ", Post-Sales Tracker found: " + (psSheet !== null));
    let names = [];
    allSheets.forEach(s => names.push(s.getName()));
    Logger.log("Available sheets: " + names.join(", "));
    return;
  }
  
  const mainData = mainSheet.getDataRange().getValues();
  const psData = psSheet.getDataRange().getValues();
  
  function isDaysAgo(dateVal, days) {
    if (!dateVal) return false;
    let targetDate = (dateVal instanceof Date) ? dateVal : new Date(dateVal);
    if (isNaN(targetDate)) return false;
    const today = new Date();
    today.setHours(0,0,0,0);
    targetDate.setHours(0,0,0,0);
    const diffTime = Math.abs(today - targetDate);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)); 
    return diffDays === days;
  }
  
  function isToday(dateVal) {
    if (!dateVal) return false;
    let target = (dateVal instanceof Date) ? dateVal : new Date(dateVal);
    if (isNaN(target)) return false;
    const today = new Date();
    return today.getDate() === target.getDate() &&
           today.getMonth() === target.getMonth() &&
           today.getFullYear() === target.getFullYear();
  }
  
  // Headers for main sheet (Row 3, index 2)
  const mainHeaders = mainData[2];
  const mainFindCol = (name) => mainHeaders.findIndex(h => h.toString().toLowerCase().includes(name.toLowerCase()));
  
  // --- ARGUS DATA PARSING ---
  const argusSheet = spreadsheet.getSheetByName("Noel's Automation : Argus Data ( New Data )");
  let argusData = {};
  if (argusSheet) {
    const aData = argusSheet.getDataRange().getValues();
    if (aData.length > 0) {
      const aHeaders = aData[0];
      const aFindCol = (name) => aHeaders.findIndex(h => h.toString().toLowerCase().includes(name.toLowerCase()));
      const aShowIdCol = aFindCol("Show ID");
      const aDurCol = aFindCol("Duration");
      const aLdauCol = aFindCol("LDAU") > -1 ? aFindCol("LDAU") : aFindCol("Plays");
      const aCommentsCol = aFindCol("Comment");
      const aRatingsCol = aFindCol("Rating");
      const aReviewsCol = aFindCol("Review");
      const aHoursCol = aFindCol("Listening Hour");
      
      if (aShowIdCol > -1) {
        for (let j = 1; j < aData.length; j++) {
           let sid = aData[j][aShowIdCol];
           if (sid) {
             let dur = aDurCol > -1 ? aData[j][aDurCol] : "";
             let ldau = aLdauCol > -1 ? aData[j][aLdauCol] : "";
             let comments = aCommentsCol > -1 ? aData[j][aCommentsCol] : "";
             let ratings = aRatingsCol > -1 ? aData[j][aRatingsCol] : "";
             let reviews = aReviewsCol > -1 ? aData[j][aReviewsCol] : "";
             let hours = aHoursCol > -1 ? aData[j][aHoursCol] : "";

             argusData[sid.toString().trim()] = {
                duration: (dur !== "" && dur !== null) ? dur + " hours" : "${argus.duration}",
                ldau: (ldau !== "" && ldau !== null) ? ldau + " listeners" : "${argus.ldau}",
                comments: (comments !== "" && comments !== null && comments.toString() !== "0") ? comments : "No comments",
                ratings: (ratings !== "" && ratings !== null && ratings.toString() !== "0") ? ratings : "No ratings",
                reviews: (reviews !== "" && reviews !== null && reviews.toString() !== "0") ? reviews : "No reviews",
                hours: (hours !== "" && hours !== null) ? hours : "${argus.hours}"
             };
           }
        }
      }
    }
  }
  // --------------------------
  
  const showIdCol = mainFindCol("Show ID");
  const emailCol = mainFindCol("Receiver Email ID");
  const authorCol = mainFindCol("Author Name");
  const firstNameCol = mainFindCol("Receiver First Name"); 
  const mainTitleCol = mainFindCol("Title / IP");
  const showLinkCol = mainFindCol("Show Link"); 
  const ccCol = mainFindCol("CC Mail ID"); 
  
  const contractSignedCol = mainFindCol("Contract Signing date"); 
  const vendorLifecycleExitedCol = contractSignedCol + 4; 
  const mgPayoutExitedCol = contractSignedCol + 7; 
  const launchStatusCol = mainFindCol("Launch Status"); 

  // Build a lookup dictionary for main sheet data based on Title / IP
  let mainDict = {};
  for(let i = 3; i < mainData.length; i++) {
     let row = mainData[i];
     let t = row[mainTitleCol];
     if (t) {
         let safeTitle = t.toString().toLowerCase().trim();
         mainDict[safeTitle] = {
             email: row[emailCol],
             author: row[authorCol],
             firstName: row[firstNameCol],
             showLink: row[showLinkCol],
             ccMail: row[ccCol],
             showId: showIdCol > -1 ? row[showIdCol] : "",
             contractSigned: row[contractSignedCol],
             vendorLifecycleExited: row[vendorLifecycleExitedCol],
             mgPayoutExited: row[mgPayoutExitedCol],
             launchStatus: row[launchStatusCol]
         };
     }
  }

  // Headers for Post-Sales Tracker (Row 3, index 2)
  const psHeaders = psData[2];
  const psFindCol = (name) => psHeaders.findIndex(h => h.toString().toLowerCase().includes(name.toLowerCase()));
  
  const psTitleCol = psFindCol("Title / IP");
  const welcomeCol = psFindCol("Welcome Email"); 
  const vendorCol = psFindCol("Vendor Onboarding Email"); 
  const mgPayoutInitiatedCol = psFindCol("MG Payout Initiated"); 
  const mgPayoutConfirmationCol = psFindCol("MG Payout Confirmation"); 
  const checkIn1Col = psFindCol("15 days"); 
  const checkIn2Col = psFindCol("30 days"); 
  const launchCol = psFindCol("Show Launch Announcement"); 
  const revStatementDueCol = psFindCol("Rev Statement Due Date"); 
  const revLinkCol = psFindCol("Revenue Statement Drive Link"); 
  const revStatementEmailCol = psFindCol("Insights Email Status") > -1 ? psFindCol("Insights Email Status") : psFindCol("Insights Email"); 

  // -------------------------------------------------------------
  // DRAFTING LOGIC WITH VARIABLE MAPPING & QUEUE INJECTION
  // -------------------------------------------------------------
  function createDraft(email, subject, firstName, type, title, link, rIdx, cIdx, customSendTime, ccMail, revLink, argus) {
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

    // 2. Map 'type' to the exact Automation Rule Template Name
    let templateName = type;
    if (type === "welcome") templateName = "Welcome Email";
    if (type === "vendor") templateName = "Vendor Onboarding Email";
    if (type === "mgInitiated") templateName = "MG Payment Initiated";
    if (type === "mgConfirmed") templateName = "MG Payment Processed";
    if (type === "checkIn1") templateName = "Personal Check In 1";
    if (type === "checkIn2") templateName = "Personal Check In 2";
    if (type === "launch") templateName = "AI Allowed - Show Launch Announcement";
    if (type === "revStatement_workedWell_content") templateName = "Content Update - worked well";
    if (type === "revStatement_workedWell_payment") templateName = "Worked Well - Payment-Related Update";
    if (type === "revStatement_didntWorkWell") templateName = "Didnt work well - Content Related Update";

    // 3. Generate Data for Queue
    const queueId = Utilities.getUuid();
    
    const body = getBody(type, firstName, title, link, grammar, revLink, argus);
    const wrappedBody = wrapHtml(body, queueId);
    
    const sendDate = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy-MM-dd");
    const exactTime = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "hh:mm a"); 
    const sendTime = customSendTime ? customSendTime : exactTime; 
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
        "Draft Ready", 
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
    
    // Update main tracker sheet to "Ready" indicating draft is prepared
    psSheet.getRange(rIdx + 1, cIdx + 1).setValue("Ready");
    Logger.log("SUCCESS: Created draft for " + title + " (Type: " + type + ")");
  }

  // Iterate over all rows in Post-Sales Tracker (starting from index 3)
  let triggerSet = false;
  
  for (let i = 3; i < psData.length; i++) {
    let psRow = psData[i];
    let title = psRow[psTitleCol];
    if (!title) continue;
    
    let safeTitle = title.toString().toLowerCase().trim();
    let mainInfo = mainDict[safeTitle];
    if (!mainInfo) {
      Logger.log("SKIPPED: Title in Post-Sales Tracker not found in Master tracker: [" + title + "]");
      continue; 
    }
    
    let email = mainInfo.email;
    if (!email || email.toString().trim() === "") {
      Logger.log("SKIPPED: Missing email for title: " + title);
      continue;
    }
    let showId = mainInfo.showId;
    let argus = (showId && argusData[showId.toString().trim()]) ? argusData[showId.toString().trim()] : {duration: "[Insert Duration Produced]", ldau: "[Insert LDAUs]", comments: "[Insert Number of Comments]", ratings: "[Insert Ratings]", reviews: "[Insert Reviews]", hours: "[Insert Listening Hours]"};
    let author = mainInfo.author;
    let link = mainInfo.showLink;
    let ccMail = mainInfo.ccMail;
    
    // Safely pull from the dynamic Revenue Statement Drive Link column on the PS Tracker
    let revLinkRaw = (revLinkCol > -1 && psRow.length > revLinkCol) ? psRow[revLinkCol] : "";
    let revLink = (revLinkRaw && revLinkRaw.toString().trim() !== "") ? revLinkRaw.toString().trim() : "";
    if (revLink && !revLink.startsWith("http")) {
        revLink = "https://" + revLink;
    }
    
    let launchStatus = mainInfo.launchStatus ? mainInfo.launchStatus.toString().toLowerCase() : "";
    
    // Graceful fallback: If First Name is missing, use Author Name
    let firstName = (mainInfo.firstName && mainInfo.firstName.toString().trim() !== "") 
                    ? mainInfo.firstName 
                    : author;
    
    if (!email) continue; 
    
    const isDropped = launchStatus.includes("dropped") || launchStatus.includes("bad") || launchStatus.includes("untested");
    
    const isReady = (status) => status !== "Scheduled" && status !== "Sent" && status !== "Draft ready" && status !== "Timer Set" && status !== "Timer Set Rev";
    
    // --- 6-HOUR TIMER EXECUTION BLOCK ---
    if (isDelayedRun) {
      if (psRow[vendorCol] === "Timer Set") {
        createDraft(email, `Vendor Onboarding for ${title}`, firstName, 'vendor', title, link, i, vendorCol, null, ccMail, revLink, argus);
      }
      if (psRow[revStatementEmailCol] === "Timer Set Rev") {
        createDraft(email, `Revenue Statement for ${title}`, firstName, 'revStatement_workedWell_payment', title, link, i, revStatementEmailCol, null, ccMail, revLink, argus);
      }
      continue; 
    }
    // ------------------------------------

    // Welcome Email (Today based on Contract Signing Date in Main Sheet)
    if (!isDropped && isToday(mainInfo.contractSigned)) {
      if (isReady(psRow[welcomeCol])) {
        createDraft(email, `Welcome to Pocket FM - here's what happens next`, firstName, 'welcome', title, link, i, welcomeCol, null, ccMail, revLink, argus);
        psSheet.getRange(i + 1, vendorCol + 1).setValue("Timer Set");
        if (!triggerSet) {
          ScriptApp.newTrigger("runDelayedDrafts").timeBased().after(6 * 60 * 60 * 1000).create();
          triggerSet = true;
        }
      } else {
        Logger.log("SKIPPED (Welcome Email): Status is already processed for " + title + " (Current status: " + psRow[welcomeCol] + ")");
      }
    } else if (!isDropped && !isToday(mainInfo.contractSigned) && mainInfo.contractSigned) {
        Logger.log("SKIPPED (Welcome Email): Contract date for " + title + " is " + mainInfo.contractSigned + " which is not today.");
    }
    
    // MG Payout Initiated (Today based on vendor lifecycle exit in Main Sheet)
    if (!isDropped && isToday(mainInfo.vendorLifecycleExited) && isReady(psRow[mgPayoutInitiatedCol])) {
      createDraft(email, `Payment Initiated: Minimum Guarantee for ${title}`, firstName, 'mgInitiated', title, link, i, mgPayoutInitiatedCol, null, ccMail, revLink, argus);
    }
    
    // MG Payout Confirmation (Today based on MG payout exit in Main Sheet)
    if (!isDropped && isToday(mainInfo.mgPayoutExited) && isReady(psRow[mgPayoutConfirmationCol])) {
      createDraft(email, `Pocket FM: Your Minimum Guarantee Payment Has Been Processed`, firstName, 'mgConfirmed', title, link, i, mgPayoutConfirmationCol, null, ccMail, revLink, argus);
    }
    
    let isShowLinkBlank = (link === "" || link === null || link === undefined);
    if (!isDropped && isDaysAgo(mainInfo.mgPayoutExited, 15) && isShowLinkBlank && isReady(psRow[checkIn1Col])) {
      createDraft(email, `We'd love your thoughts on ${title}`, firstName, 'checkIn1', title, link, i, checkIn1Col, null, ccMail, revLink, argus);
    }
    
    if (!isDropped && isDaysAgo(mainInfo.mgPayoutExited, 30) && isShowLinkBlank && isReady(psRow[checkIn2Col])) {
      createDraft(email, `Pocket FM: A quick update on your show: ${title}`, firstName, 'checkIn2', title, link, i, checkIn2Col, null, ccMail, revLink, argus);
    }
    
    if (!isDropped && isReady(psRow[launchCol])) {
      if (link && link !== "") {
        createDraft(email, `Your Pocket FM Show Is Now Live`, firstName, 'launch', title, link, i, launchCol, null, ccMail, revLink, argus);
      } else if (psRow[launchCol] === "Ready No AI") {
        createDraft(email, `We are working on ${title}`, firstName, 'launch_no_ai', title, link, i, launchCol, null, ccMail, revLink, argus);
      }
    }
    
    if (isToday(psRow[revStatementDueCol]) && isReady(psRow[revStatementEmailCol])) {
      if (launchStatus.includes("testing_pgc") || launchStatus.includes("launched")) {
         createDraft(email, `Content Update for ${title}`, firstName, 'revStatement_workedWell_content', title, link, i, revStatementEmailCol, null, ccMail, revLink, argus);
         psSheet.getRange(i + 1, revStatementEmailCol + 1).setValue("Timer Set Rev");
         if (!triggerSet) {
           ScriptApp.newTrigger("runDelayedDrafts").timeBased().after(6 * 60 * 60 * 1000).create();
           triggerSet = true;
         }
      }
      else if (launchStatus.includes("dropped")) {
         createDraft(email, `Pocket FM: An Update on ${title}`, firstName, 'revStatement_didntWorkWell', title, link, i, revStatementEmailCol, null, ccMail, revLink, argus);
      }
      else if (launchStatus.includes("bad") || launchStatus.includes("untested")) {
         psSheet.getRange(i + 1, revStatementEmailCol + 1).setValue("Review - No email trigger");
      }
    }
  }
}

// Handler function that Google's servers will run automatically 6 hours later
function runDelayedDrafts() {
  processOutreachQueue(true);
}

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

function getBody(type, firstName, title, link, grammar, revLink, argus) {
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
        const revHrefLaunch = revLink ? revLink : "#";
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Exciting news! Your work <b>${title}</b> is now live on Pocket FM!
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
          Please also find attached your quarterly revenue statement, which includes a breakdown of your show's performance for the reporting period.<br>
          <table border="0" cellspacing="0" cellpadding="0" style="margin-top: 10px; margin-bottom: 10px;">
            <tr>
              <td align="center" style="border-radius: 6px; background-color: #E51A4D;">
                <a href="${revHrefLaunch}" target="_blank" style="font-size: 16px; font-weight: bold; color: #ffffff; text-decoration: none; border-radius: 6px; padding: 12px 24px; border: 1px solid #E51A4D; display: inline-block;">Access Revenue Statements</a>
              </td>
            </tr>
          </table>
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
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We're sharing the latest performance update for your licensed series, <b>${title}</b>, on Pocket FM. (Pocket FM App Name: <b>${title}</b>) Attached, you'll find your revenue statement for this quarter, which provides a breakdown of your earnings for the reporting period, along with a snapshot of how your show has been performing.
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
          <b>Invoice template for the revenue share payment</b><br>
          Please share an invoice for the due amount for us to process the payout. The invoice must include the details provided in your onboarding guidelines.
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

    }
  }

// -------------------------------------------------------------
// STATUS SYNC FUNCTION (RUNS EVERY HOUR OR MANUALLY)
// -------------------------------------------------------------
function syncSentEmails() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  const allSheets = spreadsheet.getSheets();
  let sheet = null;
  let queueSheet = null;
  
  allSheets.forEach(s => {
    let sName = s.getName().toLowerCase().trim();
    if (sName.includes("post-sales tracker") || sName.includes("post sales tracker") || sName.includes("post sale comms tracker")) sheet = s;
    else if (sName === "queue") queueSheet = s;
  });
  
  if (!queueSheet || !sheet) return;

  const qData = queueSheet.getDataRange().getValues();
  
  for (let i = 1; i < qData.length; i++) {
    let qStatus = qData[i][8]; // Column I (Status)
    let queueId = qData[i][0]; // Column A (Queue ID)
    let subject = qData[i][4]; // Column E (Subject)
    let trackerRow = qData[i][9]; // Column J (Tracker Row IDs)
    
    // Only check if it's marked as Draft Ready
    if (qStatus === "Draft Ready" || qStatus === "Ready") {
      let subject = qData[i][4]; // Column E (Subject)
      
      // 1. Search Gmail for ALL sent emails with this exact Subject (Indexed instantly)
      let threads = GmailApp.search(`in:sent subject:"${subject}"`);
      
      let foundMessage = null;
      let cleanId = queueId.replace(/-/g, "");
      let trackingStr = "Ref" + cleanId;
      
      // 2. Loop through all found threads and messages manually to bypass Gmail's HTML search limitations
      for (let t = 0; t < threads.length; t++) {
        let messages = threads[t].getMessages();
        for (let m = 0; m < messages.length; m++) {
          let msg = messages[m];
          let body = msg.getBody(); // Get raw HTML
          // 3. If the actual HTML body contains our tracking ID, THIS is the exact email!
          if (body.includes(trackingStr)) {
            foundMessage = msg;
            break;
          }
        }
        if (foundMessage) break;
      }
      
      if (foundMessage) {
        let actualTo = foundMessage.getTo();
        let actualCc = foundMessage.getCc();
        
        // Update Queue with the actual sent data!
        queueSheet.getRange(i + 1, 2).setValue(actualTo); // Column B (Recipient)
        queueSheet.getRange(i + 1, 12).setValue(actualCc); // Column L (CC)
        
        // Mark Queue as Sent
        queueSheet.getRange(i + 1, 9).setValue("Sent");
        
        // Mark Tracker as Sent (Replaces 'Ready' with 'Sent' for this row)
        if (trackerRow) {
           let tRowData = sheet.getRange(trackerRow, 1, 1, sheet.getLastColumn()).getValues()[0];
           for (let c = 0; c < tRowData.length; c++) {
             if (tRowData[c] === "Ready" || tRowData[c] === "Draft ready") {
               sheet.getRange(trackerRow, c + 1).setValue("Sent");
             }
           }
        }
      }
    }
  }
}

function debugGmailSearch() {
  let subject = "Your Pocket FM Show Is Now Live";
  let threads = GmailApp.search(`in:sent subject:"${subject}"`);
  Logger.log("Found " + threads.length + " threads for subject: " + subject);
  
  if (threads.length > 0) {
    let messages = threads[0].getMessages();
    Logger.log("Thread 0 has " + messages.length + " messages");
    for (let m = 0; m < messages.length; m++) {
      let msg = messages[m];
      Logger.log("Message " + m + " To: " + msg.getTo() + " CC: " + msg.getCc());
      let body = msg.getBody();
      let match = body.match(/Ref[a-zA-Z0-9]+/);
      Logger.log("Message " + m + " Tracking Ref Found: " + (match ? match[0] : "None"));
    }
  } else {
    Logger.log("No threads found for this subject in the Sent folder.");
  }
}
