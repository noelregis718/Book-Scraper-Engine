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
        optPsSheet ? optPsSheet.getName() : "Post-Sales Tracker",
        ccValue,
        cIdx !== undefined && cIdx !== null ? cIdx + 1 : "",
        type
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

    // Launch dropdown & status: ONLY mark "Draft Ready". DO NOT stamp Sent Date until email is actually sent!
    if (type === "launch" || type === "launch_no_ai") {
      let launchSentCol = colMappings.launchSentCol !== undefined ? colMappings.launchSentCol : 27; // Col AB
      let launchCol = colMappings.launchCol !== undefined ? colMappings.launchCol : 26; // Col AA

      psSheet.getRange(rIdx + 1, launchSentCol + 1).setValue("Draft Ready");
      let curAAFormula = psSheet.getRange(rIdx + 1, launchCol + 1).getFormula();
      if (!curAAFormula) {
        psSheet.getRange(rIdx + 1, launchCol + 1).setValue("Draft Ready");
      }
      // NOTE: Launch Sent Date (Col AC) is left BLANK. Stamped by syncSentEmails() upon actual dispatch!
    }

    // Newsletter dropdown: ONLY mark "Draft Ready". DO NOT stamp Sent Date until email is actually sent!
    if (type === "authorEdit" || type === "newsletter") {
      let newsletterCol = colMappings.newsletterCol !== undefined ? colMappings.newsletterCol : 29; // Col AD
      psSheet.getRange(rIdx + 1, newsletterCol + 1).setValue("Draft Ready");
      // NOTE: Newsletter Sent Date is left BLANK. Stamped by syncSentEmails() upon actual dispatch!
    }

    // NOTE: Feedback Mail Date (Col V), Check-In 1 Date (Col X), and Check-In 2 Date (Col Z) are left BLANK here.
    // They are stamped strictly by syncSentEmails() with the actual timestamp when the email is sent from Gmail!
  }

  Logger.log(`SUCCESS: Created draft for "${title}" (Type: ${type})`);
  return true;
}

/**
 * TARGETED SENT MAIL SYNCHRONIZER (MANUAL OR AUTOMATED TRIGGER):
 * Scans Gmail sent threads for emails with Ref tracking tokens or matching subjects.
 * Flips spreadsheet status strictly when the drafted email is actually SENT from Gmail Drafts folder.
 * Accurately stamps the true send timestamp in the corresponding Date column!
 */
