/**
 * =============================================================
 * POCKET FM LIFECYCLE CRM AUTOMATION - MODULE 5: MAIN & TRIGGERS
 * File: Main.gs (or Main.js)
 * =============================================================
 * 10 INDIVIDUAL ISOLATED STAGE TRIGGERS:
 * 1. Welcome Emails Only
 * 2. Vendor Onboarding Only
 * 3. MG Payout Initiated Only
 * 4. MG Payout Confirmation Only
 * 5. Author Check-In 1 (15 Days) Only
 * 6. Author Check-In 2 (30 Days) Only
 * 7. Show Launch Announcements Only
 * 8. Newsletter (The Author Edit) Only
 * 9. Quarterly Revenue Statements (Worked Well) Only
 * 10. Content Didn't Work Well Statements Only
 * Bonus: Test Newsletter Draft & Sync Sent Emails Only
 *
 * ZERO COMMOTION: Each button evaluates and runs ONLY its specific condition!
 * No master "all running together" button.
 */

// Global in-memory log buffer for the current session
var GLOBAL_SESSION_LOGS = [];

/**
 * GOOGLE SHEETS TOP-BAR MENU BUILDER:
 * Creates the "Pocket FM Automation" menu with 10 INDIVIDUAL STAGE TRIGGERS.
 */
function onOpen() {
  try {
    SpreadsheetApp.getUi()
      .createMenu("Pocket FM Automation")
      .addItem("▶️ Run All Automations at Once", "triggerRunAllStagesSequentially")
      .addSeparator()
      .addItem("1️⃣ Run Welcome Emails Only", "triggerWelcomeEmailsOnly")
      .addItem("2️⃣ Run Vendor Onboarding Only", "triggerVendorOnboardingOnly")
      .addItem("3️⃣ Run MG Payout Initiated Only", "triggerMgInitiatedOnly")
      .addItem("4️⃣ Run MG Payout Confirmation Only", "triggerMgConfirmedOnly")
      .addItem("5️⃣ Run Author Check-In 1 (15 Days) Only", "triggerCheckIn1Only")
      .addItem("6️⃣ Run Author Check-In 2 (30 Days) Only", "triggerCheckIn2Only")
      .addItem("7️⃣ Run Show Launch Announcements Only", "triggerLaunchAnnouncementsOnly")
      .addItem("8️⃣ Run Newsletter (The Author Edit) Only", "triggerNewsletterOnly")
      .addItem("9️⃣ Run Quarterly Revenue Statements (Worked Well) Only", "triggerRevenueStatementsOnly")
      .addItem("🔟 Run Content Didn't Work Well Statements Only", "triggerRevStatementContentBadOnly")
      .addSeparator()
      .addItem("🧪 Test Newsletter Draft (Generate Directly to My Gmail)", "triggerTestNewsletterDraft")
      .addItem("⚡ Enable Auto-Sync Sent Emails (Every 1 Min)", "installSentMailSyncTrigger")
      .addItem("⏰ Enable Daily Outreach Automation (Every Morning 9 AM)", "installDailyOutreachTrigger")
      .addItem("🔄 Sync Sent Emails Now", "triggerSyncSentEmailsOnly")
      .addToUi();

    // Pocket FM CMS Scraper Menu
    SpreadsheetApp.getUi()
      .createMenu("Pocket FM CMS Scraper")
      .addItem("🚀 Launch CMS Scraper", "openCmsScraperWindow")
      .addToUi();
  } catch (e) {
    Logger.log("Menu creation skipped (not in spreadsheet UI context): " + e.message);
  }
}

/**
 * REUSABLE ISOLATED SINGLE-STAGE RUNNER:
 * Runs STRICTLY and ONLY the condition specified by targetStage.
 */
function runSingleStage(stageKey, stageLabel) {
  Logger.log("==================================================================");
  Logger.log("[START] Running " + stageLabel + " Only (Condition: " + stageKey + ")...");
  Logger.log("==================================================================");

  try {
    if (stageKey === 'syncSent') {
      if (typeof syncSentEmails === 'function') {
        syncSentEmails();
      } else {
        Logger.log("[WARNING] syncSentEmails function is not loaded. Ensure DraftEngine.gs is saved.");
      }
    } else {
      if (typeof processOutreachQueue === 'function') {
        processOutreachQueue(false, stageKey);
      } else {
        Logger.log("[ERROR] processOutreachQueue function is not loaded. Ensure StageHandlers.gs is saved.");
      }
    }

    try {
      SpreadsheetApp.flush();
    } catch (e) {}

    const successMsg = stageLabel + " evaluated successfully! Check Gmail Drafts.";
    Logger.log("[SUCCESS] " + successMsg);
    Logger.log("==================================================================");

    try {
      const activeSs = SpreadsheetApp.getActiveSpreadsheet();
      if (activeSs) activeSs.toast(successMsg, "Pocket FM Automation", 5);
    } catch (e) {}

    return { success: true, message: successMsg };
  } catch (err) {
    const errorMsg = "[ERROR] [" + stageLabel + "] " + err.message;
    Logger.log(errorMsg);
    try {
      const activeSs = SpreadsheetApp.getActiveSpreadsheet();
      if (activeSs) activeSs.toast(errorMsg, "Error", 6);
    } catch (e) {}
    return { success: false, error: err.message };
  }
}

