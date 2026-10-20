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
 * Scans Gmail sent threads for emails with Ref tracking tokens, recipient email, or matching subjects.
 * Dual-Channel Sync:
 *   Channel A: Checks the 'Queue' tab for any pending 'Draft Ready' entries.
 *   Channel B: DIRECT TRACKER SCANNER - Checks Post-Sales Tracker directly for any rows marked 'Draft Ready'.
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
  
  let syncedCount = 0;

  // Helper to normalize strings for robust comparison (handles curly/straight quotes, spacing)
  const norm = (s) => (s || "").toString().toLowerCase().replace(/[’'"`]/g, "'").replace(/[^a-z0-9]/g, " ").replace(/\s+/g, " ").trim();

  // Helper to find header column index across rows 1 to 3
  const resolveHeaders = (sheet) => {
    if (!sheet) return { headers: [], rowIdx: -1 };
    for (let r = 1; r <= 3; r++) {
      let vals = sheet.getRange(r, 1, 1, Math.max(sheet.getLastColumn(), 45)).getValues()[0];
      if (vals.some(v => v.toString().toLowerCase().includes("title") || v.toString().toLowerCase().includes("status") || v.toString().toLowerCase().includes("email"))) {
        return { headers: vals, rowIdx: r };
      }
    }
    return { headers: sheet.getRange(1, 1, 1, Math.max(sheet.getLastColumn(), 45)).getValues()[0], rowIdx: 1 };
  };

  let psRes = resolveHeaders(psSheet);
  let psHeaders = psRes.headers;
  let sFindCol = (name) => psHeaders.findIndex(h => h.toString().toLowerCase().includes(name.toLowerCase()));

  let sTitleCol = sFindCol("title") > -1 ? sFindCol("title") : 2; // Col C
  let sEmailCol = sFindCol("email") > -1 ? sFindCol("email") : (sFindCol("recipient") > -1 ? sFindCol("recipient") : 27); // Col AB or 27

  let sMgConfCol = sFindCol("mg payout confirmation");
  let sFeedbackDateCol = sFindCol("feedback mail date");
  
  let sLaunchCol = sFindCol("show launch announcement status");
  if (sLaunchCol === -1) sLaunchCol = 26; // Col AA
  
  let sLaunchSentCol = psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return (s.includes("launch") && s.includes("sent") && !s.includes("date")) ||
           (s.includes("launch") && s.includes("announcement sent"));
  });
  if (sLaunchSentCol === -1) sLaunchSentCol = 27; // Col AB
  
  let sLaunchSentDateCol = psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return (s.includes("launch") && s.includes("sent") && s.includes("date")) ||
           (s.includes("launch") && s.includes("announcement") && s.includes("date"));
  });
  if (sLaunchSentDateCol === -1) sLaunchSentDateCol = 28; // Col AC

  let sCheckIn1Col = psHeaders.findIndex(h => h.toString().toLowerCase().includes("15 days") && !h.toString().toLowerCase().includes("newsletter") && !h.toString().toLowerCase().includes("date"));
  if (sCheckIn1Col === -1) sCheckIn1Col = 22; // Col W
  let sCheckIn1DateCol = psHeaders.findIndex(h => h.toString().toLowerCase().includes("15 days") && !h.toString().toLowerCase().includes("newsletter") && h.toString().toLowerCase().includes("date"));
  if (sCheckIn1DateCol === -1) sCheckIn1DateCol = 23; // Col X

  let sCheckIn2Col = psHeaders.findIndex(h => h.toString().toLowerCase().includes("30 days") && !h.toString().toLowerCase().includes("date"));
  if (sCheckIn2Col === -1) sCheckIn2Col = 24; // Col Y
  let sCheckIn2DateCol = psHeaders.findIndex(h => h.toString().toLowerCase().includes("30 days") && h.toString().toLowerCase().includes("date"));
  if (sCheckIn2DateCol === -1) sCheckIn2DateCol = 25; // Col Z

  let sNewsletterCol = psHeaders.findIndex(h => h.toString().toLowerCase().includes("newsletter") && !h.toString().toLowerCase().includes("date"));
  if (sNewsletterCol === -1) sNewsletterCol = 29; // Col AD
  let sNewsletterDateCol = psHeaders.findIndex(h => h.toString().toLowerCase().includes("newsletter") && h.toString().toLowerCase().includes("date"));
  if (sNewsletterDateCol === -1) sNewsletterDateCol = 30; // Col AE

  // ==================================================================
  // CHANNEL A: SCAN QUEUE SHEET (IF POPULATED)
  // ==================================================================
  if (queueSheet) {
    const qData = queueSheet.getDataRange().getValues();
    for (let i = 1; i < qData.length; i++) {
      let queueId = qData[i][0];
      let recipient = qData[i][1];
      let templateName = qData[i][3];
      let subject = qData[i][4];
      let qStatus = qData[i][8];
      let trackerRow = parseInt(qData[i][9]);
      let targetSheetName = qData[i][10] || "Post-Sales Tracker";
      let loggedStatusCol = qData[i][12] ? parseInt(qData[i][12]) : null;
      let stageType = qData[i][13] || "";

      if (!queueId || !subject || !qStatus) continue;
      let curStatus = qStatus.toString().toLowerCase().trim();
      if (curStatus !== "draft ready" && curStatus !== "ready") continue;

      let cleanId = queueId.toString().replace(/-/g, "");
      let trackingStr = "Ref" + cleanId;
      let foundMessage = null;

      // 1. Search by token in sent
      let threads = GmailApp.search(`in:sent "${trackingStr}"`);
      if (!threads || threads.length === 0) {
        // Fallback: search by recipient
        let cleanSubj = subject.replace(/["\\]/g, "");
        threads = GmailApp.search(`in:sent to:${recipient}`);
      }

      if (threads && threads.length > 0) {
        for (let t = 0; t < threads.length; t++) {
          let messages = threads[t].getMessages();
          for (let m = 0; m < messages.length; m++) {
            let msg = messages[m];
            let body = msg.getBody();
            let msgSubj = norm(msg.getSubject());
            let targetSubj = norm(subject);
            let toMatch = msg.getTo().toLowerCase().includes(recipient.toLowerCase());

            if (body.includes(trackingStr) || body.includes(cleanId) || (toMatch && (msgSubj.includes(targetSubj) || targetSubj.includes(msgSubj) || msgSubj.includes("pocket edit") || msgSubj.includes("pocket fm")))) {
              foundMessage = msg;
              break;
            }
          }
          if (foundMessage) break;
        }
      }

      if (foundMessage) {
        const actualSentDate = foundMessage.getDate();
        queueSheet.getRange(i + 1, 9).setValue("Sent");
        queueSheet.getRange(i + 1, 7).setValue(actualSentDate);

        let targetSheet = psSheet;
        if (targetSheetName.toString().toLowerCase().includes("master") || targetSheetName.toString().toLowerCase().includes("lifecycle")) {
          targetSheet = mainSheet || psSheet;
        }

        if (targetSheet && trackerRow > 0) {
          if (loggedStatusCol && loggedStatusCol > 0) {
            targetSheet.getRange(trackerRow, loggedStatusCol).setValue("Sent");
          }
          const tName = norm(templateName);
          const sType = norm(stageType);

          if (tName.includes("mg payment processed") || tName.includes("mg payout confirmation") || sType === "mgconfirmed") {
            if (sMgConfCol !== -1) targetSheet.getRange(trackerRow, sMgConfCol + 1).setValue("Sent");
            if (sFeedbackDateCol !== -1) targetSheet.getRange(trackerRow, sFeedbackDateCol + 1).setValue(actualSentDate);
          } else if (tName.includes("launch") || sType === "launch" || sType === "launch_no_ai") {
            if (sLaunchSentCol !== -1) targetSheet.getRange(trackerRow, sLaunchSentCol + 1).setValue("Sent");
            if (sLaunchCol !== -1) targetSheet.getRange(trackerRow, sLaunchCol + 1).setValue("Sent");
            if (sLaunchSentDateCol !== -1) targetSheet.getRange(trackerRow, sLaunchSentDateCol + 1).setValue(actualSentDate);
          } else if (tName.includes("check in 1") || sType === "checkin1") {
            if (sCheckIn1Col !== -1) targetSheet.getRange(trackerRow, sCheckIn1Col + 1).setValue("Sent");
            if (sCheckIn1DateCol !== -1) targetSheet.getRange(trackerRow, sCheckIn1DateCol + 1).setValue(actualSentDate);
          } else if (tName.includes("check in 2") || sType === "checkin2") {
            if (sCheckIn2Col !== -1) targetSheet.getRange(trackerRow, sCheckIn2Col + 1).setValue("Sent");
            if (sCheckIn2DateCol !== -1) targetSheet.getRange(trackerRow, sCheckIn2DateCol + 1).setValue(actualSentDate);
          } else if (tName.includes("author edit") || tName.includes("newsletter") || sType === "newsletter" || sType === "authoredit") {
            if (sNewsletterCol !== -1) targetSheet.getRange(trackerRow, sNewsletterCol + 1).setValue("Sent");
            if (sNewsletterDateCol !== -1) targetSheet.getRange(trackerRow, sNewsletterDateCol + 1).setValue(actualSentDate);
          }
        }
        syncedCount++;
        Logger.log(`[QUEUE SYNC SUCCESS] [ROW ${trackerRow}] Marked ${templateName} as "Sent" (Dispatched at: ${actualSentDate})`);
      }
    }
  }

  // ==================================================================
  // CHANNEL B: DIRECT TRACKER SCANNER (SCANS POST-SALES TRACKER DIRECTLY)
  // Ensures any cell marked 'Draft Ready' is flipped to 'Sent' if the email was dispatched!
  // ==================================================================
  if (psSheet && typeof psSheet.getLastRow === 'function') {
    const psLastRow = psSheet.getLastRow();
    const startRow = (psRes.rowIdx > 0 ? psRes.rowIdx + 1 : 4);
    if (psLastRow >= startRow) {
      const rowRange = psSheet.getRange(startRow, 1, psLastRow - startRow + 1, Math.max(psSheet.getLastColumn(), 45));
      const allRows = rowRange.getValues();

      for (let r = 0; r < allRows.length; r++) {
        const rowVals = allRows[r];
        const actualRow = startRow + r;
        const rowTitle = (sTitleCol > -1 && rowVals[sTitleCol]) ? rowVals[sTitleCol].toString().trim() : "";
        if (!rowTitle) continue;

        // Check if row has any stage marked as 'Draft Ready'
        const checkStatusCol = (statusColIdx, dateColIdx, stageKeyword) => {
          if (statusColIdx === -1 || statusColIdx >= rowVals.length) return;
          let val = (rowVals[statusColIdx] || "").toString().toLowerCase().trim();
          if (val === "draft ready" || val === "ready") {
            let recipientEmail = "";
            if (sEmailCol > -1 && rowVals[sEmailCol]) recipientEmail = cleanEmail(rowVals[sEmailCol]);
            if (!recipientEmail && mainSheet) {
              try {
                let mData = mainSheet.getRange(2, 1, Math.min(mainSheet.getLastRow(), 200), 30).getValues();
                for (let mr = 0; mr < mData.length; mr++) {
                  if (mData[mr][2] && norm(mData[mr][2]) === norm(rowTitle)) {
                    recipientEmail = cleanEmail(mData[mr][27]);
                    break;
                  }
                }
              } catch(e) {}
            }

            let query = "";
            if (recipientEmail) {
              query = `in:sent to:${recipientEmail}`;
            } else if (rowTitle) {
              query = `in:sent "${rowTitle.replace(/["\\]/g, "")}"`;
            }

            if (query) {
              let threads = GmailApp.search(query);
              if (threads && threads.length > 0) {
                for (let t = 0; t < threads.length; t++) {
                  let msgs = threads[t].getMessages();
                  for (let m = 0; m < msgs.length; m++) {
                    let msg = msgs[m];
                    let msgSubj = norm(msg.getSubject());
                    let titleNorm = norm(rowTitle);
                    let kwNorm = norm(stageKeyword);

                    if (msgSubj.includes(titleNorm) || (kwNorm && msgSubj.includes(kwNorm)) || (recipientEmail && msg.getTo().toLowerCase().includes(recipientEmail.toLowerCase()))) {
                      let sentDate = msg.getDate();
                      psSheet.getRange(actualRow, statusColIdx + 1).setValue("Sent");
                      if (dateColIdx !== -1) {
                        psSheet.getRange(actualRow, dateColIdx + 1).setValue(sentDate);
                      }
                      syncedCount++;
                      Logger.log(`[DIRECT SHEET SYNC SUCCESS] Row ${actualRow} ("${rowTitle}"): Marked Col ${statusColIdx + 1} as 'Sent' and Date as ${sentDate}`);
                      return;
                    }
                  }
                }
              }
            }
          }
        };

        // 1. Launch Status (Col AB & AA, Date Col AC)
        checkStatusCol(sLaunchSentCol, sLaunchSentDateCol, "launch");
        if (sLaunchCol !== -1 && sLaunchCol !== sLaunchSentCol) {
          let lVal = (rowVals[sLaunchCol] || "").toString().toLowerCase().trim();
          if (lVal === "draft ready" || lVal === "ready") {
            let lSentVal = psSheet.getRange(actualRow, sLaunchSentCol + 1).getValue().toString().toLowerCase().trim();
            if (lSentVal === "sent") psSheet.getRange(actualRow, sLaunchCol + 1).setValue("Sent");
          }
        }

        // 2. Check-In 1 (Col W, Date Col X)
        checkStatusCol(sCheckIn1Col, sCheckIn1DateCol, "check in 1");

        // 3. Check-In 2 (Col Y, Date Col Z)
        checkStatusCol(sCheckIn2Col, sCheckIn2DateCol, "check in 2");

        // 4. Newsletter (Col AD, Date Col AE)
        checkStatusCol(sNewsletterCol, sNewsletterDateCol, "pocket edit");

        // 5. MG Payout Confirmation (Col U/W, Date Col V)
        checkStatusCol(sMgConfCol, sFeedbackDateCol, "minimum guarantee");
      }
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
 * Installs a background trigger to run syncSentEmails() every 1 minute automatically.
 * Ensures the moment an outreach draft is sent from Gmail, the sheet flips to 'Sent'!
 */
function installSentMailSyncTrigger() {
  const triggers = ScriptApp.getProjectTriggers();
  for (let t of triggers) {
    if (t.getHandlerFunction() === 'syncSentEmails') {
      ScriptApp.deleteTrigger(t);
    }
  }
  ScriptApp.newTrigger('syncSentEmails')
    .timeBased()
    .everyMinutes(1)
    .create();
  
  const msg = "⚡ Automated Sent Mail Sync Trigger is active! Runs every 1 minute in the background.";
  Logger.log("[SUCCESS] " + msg);
  try {
    SpreadsheetApp.getActiveSpreadsheet().toast(msg, "Sync Activated", 6);
  } catch (e) {}
  return msg;
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