function syncSentEmails() {
  Logger.log("==================================================================");
  Logger.log("[START] Running Sent Mail Synchronizer (Draft Ready -> Sent)...");
  Logger.log("==================================================================");

  const psSheet = getPostSalesTrackerSheet();
  const mainSheet = getMainTrackerSheet();
  const queueSheet = getQueueSheet();
  
  if (!queueSheet) {
    Logger.log("[WARNING] Queue sheet not found. Cannot synchronize sent emails.");
    return { success: false, syncedCount: 0 };
  }

  const qData = queueSheet.getDataRange().getValues();
  if (qData.length <= 1) {
    Logger.log("[INFO] Queue sheet is empty.");
    return { success: true, syncedCount: 0 };
  }

  // Preload headers for Post-Sales Tracker to dynamically resolve target columns
  let psHeaders = [];
  let sFindCol = () => -1;
  let sFeedbackDateCol = -1;
  let sLaunchCol = -1;
  let sLaunchSentCol = -1;
  let sLaunchSentDateCol = -1;
  let sCheckIn1Col = -1;
  let sCheckIn1DateCol = -1;
  let sCheckIn2Col = -1;
  let sCheckIn2DateCol = -1;
  let sNewsletterCol = -1;
  let sNewsletterDateCol = -1;
  let sMgConfCol = -1;

  if (psSheet) {
    psHeaders = psSheet.getRange(3, 1, 1, Math.max(psSheet.getLastColumn(), 45)).getValues()[0];
    sFindCol = (name) => psHeaders.findIndex(h => h.toString().toLowerCase().includes(name.toLowerCase()));
    
    sMgConfCol = sFindCol("MG Payout Confirmation");
    sFeedbackDateCol = sFindCol("Feedback Mail Date");
    
    sLaunchCol = sFindCol("Show Launch Announcement Status");
    if (sLaunchCol === -1) sLaunchCol = 26; // Col AA
    
    sLaunchSentCol = psHeaders.findIndex(h => {
      let s = h.toString().toLowerCase().trim();
      return (s.includes("launch") && s.includes("sent") && !s.includes("date")) ||
             (s.includes("launch") && s.includes("announcement sent"));
    });
    if (sLaunchSentCol === -1) sLaunchSentCol = 27; // Col AB
    
    sLaunchSentDateCol = psHeaders.findIndex(h => {
      let s = h.toString().toLowerCase().trim();
      return (s.includes("launch") && s.includes("sent") && s.includes("date")) ||
             (s.includes("launch") && s.includes("announcement") && s.includes("date"));
    });
    if (sLaunchSentDateCol === -1) sLaunchSentDateCol = 28; // Col AC

    sCheckIn1Col = psHeaders.findIndex(h => h.toString().toLowerCase().includes("15 days") && !h.toString().toLowerCase().includes("newsletter") && !h.toString().toLowerCase().includes("date"));
    if (sCheckIn1Col === -1) sCheckIn1Col = 22; // Col W
    sCheckIn1DateCol = psHeaders.findIndex(h => h.toString().toLowerCase().includes("15 days") && !h.toString().toLowerCase().includes("newsletter") && h.toString().toLowerCase().includes("date"));
    if (sCheckIn1DateCol === -1) sCheckIn1DateCol = 23; // Col X

    sCheckIn2Col = psHeaders.findIndex(h => h.toString().toLowerCase().includes("30 days") && !h.toString().toLowerCase().includes("date"));
    if (sCheckIn2Col === -1) sCheckIn2Col = 24; // Col Y
    sCheckIn2DateCol = psHeaders.findIndex(h => h.toString().toLowerCase().includes("30 days") && h.toString().toLowerCase().includes("date"));
    if (sCheckIn2DateCol === -1) sCheckIn2DateCol = 25; // Col Z

    sNewsletterCol = psHeaders.findIndex(h => h.toString().toLowerCase().includes("newsletter") && !h.toString().toLowerCase().includes("date"));
    if (sNewsletterCol === -1) sNewsletterCol = 29; // Col AD
    sNewsletterDateCol = psHeaders.findIndex(h => h.toString().toLowerCase().includes("newsletter") && h.toString().toLowerCase().includes("date"));
    if (sNewsletterDateCol === -1) sNewsletterDateCol = 30; // Col AE
  }

  let syncedCount = 0;

  for (let i = 1; i < qData.length; i++) {
    let queueId = qData[i][0]; // Column A (Queue ID)
    let recipient = qData[i][1]; // Column B (Recipient Email)
    let templateName = qData[i][3]; // Column D (Template / Stage)
    let subject = qData[i][4]; // Column E (Subject)
    let qStatus = qData[i][8]; // Column I (Status)
    let trackerRow = parseInt(qData[i][9]); // Column J (Tracker Row Index, 1-based)
    let targetSheetName = qData[i][10] || "Post-Sales Tracker";
    let loggedStatusCol = qData[i][12] ? parseInt(qData[i][12]) : null;
    let stageType = qData[i][13] || "";

    // Skip empty or already sent queue entries
    if (!queueId || !subject || !qStatus) continue;
    let curStatus = qStatus.toString().toLowerCase().trim();
    if (curStatus !== "draft ready" && curStatus !== "ready") {
      continue;
    }

    // Search Gmail in:sent for this specific message using Ref tracking token
    let cleanId = queueId.toString().replace(/-/g, "");
    let trackingStr = "Ref" + cleanId;
    let searchQuery = `in:sent "${trackingStr}"`;
    let threads = GmailApp.search(searchQuery);

    // Fallback search by recipient and exact subject if tracking token search yields nothing
    if ((!threads || threads.length === 0) && recipient && subject) {
      let cleanSubject = subject.replace(/["\\]/g, "");
      threads = GmailApp.search(`in:sent to:${recipient} subject:"${cleanSubject}"`);
    }

    let foundMessage = null;
    if (threads && threads.length > 0) {
      for (let t = 0; t < threads.length; t++) {
        let messages = threads[t].getMessages();
        for (let m = 0; m < messages.length; m++) {
          let msg = messages[m];
          let body = msg.getBody();
          if (body.includes(trackingStr) || (msg.getTo().toLowerCase().includes(recipient.toLowerCase()) && msg.getSubject() === subject)) {
            foundMessage = msg;
            break;
          }
        }
        if (foundMessage) break;
      }
    }

    // IF FOUND IN SENT FOLDER: The user clicked Send in Gmail!
    if (foundMessage) {
      const actualSentDate = foundMessage.getDate();
      const actualTo = foundMessage.getTo();
      const actualCc = foundMessage.getCc();

      // 1. Mark Queue row as Sent with actual timestamp
      queueSheet.getRange(i + 1, 2).setValue(actualTo);
      if (actualCc) queueSheet.getRange(i + 1, 12).setValue(actualCc);
      queueSheet.getRange(i + 1, 9).setValue("Sent");
      queueSheet.getRange(i + 1, 7).setValue(actualSentDate); // Record actual sent timestamp in Queue

      // 2. Resolve Target Sheet (Post-Sales Tracker vs Lifecycle Master)
      let targetSheet = psSheet;
      if (targetSheetName.toString().toLowerCase().includes("master") || targetSheetName.toString().toLowerCase().includes("lifecycle")) {
        targetSheet = mainSheet || psSheet;
      }

      if (targetSheet && trackerRow > 0) {
        // Update direct logged status column if recorded
        if (loggedStatusCol && loggedStatusCol > 0) {
          targetSheet.getRange(trackerRow, loggedStatusCol).setValue("Sent");
        }

        const tName = (templateName || "").toString().toLowerCase();
        const sType = (stageType || "").toString().toLowerCase();

        // Stage 4: MG Payout Confirmation -> Mark Sent & Stamp Feedback Mail Date (Col V)
        if (tName.includes("mg payment processed") || tName.includes("mg payout confirmation") || sType === "mgconfirmed") {
          if (sMgConfCol !== -1) targetSheet.getRange(trackerRow, sMgConfCol + 1).setValue("Sent");
          if (sFeedbackDateCol !== -1) {
            targetSheet.getRange(trackerRow, sFeedbackDateCol + 1).setValue(actualSentDate);
            Logger.log(`[SYNC SUCCESS] Row ${trackerRow}: Stamped Feedback Mail Date (Col V) as ${actualSentDate}`);
          }
        }

        // Stage 7: Show Launch Announcement -> Mark Col AB & AA Sent, Stamp Col AC Date
        else if (tName.includes("launch") || sType === "launch" || sType === "launch_no_ai") {
          if (sLaunchSentCol !== -1) targetSheet.getRange(trackerRow, sLaunchSentCol + 1).setValue("Sent");
          if (sLaunchCol !== -1) {
            let formula = targetSheet.getRange(trackerRow, sLaunchCol + 1).getFormula();
            if (!formula) targetSheet.getRange(trackerRow, sLaunchCol + 1).setValue("Sent");
          }
          if (sLaunchSentDateCol !== -1) {
            targetSheet.getRange(trackerRow, sLaunchSentDateCol + 1).setValue(actualSentDate);
            Logger.log(`[SYNC SUCCESS] Row ${trackerRow}: Stamped Launch Sent Date (Col AC) as ${actualSentDate}`);
          }
        }

        // Stage 5: Check-In 1 (15 Days) -> Mark Col W Sent, Stamp Col X Date
        else if (tName.includes("check in 1") || sType === "checkin1") {
          if (sCheckIn1Col !== -1) targetSheet.getRange(trackerRow, sCheckIn1Col + 1).setValue("Sent");
          if (sCheckIn1DateCol !== -1) {
            targetSheet.getRange(trackerRow, sCheckIn1DateCol + 1).setValue(actualSentDate);
            Logger.log(`[SYNC SUCCESS] Row ${trackerRow}: Stamped Check-In 1 Date (Col X) as ${actualSentDate}`);
          }
        }

        // Stage 6: Check-In 2 (30 Days) -> Mark Col Y Sent, Stamp Col Z Date
        else if (tName.includes("check in 2") || sType === "checkin2") {
          if (sCheckIn2Col !== -1) targetSheet.getRange(trackerRow, sCheckIn2Col + 1).setValue("Sent");
          if (sCheckIn2DateCol !== -1) {
            targetSheet.getRange(trackerRow, sCheckIn2DateCol + 1).setValue(actualSentDate);
            Logger.log(`[SYNC SUCCESS] Row ${trackerRow}: Stamped Check-In 2 Date (Col Z) as ${actualSentDate}`);
          }
        }

        // Stage 8: Newsletter (The Author Edit) -> Mark Col AD Sent, Stamp Col AE Date
        else if (tName.includes("author edit") || tName.includes("newsletter") || sType === "newsletter" || sType === "authoredit") {
          if (sNewsletterCol !== -1) targetSheet.getRange(trackerRow, sNewsletterCol + 1).setValue("Sent");
          if (sNewsletterDateCol !== -1) {
            targetSheet.getRange(trackerRow, sNewsletterDateCol + 1).setValue(actualSentDate);
            Logger.log(`[SYNC SUCCESS] Row ${trackerRow}: Stamped Newsletter Sent Date as ${actualSentDate}`);
          }
        }

        // Stage 1 & 2: Welcome & Vendor Onboarding
        else if (tName.includes("welcome")) {
          let sWelcomeCol = sFindCol("Welcome Email");
          if (sWelcomeCol !== -1) targetSheet.getRange(trackerRow, sWelcomeCol + 1).setValue("Sent");
        }
        else if (tName.includes("vendor")) {
          let sVendorCol = sFindCol("Vendor Onboarding");
          if (sVendorCol !== -1) targetSheet.getRange(trackerRow, sVendorCol + 1).setValue("Sent");
        }

        // Stage 9: Quarterly Revenue Statements
        else if (tName.includes("content update") || tName.includes("worked well") || tName.includes("revenue statement") || sType.includes("revstatement")) {
          let revCols = [38, 33, 42]; // 0-based for AM (39), AH (34), AQ (43)
          for (let rc of revCols) {
            if (rc < targetSheet.getLastColumn()) {
              let val = (targetSheet.getRange(trackerRow, rc + 1).getValue() || "").toString().toLowerCase().trim();
              if (val === "draft ready" || val === "ready") {
                targetSheet.getRange(trackerRow, rc + 1).setValue("Sent");
                Logger.log(`[SYNC SUCCESS] Row ${trackerRow}: Updated Revenue Statement in Col ${rc + 1} to 'Sent'`);
              }
            }
          }
        }
      }

      syncedCount++;
      Logger.log(`[SYNC SUCCESS] [ROW ${trackerRow}] Marked ${templateName} as "Sent" (Dispatched at: ${actualSentDate})`);
    }
  }

  try { SpreadsheetApp.flush(); } catch (e) {}

  const summaryMsg = `Sent Mail Sync Complete: ${syncedCount} draft(s) detected as sent and updated to "Sent"!`;
  Logger.log(summaryMsg);
  Logger.log("==================================================================");

  try {
    const activeSs = SpreadsheetApp.getActiveSpreadsheet();
    if (activeSs) activeSs.toast(summaryMsg, "Pocket FM Automation", 5);
  } catch (e) {}

  return { success: true, syncedCount: syncedCount };
}

/**
 * AUTOMATED TIME-DRIVEN TRIGGER INSTALLER:
 * Installs a background trigger to run syncSentEmails() every 10 minutes automatically.
 */
function setupAutoSyncSentTrigger() {
  const triggers = ScriptApp.getProjectTriggers();
  for (let t of triggers) {
    if (t.getHandlerFunction() === 'syncSentEmails') {
      ScriptApp.deleteTrigger(t);
    }
  }
  ScriptApp.newTrigger('syncSentEmails')
    .timeBased()
    .everyMinutes(10)
    .create();
  Logger.log("SUCCESS: Automated 10-Minute Sent Mail Sync Trigger successfully configured!");
  try {
    SpreadsheetApp.getActiveSpreadsheet().toast("Automated 10-Minute Sent Mail Sync Trigger is active!", "Trigger Installed", 5);
  } catch (e) {}
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
  
  let timeStr = "";
  try {
    timeStr = " - " + Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "hh:mm a");
  } catch(e) {}
  const subject = "What’s new at Pocket FM + a few things worth knowing" + timeStr;

  GmailApp.createDraft(myEmail, subject, "", { htmlBody: wrappedBody });
  Logger.log(`SUCCESS: Test Newsletter Draft created with subject "${subject}" sent to: ${myEmail}`);
  return subject;
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