// =============================================================
// MASTER RUNNER: RUN ALL STAGES SEQUENTIALLY (AT ONCE)
// =============================================================

/**
 * MASTER RUNNER: RUN ALL AUTOMATIONS AT ONCE (SEQUENTIAL EXECUTION)
 * Executes every single lifecycle stage in order.
 * Strictly waits for each stage to finish completely and commits all
 * spreadsheet updates before initiating the next stage.
 */
function triggerRunAllStagesSequentially() {
  Logger.log("==================================================================");
  Logger.log("[MASTER] Starting Sequential Execution of All Automations...");
  Logger.log("==================================================================");

  const stages = [
    { key: 'welcome', label: '1. Welcome Emails', fn: triggerWelcomeEmailsOnly },
    { key: 'vendor', label: '2. Vendor Onboarding', fn: triggerVendorOnboardingOnly },
    { key: 'mgInitiated', label: '3. MG Payout Initiated', fn: triggerMgInitiatedOnly },
    { key: 'mgConfirmed', label: '4. MG Payout Confirmation', fn: triggerMgConfirmedOnly },
    { key: 'checkIn1', label: '5. Author Check-In 1 (15 Days)', fn: triggerCheckIn1Only },
    { key: 'checkIn2', label: '6. Author Check-In 2 (30 Days)', fn: triggerCheckIn2Only },
    { key: 'launch', label: '7. Show Launch Announcements', fn: triggerLaunchAnnouncementsOnly },
    { key: 'newsletter', label: '8. Newsletter (The Author Edit)', fn: triggerNewsletterOnly },
    { key: 'revStatement_workedWell', label: '9. Quarterly Revenue Statements (Worked Well)', fn: triggerRevenueStatementsOnly },
    { key: 'revStatement_didntWorkWell', label: '10. Content Didn\'t Work Well Statements', fn: triggerRevStatementContentBadOnly }
  ];

  let results = [];
  let ss = null;
  try { ss = SpreadsheetApp.getActiveSpreadsheet(); } catch (e) {}

  for (let i = 0; i < stages.length; i++) {
    const stage = stages[i];
    const stepNum = i + 1;
    const totalSteps = stages.length;

    Logger.log(`\n>>> [STEP ${stepNum}/${totalSteps}] Starting ${stage.label}...`);
    if (ss) {
      try {
        ss.toast(`Running ${stage.label} (${stepNum}/${totalSteps})...`, "Pocket FM Automation", 4);
      } catch (e) {}
    }

    try {
      const res = stage.fn();
      results.push({ stage: stage.label, success: true, res: res });
      Logger.log(`>>> [STEP ${stepNum}/${totalSteps}] Completed ${stage.label} successfully.`);
    } catch (err) {
      results.push({ stage: stage.label, success: false, error: err.message });
      Logger.log(`>>> [STEP ${stepNum}/${totalSteps}] Error in ${stage.label}: ${err.message}`);
    }

    try {
      SpreadsheetApp.flush();
    } catch (eFlush) {}
  }

  // Draft generation complete.
  // Note: We do NOT auto-sync sent emails here because drafts were just created and have not been dispatched by the user yet.
  // When drafts are dispatched from Gmail, syncSentEmails will update dropdowns from 'Draft Ready' to 'Sent'.
  Logger.log("\n>>> [RUN COMPLETE] All eligible drafts have been generated and marked 'Draft Ready' in the spreadsheet.");

  const completionMsg = "🎉 All 9 stages executed! Drafts generated and marked 'Draft Ready'. Review in Gmail Drafts.";
  Logger.log("==================================================================");
  Logger.log("[MASTER COMPLETE] " + completionMsg);
  Logger.log("==================================================================");

  if (ss) {
    try {
      ss.toast(completionMsg, "All Automations Complete", 6);
    } catch (e) {}
  }

  return { success: true, stagesRun: stages.length, results: results };
}

