/**
 * =============================================================
 * POCKET FM LIFECYCLE CRM AUTOMATION - MODULE 3: DRAFT ENGINE
 * File: DraftEngine.gs (or DraftEngine.js)
 * =============================================================
 * Handles:
 * - Gmail API Draft creation (GmailApp.createDraft)
 * - GMass Queue tab injection with UUID tracking tokens
 * - Live spreadsheet dropdown updates ("Draft Ready" -> Col AB, Col W, Col Y)
 * - Automated timestamp stamping (Col AC, Col X, Col Z, Col AD, Col R)
 * - Sent Mail Synchronization (syncSentEmails)
 */

/**
 * CORE DRAFT CREATOR & SPREADSHEET STATUS UPDATER
 */
function createDraft(rawEmail, subject, firstName, type, title, link, rIdx, cIdx, customSendTime, rawCcMail, revLink, argus, showName = "", optPsSheet = null, optQueueSheet = null, colMappings = {}) {
  const email = cleanEmail(rawEmail);
  const ccMail = cleanCcList(rawCcMail);
  const psSheet = optPsSheet || getPostSalesTrackerSheet();
  const queueSheet = optQueueSheet || getQueueSheet();
  const rowPrefix = (rIdx !== null && rIdx !== undefined) ? `[ROW ${rIdx + 1}] ` : "";

  // 1. Notification Check: Recipient Email ID
  if (!email || email === "" || !isValidEmail(email)) {
    Logger.log(`${rowPrefix}[RECOMMENDED NOTIFICATION] Recipient Email ID is missing: Recipient Email ID is invalid or missing in Master Sheet (Col AB) for "${title}" ("${rawEmail || ''}"). Cannot create draft.`);
    return false;
  }

  // 2. Notification Check: Email Template Selected
  const validTemplates = [
    'welcome', 'vendor', 'mgInitiated', 'mgConfirmed', 
    'checkIn1', 'checkIn2', 'launch', 'launch_no_ai', 
    'authorEdit', 'newsletter',
    'revStatement_workedWell_content', 'revStatement_workedWell_payment', 
    'revStatement_didntWorkWell'
  ];
  if (!type || !validTemplates.includes(type)) {
    Logger.log(`${rowPrefix}[RECOMMENDED NOTIFICATION] Email template not selected: Email template not selected or unrecognized for stage type: "${type}" (Title: "${title}"). Draft creation skipped.`);
    return false;
  }

  // 3. Variable Mapping (Singular vs Plural logic from 'Variable Mapping' tab)
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

  // 4. Map 'type' to the exact Automation Rule Template Name
  let templateName = type;
  if (type === "welcome") templateName = "Welcome Email";
  if (type === "vendor") templateName = "Vendor Onboarding Email";
  if (type === "mgInitiated") templateName = "MG Payment Initiated";
  if (type === "mgConfirmed") templateName = "MG Payment Processed";
  if (type === "checkIn1") templateName = "Personal Check In 1";
  if (type === "checkIn2") templateName = "Personal Check In 2";
  if (type === "launch") templateName = "AI Allowed - Show Launch Announcement";
  if (type === "authorEdit" || type === "newsletter") templateName = "The Author Edit";
  if (type === "revStatement_workedWell_content") templateName = "Content Update - worked well";
  if (type === "revStatement_workedWell_payment") templateName = "Worked Well - Payment-Related Update";
  if (type === "revStatement_didntWorkWell") templateName = "Didnt work well - Content Related Update";

  // 5. Generate Data for Queue
  const queueId = Utilities.getUuid();
  const body = getBody(type, firstName, title, link, grammar, revLink, argus, showName);
  if (!body || body.trim() === "") {
    Logger.log(`${rowPrefix}[RECOMMENDED NOTIFICATION] Email template not selected: Email template body is empty or not defined for stage type: "${type}" (Title: "${title}").`);
    return false;
  }
  const wrappedBody = wrapHtml(body, queueId);

  const sendDate = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy-MM-dd");
  const exactTime = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "hh:mm a"); 
  const sendTime = customSendTime ? customSendTime : exactTime; 
  const ccValue = ccMail ? ccMail : "";

  // 6. Append to Queue Tab
  if (queueSheet) {
    try {
      let senderEmail = "";
      try { senderEmail = Session.getActiveUser().getEmail(); } catch (eUser) {}
      queueSheet.appendRow([
        queueId,
        email, 
        senderEmail, 
        templateName, 
        subject,
        wrappedBody,
        sendDate,
        sendTime,
        "Draft Ready", 
        rIdx + 1, 
        "Yes",
        ccValue
      ]);
    } catch (errQueue) {
      Logger.log(`[QUEUE SHEET WARNING] Failed to append row to Queue sheet: ${errQueue.message}`);
    }
  }

  // 7. Create Gmail Draft
  let draftOptions = { htmlBody: wrappedBody };
  if (ccMail && ccMail !== "") {
    draftOptions.cc = ccMail;
  }
  let draftSuccess = false;
  try {
    GmailApp.createDraft(email, subject, "", draftOptions);
    draftSuccess = true;
  } catch (err) {
    Logger.log(`[WARNING] Gmail draft creation failed for "${title}" (${email}): ${err.message}`);
  }

  if (!draftSuccess) {
    Logger.log(`[SKIPPED] Draft was NOT created in mailbox for "${title}". Dates and statuses will not be updated.`);
    return false;
  }

  // 8. Update Sheet Dropdowns & Timestamps
  if (psSheet && rIdx >= 0) {
    let statusValue = "Draft Ready";
    if (type === "mgConfirmed" || cIdx === colMappings.mgPayoutConfirmationCol) {
      statusValue = "Draft ready";
    } else if (type === "checkIn1" || type === "checkIn2" || cIdx === colMappings.checkIn1Col || cIdx === colMappings.checkIn2Col) {
      statusValue = "draft ready";
    }

    if (cIdx >= 0) {
      psSheet.getRange(rIdx + 1, cIdx + 1).setValue(statusValue);
    }

    // Launch dropdown & status
    if (type === "launch" || type === "launch_no_ai") {
      let launchSentCol = colMappings.launchSentCol !== undefined ? colMappings.launchSentCol : 27; // Col AB
      let launchCol = colMappings.launchCol !== undefined ? colMappings.launchCol : 26; // Col AA
      let launchSentDateCol = colMappings.launchSentDateCol !== undefined ? colMappings.launchSentDateCol : 28; // Col AC

      psSheet.getRange(rIdx + 1, launchSentCol + 1).setValue("Draft Ready");
      let curAAFormula = psSheet.getRange(rIdx + 1, launchCol + 1).getFormula();
      if (!curAAFormula) {
        psSheet.getRange(rIdx + 1, launchCol + 1).setValue("Draft Ready");
      }
      psSheet.getRange(rIdx + 1, launchSentDateCol + 1).setValue(new Date());
    }

    // Newsletter dropdown & date
    if (type === "authorEdit" || type === "newsletter") {
      let newsletterCol = colMappings.newsletterCol !== undefined ? colMappings.newsletterCol : 29; // Col AD
      let newsletterSentDateCol = colMappings.newsletterSentDateCol !== undefined ? colMappings.newsletterSentDateCol : 30;
      psSheet.getRange(rIdx + 1, newsletterCol + 1).setValue("Draft Ready");
      if (newsletterSentDateCol > -1) {
        psSheet.getRange(rIdx + 1, newsletterSentDateCol + 1).setValue(new Date());
      }
    }

    // Feedback Mail Date (Col V) for MG Confirmed
    if (type === "mgConfirmed" || cIdx === colMappings.mgPayoutConfirmationCol) {
      let feedbackMailDateCol = colMappings.feedbackMailDateCol !== undefined ? colMappings.feedbackMailDateCol : 21;
      if (feedbackMailDateCol > -1) {
        psSheet.getRange(rIdx + 1, feedbackMailDateCol + 1).setValue(new Date());
      }
    }

    // Check-In 1 Date (Col X)
    if (type === "checkIn1" || cIdx === colMappings.checkIn1Col) {
      let checkIn1DateCol = colMappings.checkIn1DateCol !== undefined ? colMappings.checkIn1DateCol : 23;
      if (checkIn1DateCol > -1) {
        psSheet.getRange(rIdx + 1, checkIn1DateCol + 1).setValue(new Date());
      }
    }

    // Check-In 2 Date (Col Z)
    if (type === "checkIn2" || cIdx === colMappings.checkIn2Col) {
      let checkIn2DateCol = colMappings.checkIn2DateCol !== undefined ? colMappings.checkIn2DateCol : 25;
      if (checkIn2DateCol > -1) {
        psSheet.getRange(rIdx + 1, checkIn2DateCol + 1).setValue(new Date());
      }
    }
  }

  Logger.log(`SUCCESS: Created draft for "${title}" (Type: ${type})`);
  return true;
}