// Backward compatibility alias for master run
function runAllOutreachAutomations() {
  return triggerRunAllStagesSequentially();
}

// =============================================================
// THE 9 ISOLATED STAGE TRIGGER FUNCTIONS
// =============================================================

/**
 * 1. TRIGGER: WELCOME EMAILS ONLY
 * Condition: Evaluates only Timestamp Column A in Master, drafts Welcome Email.
 */
function triggerWelcomeEmailsOnly() {
  return runSingleStage('welcome', '1. Welcome Emails');
}

/**
 * 2. TRIGGER: VENDOR ONBOARDING ONLY
 * Condition: Evaluates only Vendor Onboarding status, drafts Vendor Email.
 */
function triggerVendorOnboardingOnly() {
  return runSingleStage('vendor', '2. Vendor Onboarding');
}

/**
 * 3. TRIGGER: MG PAYOUT INITIATED ONLY
 * Condition: Evaluates Vendor Lifecycle Exit Date (Col U in Master).
 */
function triggerMgInitiatedOnly() {
  return runSingleStage('mgInitiated', '3. MG Payout Initiated');
}

/**
 * 4. TRIGGER: MG PAYOUT CONFIRMATION ONLY
 * Condition: Evaluates MG Payout Exit Date (Col X in Master), stamps Feedback Mail Date.
 */
function triggerMgConfirmedOnly() {
  return runSingleStage('mgConfirmed', '4. MG Payout Confirmation');
}

/**
 * 5. TRIGGER: AUTHOR CHECK-IN 1 (15 DAYS) ONLY
 * Condition: Evaluates 15 Days from Feedback Mail Date (Col R in Post-Sales).
 */
function triggerCheckIn1Only() {
  return runSingleStage('checkIn1', '5. Author Check-In 1 (15 Days)');
}

/**
 * 6. TRIGGER: AUTHOR CHECK-IN 2 (30 DAYS) ONLY
 * Condition: Evaluates 30 Days from Feedback Mail Date (Col R in Post-Sales).
 */
function triggerCheckIn2Only() {
  return runSingleStage('checkIn2', '6. Author Check-In 2 (30 Days)');
}

/**
 * 7. TRIGGER: SHOW LAUNCH ANNOUNCEMENTS ONLY
 * Condition: Evaluates Launch Date vs Script Date anomaly check (Col J vs Col O).
 */
function triggerLaunchAnnouncementsOnly() {
  return runSingleStage('launch', '7. Show Launch Announcements');
}

/**
 * 8. TRIGGER: NEWSLETTER (THE AUTHOR EDIT) ONLY
 * Condition: Evaluates 15 Days after Show Launch (Col X Sent).
 */
function triggerNewsletterOnly() {
  return runSingleStage('newsletter', '8. Newsletter (The Author Edit)');
}

/**
 * TEST TRIGGER: IMMEDIATE NEWSLETTER DRAFT GENERATOR
 * Generates a fresh, styled newsletter draft directly into the active user's Gmail drafts.
 */
function triggerTestNewsletterDraft() {
  try {
    if (typeof testNewsletterDraft === 'function') {
      const subject = testNewsletterDraft();
      let myEmail = "";
      try { myEmail = Session.getActiveUser().getEmail(); } catch (e) {}
      const msg = "✅ Fresh Newsletter Draft generated in your Gmail drafts folder! (" + (myEmail || "your email") + ")";
      Logger.log("[SUCCESS] " + msg);
      try {
        SpreadsheetApp.getActiveSpreadsheet().toast(msg, "The Pocket Edit", 8);
      } catch(e) {}
      return { success: true, message: msg };
    } else {
      Logger.log("[ERROR] testNewsletterDraft function not found. Ensure DraftEngine.gs is saved.");
      return { success: false, error: "testNewsletterDraft not found" };
    }
  } catch (err) {
    Logger.log("[ERROR] Failed to generate test newsletter: " + err.message);
    return { success: false, error: err.message };
  }
}

/**
 * 9. TRIGGER: QUARTERLY REVENUE STATEMENTS (WORKED WELL) ONLY
 * Condition: Evaluates AMJ, JAS, OND quarterly statement due dates & links for Testing_PGC / Launched shows.
 */
function triggerRevenueStatementsOnly() {
  return runSingleStage('revStatement_workedWell', '9. Quarterly Revenue Statements (Worked Well)');
}

/**
 * 10. TRIGGER: CONTENT DIDN'T WORK WELL REVENUE STATEMENTS ONLY
 * Condition: Evaluates shows where Launch Status is Bad / Dropped / Sunset (Stage 9C), drafts 'Didnt work well - Content Related Update'.
 */