/**
 * STATUS SYNC FUNCTION (RUNS EVERY HOUR OR MANUALLY):
 * Scans Gmail sent threads, matches Ref tracking IDs, and updates status from "Draft Ready" -> "Sent"
 * Skips blank queue rows.
 */
function syncSentEmails() {
  const sheet = getPostSalesTrackerSheet();
  const queueSheet = getQueueSheet();
  
  if (!queueSheet || !sheet) return;

  const qData = queueSheet.getDataRange().getValues();
  
  for (let i = 1; i < qData.length; i++) {
    let qStatus = qData[i][8]; // Column I (Status)
    let queueId = qData[i][0]; // Column A (Queue ID)
    let subject = qData[i][4]; // Column E (Subject)
    let trackerRow = qData[i][9]; // Column J (Tracker Row IDs)
    
    // Skip blank or unpopulated queue rows
    if (!queueId || !subject || !qStatus) continue;
    
    // Only check if it's marked as Draft Ready
    if (qStatus === "Draft Ready" || qStatus === "Ready") {
      let threads = GmailApp.search(`in:sent subject:"${subject}"`);
      let foundMessage = null;
      let cleanId = queueId.toString().replace(/-/g, "");
      let trackingStr = "Ref" + cleanId;
      
      for (let t = 0; t < threads.length; t++) {
        let messages = threads[t].getMessages();
        for (let m = 0; m < messages.length; m++) {
          let msg = messages[m];
          let body = msg.getBody();
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
        
        queueSheet.getRange(i + 1, 2).setValue(actualTo);
        queueSheet.getRange(i + 1, 12).setValue(actualCc);
        queueSheet.getRange(i + 1, 9).setValue("Sent");
        
        if (trackerRow) {
           let tRowData = sheet.getRange(trackerRow, 1, 1, sheet.getLastColumn()).getValues()[0];
           const sHeaders = sheet.getRange(3, 1, 1, sheet.getLastColumn()).getValues()[0];
           const sFindCol = (name) => sHeaders.findIndex(h => h.toString().toLowerCase().includes(name.toLowerCase()));
           const sMgConfCol = sFindCol("MG Payout Confirmation");
           const sFeedbackDateCol = sFindCol("Feedback Mail Date");
           const sLaunchCol = sFindCol("Show Launch Announcement");
           const sLaunchSentCol = sHeaders.findIndex(h => {
             let s = h.toString().toLowerCase().trim();
             return (s.includes("launch") && s.includes("announcement") && s.includes("sent") && !s.includes("date")) ||
                    (s.includes("launch") && s.includes("email sent") && !s.includes("date"));
           });
           const sLaunchSentDateCol = sHeaders.findIndex(h => {
             let s = h.toString().toLowerCase().trim();
             return (s.includes("launch") && s.includes("sent") && s.includes("date")) ||
                    (s.includes("launch") && s.includes("announcement") && s.includes("date"));
           });

           for (let c = 0; c < tRowData.length; c++) {
             let cellStr = (tRowData[c] || "").toString().toLowerCase().trim();
             if (cellStr === "ready" || cellStr === "draft ready") {
               sheet.getRange(trackerRow, c + 1).setValue("Sent");
               if (c === sMgConfCol && sFeedbackDateCol !== -1) {
                 const sentDate = new Date();
                 sheet.getRange(trackerRow, sFeedbackDateCol + 1).setValue(sentDate);
                 Logger.log(`[SYNC] Captured Feedback Mail Date in Col ${sFeedbackDateCol + 1} for row ${trackerRow}: ${sentDate}`);
               }
               if (c === sLaunchCol) {
                 if (sLaunchSentCol !== -1) {
                   sheet.getRange(trackerRow, sLaunchSentCol + 1).setValue("Sent");
                 }
                 if (sLaunchSentDateCol !== -1) {
                   const sentDate = new Date();
                   sheet.getRange(trackerRow, sLaunchSentDateCol + 1).setValue(sentDate);
                   Logger.log(`[SYNC] Captured Launch Sent Date in Col ${sLaunchSentDateCol + 1} for row ${trackerRow}: ${sentDate}`);
                 }
               }
             }
           }
        }
      }
    }
  }
}

/**
 * DEBUG HELPER FOR SENT GMAIL SEARCH
 */
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

/**
 * TEST FUNCTION: WELCOME EMAIL DRAFT
 * Generates a real test draft in user's Gmail Drafts folder.
 */
function testWelcomeEmailDraft() {
  const myEmail = Session.getActiveUser().getEmail();
  const testTitle = "A Shade of Vampire Series";
  const testFirstName = "Bella";
  const testLink = "https://pocketfm.onelink.me/2IE7/qgh3r7hu";

  const grammar = { work: "work", is: "is", has: "has", title: "title", this: "this", it: "it", its: "its" };
  const queueId = Utilities.getUuid();
  const bodyContent = getBody('welcome', testFirstName, testTitle, testLink, grammar);
  const wrappedBody = wrapHtml(bodyContent, queueId);
  const subject = "Welcome to Pocket FM - here's what happens next";

  GmailApp.createDraft(myEmail, subject, "", { htmlBody: wrappedBody });
  Logger.log(`SUCCESS: Test Welcome Email Draft created with subject "${subject}" sent to: ${myEmail}`);
}

/**
 * TEST FUNCTION: VENDOR ONBOARDING EMAIL DRAFT
 * Generates a real test draft in user's Gmail Drafts folder with W-9, VRF, COI table & Drive folder button.
 */
function testVendorOnboardingDraft() {
  const myEmail = Session.getActiveUser().getEmail();
  const testTitle = "A Shade of Vampire Series";
  const testFirstName = "Bella";
  const testLink = "https://pocketfm.onelink.me/2IE7/qgh3r7hu";

  const grammar = { work: "work", is: "is", has: "has", title: "title", this: "this", it: "it", its: "its" };
  const queueId = Utilities.getUuid();
  const bodyContent = getBody('vendor', testFirstName, testTitle, testLink, grammar);
  const wrappedBody = wrapHtml(bodyContent, queueId);
  const subject = `Vendor Onboarding for ${testTitle}`;

  GmailApp.createDraft(myEmail, subject, "", { htmlBody: wrappedBody });
  Logger.log(`SUCCESS: Test Vendor Onboarding Draft created with subject "${subject}" sent to: ${myEmail}`);
}

/**
 * TEST FUNCTION: MG PAYOUT DRAFTS (INITIATED & CONFIRMED)
 */
function testMgPayoutDrafts() {
  const myEmail = Session.getActiveUser().getEmail();
  const testTitle = "A Shade of Vampire Series";
  const testFirstName = "Bella";
  const grammar = { work: "work", is: "is", has: "has", title: "title", this: "this", it: "it", its: "its" };

  // 1. MG Initiated
  const qId1 = Utilities.getUuid();
  const body1 = getBody('mgInitiated', testFirstName, testTitle, "", grammar);
  const wrapped1 = wrapHtml(body1, qId1);
  const subj1 = `Payment Initiated: Minimum Guarantee for ${testTitle}`;
  GmailApp.createDraft(myEmail, subj1, "", { htmlBody: wrapped1 });
  Logger.log(`SUCCESS: Test MG Initiated Draft created with subject "${subj1}" sent to: ${myEmail}`);

  // 2. MG Confirmed
  const qId2 = Utilities.getUuid();
  const body2 = getBody('mgConfirmed', testFirstName, testTitle, "", grammar);
  const wrapped2 = wrapHtml(body2, qId2);
  const subj2 = "Pocket FM: Your Minimum Guarantee Payment Has Been Processed";
  GmailApp.createDraft(myEmail, subj2, "", { htmlBody: wrapped2 });
  Logger.log(`SUCCESS: Test MG Confirmed Draft created with subject "${subj2}" sent to: ${myEmail}`);
}

/**
 * TEST FUNCTION: WELCOME & VENDOR ONBOARDING RUNNER
 */
function testWelcomeAndVendorDraft() {
  Logger.log("\n=======================================================");
  Logger.log("RUNNING WELCOME & VENDOR ONBOARDING TEST");
  Logger.log("=======================================================");
  testWelcomeEmailDraft();
  testVendorOnboardingDraft();
  Logger.log("=======================================================\n");
  try {
    getSpreadsheet().toast("Test Welcome & Vendor Onboarding drafts created in Gmail Drafts!", "Tests Complete", 5);
  } catch (e) {}
}

/**
 * TEST FUNCTION: NEWSLETTER DRAFT
 */
function testNewsletterDraft() {
  const myEmail = Session.getActiveUser().getEmail();
  const testTitle = "The Shadow Heir";
  const testFirstName = "Elena";
  const testLink = "https://pocketfm.com/show/shadow-heir";
  
  const grammar = { work: "work", is: "is", has: "has", title: "title", this: "this", it: "it", its: "its" };
  const queueId = Utilities.getUuid();
  const bodyContent = getBody('authorEdit', testFirstName, testTitle, testLink, grammar);
  const wrappedBody = wrapHtml(bodyContent, queueId);
  const subject = "What’s new at Pocket FM + a few things worth knowing";

  GmailApp.createDraft(myEmail, subject, "", { htmlBody: wrappedBody });
  Logger.log(`SUCCESS: Test Newsletter Draft created with subject "${subject}" sent to: ${myEmail}`);
}

/**
 * TEST FUNCTION: REVENUE STATEMENT WITH ARGUS METRICS
 */
function testRevenueStatementDraft() {
  const ss = getSpreadsheet();
  const myEmail = Session.getActiveUser().getEmail();
  
  const argusSheet = getArgusSheet(ss);
  let sampleMetrics = {
    duration: "56.8 hours",
    ldau: "159.2K listeners",
    comments: "164",
    ratings: "4.6",
    reviews: "28",
    hours: "N/A"
  };
  let testTitle = "A Shade of Vampire Series";
  let testShowName = "A Shade of Vampire";
  let testFirstName = "Bella";
  let testRevLink = "https://drive.google.com/drive/folders/sample-revenue-statement";

  if (argusSheet) {
    const aData = argusSheet.getDataRange().getValues();
    if (aData.length > 1) {
      const aHeaders = aData[0];
      const aFindCol = (name) => aHeaders.findIndex(h => h.toString().toLowerCase().includes(name.toLowerCase()));
      const aTitleCol = aFindCol("Title");
      const aShowNameCol = aFindCol("Show Name");
      const aDurCol = aFindCol("Duration");
      const aLdauCol = aFindCol("Plays") > -1 ? aFindCol("Plays") : aFindCol("LDAU");
      const aCommentsCol = aFindCol("Comment");
      const aRatingsCol = aFindCol("Rating");
      const aReviewsCol = aFindCol("Review");

      for (let j = 1; j < aData.length; j++) {
        let rowTitle = aTitleCol > -1 ? aData[j][aTitleCol] : "";
        if (rowTitle && rowTitle.toString().trim() !== "") {
          testTitle = rowTitle.toString().trim();
          testShowName = (aShowNameCol > -1 && aData[j][aShowNameCol]) ? aData[j][aShowNameCol].toString().trim() : testTitle;
          let dur = aDurCol > -1 ? aData[j][aDurCol] : "";
          let ldau = aLdauCol > -1 ? aData[j][aLdauCol] : "";
          let comments = aCommentsCol > -1 ? aData[j][aCommentsCol] : "";
          let ratings = aRatingsCol > -1 ? aData[j][aRatingsCol] : "";
          let reviews = aReviewsCol > -1 ? aData[j][aReviewsCol] : "";

          sampleMetrics = {
            duration: (dur !== "" && dur !== null && dur !== undefined) ? dur + " hours" : "N/A",
            ldau: (ldau !== "" && ldau !== null && ldau !== undefined) ? (ldau.toString().toLowerCase().includes("listener") || ldau.toString().toLowerCase().includes("play") ? ldau.toString() : ldau + " listeners") : "N/A",
            comments: (comments !== "" && comments !== null && comments.toString() !== "0") ? (!isNaN(comments) ? Math.round(Number(comments)).toString() : comments.toString()) : "No comments",
            ratings: (ratings !== "" && ratings !== null && ratings.toString() !== "0") ? ratings.toString() : "No ratings",
            reviews: (reviews !== "" && reviews !== null && reviews.toString() !== "0") ? (!isNaN(reviews) ? Math.round(Number(reviews)).toString() : reviews.toString()) : "No reviews",
            hours: "N/A"
          };
          break;
        }
      }
    }
  }

  const grammar = { work: "work", is: "is", has: "has", title: "title", this: "this", it: "it", its: "its" };
  
  // Draft 1: Content Update
  const queueId1 = Utilities.getUuid();
  const bodyContent1 = getBody('revStatement_workedWell_content', testFirstName, testTitle, "", grammar, testRevLink, sampleMetrics, testShowName);
  const wrappedBody1 = wrapHtml(bodyContent1, queueId1);
  const subject1 = `Content Update for ${testTitle}`;
  GmailApp.createDraft(myEmail, subject1, "", { htmlBody: wrappedBody1 });
  Logger.log(`SUCCESS [Draft 1]: Created "${subject1}" with Argus metrics for "${testTitle}"`);

  // Draft 2: Payment Update
  const queueId2 = Utilities.getUuid();
  const bodyContent2 = getBody('revStatement_workedWell_payment', testFirstName, testTitle, "", grammar, testRevLink, sampleMetrics, testShowName);
  const wrappedBody2 = wrapHtml(bodyContent2, queueId2);
  const subject2 = "Pocket FM: Your earnings are waiting for you!";
  GmailApp.createDraft(myEmail, subject2, "", { htmlBody: wrappedBody2 });
  Logger.log(`SUCCESS [Draft 2]: Created "${subject2}" with invoice template table`);
}