function triggerRevStatementContentBadOnly() {
  return runSingleStage('revStatement_didntWorkWell', '10. Content Didn\'t Work Well Statements');
}

// Backward compatibility aliases for Content Didn't Work Well trigger
function triggerContentBadOnly() {
  return triggerRevStatementContentBadOnly();
}
function triggerContentDidntWorkWellOnly() {
  return triggerRevStatementContentBadOnly();
}

/**
 * (BONUS HELPER) TRIGGER: SYNC SENT EMAILS ONLY
 * Synchronizes Gmail Sent Mail status back to the sheet dropdowns.
 */
function triggerSyncSentEmailsOnly() {
  return runSingleStage('syncSent', 'Sync Sent Emails');
}

// Backward compatibility alias functions
function showExecutionLogsSidebar() {}
function openExecutionLogsSidebar() {}
function openLiveAutomationConsole() {}


/**
 * INSTALLER: AUTO-SYNC SENT EMAILS TRIGGER (EVERY 1 MINUTE)
 * Installs a time-driven clock trigger in Apps Script to automatically scan Gmail Sent Mail
 * and update "Draft Ready" to "Sent" in the spreadsheet.
 */

/**
 * AUTOMATED DAILY OUTREACH TRIGGER INSTALLER:
 * Installs a background trigger to run triggerRunAllStagesSequentially() every day at 9:00 AM automatically.
 * Automatically checks all 10 stages (e.g. Col AC + 15 days for Newsletter) and generates drafts into Gmail Drafts!
 */
function installDailyOutreachTrigger() {
  const triggers = ScriptApp.getProjectTriggers();
  for (let t of triggers) {
    if (t.getHandlerFunction() === 'triggerRunAllStagesSequentially' || t.getHandlerFunction() === 'runAllOutreachAutomations') {
      ScriptApp.deleteTrigger(t);
    }
  }
  ScriptApp.newTrigger('triggerRunAllStagesSequentially')
    .timeBased()
    .atHour(9)
    .everyDays(1)
    .create();

  const msg = "⏰ Daily Automated Outreach Trigger is active! Runs every morning at 9:00 AM.";
  Logger.log("[SUCCESS] " + msg);
  try {
    SpreadsheetApp.getActiveSpreadsheet().toast(msg, "Daily Schedule Active", 6);
  } catch (e) {}
  return msg;
}
function installSentMailSyncTrigger() {
  if (typeof setupAutoSyncSentTrigger === 'function') {
    return setupAutoSyncSentTrigger();
  }
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
  const msg = "⚡ Automated Sent Mail Sync Trigger activated! Runs every 1 minute.";
  Logger.log("[SUCCESS] " + msg);
  try {
    SpreadsheetApp.getActiveSpreadsheet().toast(msg, "Auto-Sync Enabled", 6);
  } catch(e) {}
  return msg;
}

/**
 * TEST TRIGGER: CONTENT DIDN'T WORK WELL DRAFT
 * Generates a test draft directly to the user's Gmail using the updated template.
 */
function triggerTestContentBadDraft() {
  if (typeof testContentBadDraft === 'function') {
    return testContentBadDraft();
  } else {
    Logger.log("testContentBadDraft function is not found in DraftEngine.gs.");
  }
}


/**
 * Pocket FM CMS Scraper Menu & 1-Click Launcher
 * Opens the deployed CMS Scraper Web App directly from the Google Sheet
 */
function openCmsScraperWindow() {
  const webAppUrl = "https://script.google.com/a/macros/pocketfm.com/s/AKfycbzZqhEd3T03yt6u_G-M51QcjYzndd9tkfJNPS8r9eXr8vFA6owv5qt_UzymosThbdkb/exec";
  const cmsUrl = "https://cms.pocketfm.com/shows/audiobooks?tab=published";
  
  const html = `<!DOCTYPE html>
<html>
<head>
  <base target="_blank">
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      padding: 24px;
      margin: 0;
      background: #fdfdfd;
      text-align: center;
      color: #202124;
    }
    h2 {
      color: #7a0000;
      font-size: 18px;
      margin-bottom: 8px;
      font-weight: 700;
    }
    p {
      color: #5f6368;
      font-size: 13px;
      margin-bottom: 20px;
      line-height: 1.4;
    }
    .btn-container {
      display: flex;
      flex-direction: column;
      gap: 12px;
      align-items: center;
    }
    .btn-primary {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      background: #7a0000;
      color: #ffffff !important;
      text-decoration: none;
      font-size: 14px;
      font-weight: 600;
      padding: 12px 24px;
      border-radius: 6px;
      width: 85%;
      box-shadow: 0 1px 3px rgba(0,0,0,0.12);
      transition: background 0.2s, transform 0.1s;
    }
    .btn-primary:hover {
      background: #5c0000;
      transform: translateY(-1px);
    }
    .btn-secondary {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      background: #f1f3f4;
      color: #3c4043 !important;
      text-decoration: none;
      font-size: 13px;
      font-weight: 600;
      padding: 10px 20px;
      border-radius: 6px;
      border: 1px solid #dadce0;
      width: 85%;
      transition: background 0.2s;
    }
    .btn-secondary:hover {
      background: #e8eaed;
    }
    .footer-note {
      margin-top: 18px;
      font-size: 11px;
      color: #80868b;
    }
  </style>
</head>
<body>
  <h2>📻 Pocket FM CMS Scraper Launcher</h2>
  <p>Click below to open your deployed CMS live scraper dashboard in a new window:</p>
  
  <div class="btn-container">
    <a href="${webAppUrl}" target="_blank" class="btn-primary" onclick="setTimeout(function(){google.script.host.close();}, 800)">
      🚀 Launch Live CMS Scraper Dashboard
    </a>
    <a href="${cmsUrl}" target="_blank" class="btn-secondary">
      🌐 Open Pocket FM CMS Directly
    </a>
  </div>
  
  <div class="footer-note">
    Target Sheet: <b>Copy of US_Licensing_Lifecycle_Tracker</b>
  </div>
</body>
</html>`;
  
  const htmlOutput = HtmlService.createHtmlOutput(html)
    .setWidth(460)
    .setHeight(280);
    
  SpreadsheetApp.getUi().showModalDialog(htmlOutput, "Pocket FM CMS Live Scraper");
}


/**
 * INSTANT ONEDIT TRIGGER FOR POST-SALES TRACKER
 * Automatically synchronizes manual dropdown selections made by the user in Google Sheets:
 * - If Column W (Author Check-In 1) is selected as "Sent" -> automatically stamps Column X with today's date!
 * - If Column Y (Author Check-In 2) is selected as "Sent" -> automatically stamps Column Z with today's date!
 * - If Column AB (Show Launch Announcement) is selected as "Sent" -> automatically stamps Column AC with today's date!
 */
function onEdit(e) {
  if (!e || !e.range) return;
  try {
    const sheet = e.range.getSheet();
    if (!sheet || typeof sheet.getName !== 'function') return;

    const sheetName = sheet.getName().toLowerCase().trim().replace(/–|—/g, "-");
    if (sheetName !== "post-sales tracker" && sheetName !== "post sales tracker") {
      return;
    }

    const row = e.range.getRow();
    if (row < 4) return; // Skip headers (Rows 1-3)

    const col = e.range.getColumn();
    const val = (e.value || sheet.getRange(row, col).getValue() || "").toString().trim().toLowerCase();

    // Col W (Col 23) -> Check-In 1
    if (col === 23 && (val === "sent" || val === "yes")) {
      let xCell = sheet.getRange(row, 24);
      if (!xCell.getValue() || xCell.getValue().toString().trim() === "") {
        let now = new Date();
        xCell.setValue(now);
        SpreadsheetApp.flush();
        Logger.log(`[onEdit] Row ${row}: Col W set to 'Sent'. Stamped Col X with date: ${now}`);
      }
    }

    // Col Y (Col 25) -> Check-In 2
    if (col === 25 && (val === "sent" || val === "yes")) {
      let zCell = sheet.getRange(row, 26);
      if (!zCell.getValue() || zCell.getValue().toString().trim() === "") {
        let now = new Date();
        zCell.setValue(now);
        SpreadsheetApp.flush();
        Logger.log(`[onEdit] Row ${row}: Col Y set to 'Sent'. Stamped Col Z with date: ${now}`);
      }
    }

    // Col AB (Col 28) -> Show Launch Announcement
    if (col === 28 && (val === "sent" || val === "yes")) {
      let acCell = sheet.getRange(row, 29);
      if (!acCell.getValue() || acCell.getValue().toString().trim() === "") {
        let now = new Date();
        acCell.setValue(now);
        SpreadsheetApp.flush();
        Logger.log(`[onEdit] Row ${row}: Col AB set to 'Sent'. Stamped Col AC with date: ${now}`);
      }
    }
  } catch (err) {
    Logger.log("[onEdit Error] " + err.message);
  }
}
