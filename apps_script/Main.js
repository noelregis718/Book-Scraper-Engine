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
 * Bonus: Sync Sent Emails & Triggers
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
      .addItem("⚡ Enable Auto-Sync Sent Emails (Every 1 Min)", "installSentMailSyncTrigger")
      .addItem("⏰ Enable Daily Outreach Automation (Every Morning 9 AM)", "installDailyOutreachTrigger")
      .addItem("🔄 Sync Sent Emails Now", "triggerSyncSentEmailsOnly")
      .addSeparator()
      .addItem("📊 Generate Revenue Statements", "triggerGenerateRevenueStatements")
      .addToUi();

    // Pocket FM CMS Scraper Menu
    if (typeof installCmsMenu === "function") {
      installCmsMenu();
    } else if (typeof openCmsScraperDialog === "function") {
      SpreadsheetApp.getUi()
        .createMenu("Pocket FM CMS Scraper")
        .addItem("🚀 Launch CMS Scraper Popup", "openCmsScraperDialog")
        .addToUi();
    } else {
      SpreadsheetApp.getUi()
        .createMenu("Pocket FM CMS Scraper")
        .addItem("🚀 Launch CMS Scraper", "openCmsScraperWindow")
        .addToUi();
    }
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

// =============================================================
// REVENUE STATEMENT GENERATOR MODULE (STAGE 9 PRE-REQUISITE)
// =============================================================
// Automatically generates branded, confidential revenue statements directly
// from Google Sheets data, creates the document on Google Drive, and saves
// the shareable link directly into Column AL (Revenue Statement Link).

const REVENUE_STATEMENT_CONFIG = {
  DRIVE_FOLDER_NAME: "Pocket FM Revenue Statements",
  DEFAULT_REV_SHARE_PCT: 15
};

/**
 * Resolves or creates the Google Drive storage folder for statements
 */
function getOrCreateStatementsFolder() {
  const folderName = REVENUE_STATEMENT_CONFIG.DRIVE_FOLDER_NAME;
  const folders = DriveApp.getFoldersByName(folderName);
  if (folders.hasNext()) {
    return folders.next();
  }
  const folder = DriveApp.createFolder(folderName);
  folder.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
  return folder;
}

/**
 * Resolves column indexes from header row
 */
function resolveStatementColumns(headers) {
  const hLower = headers.map(h => (h || "").toString().toLowerCase().trim());
  
  let titleCol = hLower.findIndex(h => h.includes("title") || h.includes("series") || h.includes("show") || h === "ip");
  if (titleCol === -1) titleCol = 2; // Default Col C

  let authorCol = hLower.findIndex(h => h.includes("author") && !h.includes("email"));
  if (authorCol === -1) authorCol = 1; // Default Col B

  let emailCol = hLower.findIndex(h => h.includes("author email") || h.includes("email"));

  let revLinkCol = hLower.findIndex(h => 
    (h.includes("jas") || h.includes("rev") || h.includes("statement")) && 
    (h.includes("link") || h.includes("drive") || h.includes("url"))
  );
  if (revLinkCol === -1) revLinkCol = 37; // Col AL (0-indexed 37)

  let grossRevCol = hLower.findIndex(h => h.includes("gross") || h.includes("revenue generated"));
  let mgPaidCol = hLower.findIndex(h => h.includes("mg paid") || h.includes("advance paid") || (h.includes("mg") && h.includes("paid")));
  let playsCol = hLower.findIndex(h => h.includes("plays") || h.includes("listens"));
  let listenersCol = hLower.findIndex(h => h.includes("listeners") || h.includes("users"));
  let periodCol = hLower.findIndex(h => h.includes("reporting period") || h.includes("period") || h.includes("quarter"));

  return {
    titleCol,
    authorCol,
    emailCol,
    revLinkCol,
    grossRevCol,
    mgPaidCol,
    playsCol,
    listenersCol,
    periodCol
  };
}

/**
 * Extracts and calculates statement data from a tracker row
 */
function extractRowStatementData(row, cols, rowNum) {
  const title = (cols.titleCol > -1 && row[cols.titleCol]) ? row[cols.titleCol].toString().trim() : `Show Row ${rowNum}`;
  const author = (cols.authorCol > -1 && row[cols.authorCol]) ? row[cols.authorCol].toString().trim() : "Valued Author";
  const firstName = author.split(" ")[0].trim() || "Author";

  let period = (cols.periodCol > -1 && row[cols.periodCol]) ? row[cols.periodCol].toString().trim() : "";
  if (!period) {
    period = "July 1, 2026 – September 30, 2026 (3-Month Statement / Q3)";
  }

  const isSixMonth = period.toLowerCase().includes("6-month") || period.toLowerCase().includes("combined");
  const introLabel = isSixMonth 
    ? "Here's your 6-month combined revenue statement for" 
    : "Here's your 3-month quarterly revenue statement for";

  const parseNum = (val, fallback = 0) => {
    if (val === null || val === undefined || val === "") return fallback;
    if (typeof val === "number") return val;
    let clean = val.toString().replace(/[$,]/g, "").trim();
    let num = parseFloat(clean);
    return isNaN(num) ? fallback : num;
  };

  const plays = (cols.playsCol > -1 && row[cols.playsCol]) ? row[cols.playsCol].toString().trim() : "1,257";
  const listeners = (cols.listenersCol > -1 && row[cols.listenersCol]) ? row[cols.listenersCol].toString().trim() : "299";

  const grossRev = (cols.grossRevCol > -1) ? parseNum(row[cols.grossRevCol], 0.0) : 0.0;
  const revSharePct = REVENUE_STATEMENT_CONFIG.DEFAULT_REV_SHARE_PCT;
  const revShareAmount = +(grossRev * (revSharePct / 100)).toFixed(2);

  const mgPaid = (cols.mgPaidCol > -1) ? parseNum(row[cols.mgPaidCol], 7500.0) : 7500.0;
  const mgRecouped = +(Math.max(0, mgPaid - revShareAmount)).toFixed(2);
  const finalPayout = +(Math.max(0, revShareAmount - mgPaid)).toFixed(2);

  const fmtCurrency = (n) => n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  return {
    rowNum,
    title,
    author,
    firstName,
    period,
    introLabel,
    totalPlays: plays,
    totalListeners: listeners,
    revenueGross: fmtCurrency(grossRev),
    revSharePercent: revSharePct.toString(),
    revShareAmount: fmtCurrency(revShareAmount),
    mgPaid: fmtCurrency(mgPaid),
    mgRecouped: fmtCurrency(mgRecouped),
    finalPayout: fmtCurrency(finalPayout)
  };
}

/**
 * Builds the HTML content for a revenue statement
 */
function buildStatementHtml(data) {
  let template = getStatementTemplateString();
  return template
    .replace(/\{\{FIRST_NAME\}\}/g, data.firstName)
    .replace(/\{\{INTRO_LABEL\}\}/g, data.introLabel)
    .replace(/\{\{SERIES_NAME\}\}/g, data.title)
    .replace(/\{\{AUTHOR_NAME\}\}/g, data.author)
    .replace(/\{\{REPORTING_PERIOD\}\}/g, data.period)
    .replace(/\{\{TOTAL_PLAYS\}\}/g, data.totalPlays)
    .replace(/\{\{TOTAL_LISTENERS\}\}/g, data.totalListeners)
    .replace(/\{\{REVENUE_GROSS\}\}/g, data.revenueGross)
    .replace(/\{\{REV_SHARE_PERCENT\}\}/g, data.revSharePercent)
    .replace(/\{\{REV_SHARE_AMOUNT\}\}/g, data.revShareAmount)
    .replace(/\{\{MG_PAID\}\}/g, data.mgPaid)
    .replace(/\{\{MG_RECOUPED\}\}/g, data.mgRecouped)
    .replace(/\{\{FINAL_PAYOUT\}\}/g, data.finalPayout);
}

/**
 * Generates statement file on Google Drive and writes link into Google Sheet (Col AL)
 */
function generateAndSaveStatement(sheet, rowVals, cols, rowNum) {
  const data = extractRowStatementData(rowVals, cols, rowNum);
  const htmlContent = buildStatementHtml(data);
  const folder = getOrCreateStatementsFolder();

  const cleanTitle = data.title.replace(/[^a-zA-Z0-9_\- ]/g, "").trim().replace(/\s+/g, "_");
  const filename = `Revenue_Statement_${cleanTitle}.html`;

  const existingFiles = folder.getFilesByName(filename);
  let file;
  if (existingFiles.hasNext()) {
    file = existingFiles.next();
    file.setContent(htmlContent);
  } else {
    file = folder.createFile(filename, htmlContent, MimeType.HTML);
  }

  file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
  const driveUrl = file.getUrl();

  const targetCol = cols.revLinkCol + 1; // 1-based index (Col AL = 38)
  sheet.getRange(rowNum, targetCol).setValue(driveUrl);

  Logger.log(`[Statement Generator] Row ${rowNum}: "${data.title}" -> Link saved in Col ${targetCol}: ${driveUrl}`);
  return {
    title: data.title,
    author: data.author,
    url: driveUrl,
    rowNum
  };
}

/**
 * MAIN REVENUE STATEMENT GENERATOR TRIGGER:
 * Added as the single revenue statement option at the end of the menu.
 * - If an author row is selected: prompts to generate for that row or batch generate all missing rows.
 * - Saves the shareable link directly into Column AL.
 */
function triggerGenerateRevenueStatements() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const range = sheet.getActiveRange();
  const selectedRow = (range && range.getRow() > 1) ? range.getRow() : null;

  try {
    const ui = SpreadsheetApp.getUi();
    if (selectedRow) {
      const resp = ui.alert(
        "📊 Generate Revenue Statements",
        `Do you want to generate the statement for the SELECTED ROW (Row ${selectedRow})?\n\n` +
        `• Click "YES" to generate for Row ${selectedRow} only.\n` +
        `• Click "NO" to scan and batch-generate for ALL rows missing a link in Column AL.\n` +
        `• Click "CANCEL" to abort.`,
        ui.ButtonSet.YES_NO_CANCEL
      );

      if (resp === ui.Button.YES) {
        triggerGenerateStatementActiveRow();
      } else if (resp === ui.Button.NO) {
        triggerGenerateAllMissingStatements();
      }
    } else {
      triggerGenerateAllMissingStatements();
    }
  } catch (e) {
    Logger.log("[Statement Trigger] Headless run or UI unavailable: " + e.message);
    triggerGenerateAllMissingStatements();
  }
}

/**
 * Action 1: Generates statement for active row and saves to Col AL
 */
function triggerGenerateStatementActiveRow() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const range = sheet.getActiveRange();
  if (!range) {
    try { SpreadsheetApp.getUi().alert("Please select an author row first!"); } catch(e){}
    return;
  }
  
  const rowNum = range.getRow();
  if (rowNum === 1) {
    try { SpreadsheetApp.getUi().alert("Row 1 is the header row. Please select an author row."); } catch(e){}
    return;
  }

  const numCols = sheet.getLastColumn();
  const headers = sheet.getRange(1, 1, 1, numCols).getValues()[0];
  const rowVals = sheet.getRange(rowNum, 1, 1, numCols).getValues()[0];
  const cols = resolveStatementColumns(headers);

  if (!rowVals[cols.titleCol]) {
    try { SpreadsheetApp.getUi().alert(`Row ${rowNum} does not contain a show title!`); } catch(e){}
    return;
  }

  try {
    const res = generateAndSaveStatement(sheet, rowVals, cols, rowNum);
    const msg = `✅ Revenue Statement Generated!\n\nShow: ${res.title}\nAuthor: ${res.author}\nLink: ${res.url}\n\nThe link has been written directly to Column AL.`;
    Logger.log(msg);
    try { SpreadsheetApp.getUi().alert(msg); } catch(e){}
  } catch (err) {
    Logger.log("Error generating statement: " + err.message);
    try { SpreadsheetApp.getUi().alert("Error generating statement: " + err.message); } catch(e){}
  }
}

/**
 * Action 2: Generates statements in batch for all active rows missing a link in Col AL
 */
function triggerGenerateAllMissingStatements() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const lastRow = sheet.getLastRow();
  const numCols = sheet.getLastColumn();
  
  if (lastRow < 2) {
    try { SpreadsheetApp.getUi().alert("No data found in current sheet."); } catch(e){}
    return;
  }

  const allData = sheet.getRange(1, 1, lastRow, numCols).getValues();
  const headers = allData[0];
  const cols = resolveStatementColumns(headers);

  let generatedCount = 0;
  let skippedCount = 0;

  for (let i = 1; i < allData.length; i++) {
    const rowNum = i + 1;
    const rowVals = allData[i];
    
    const rawTitle = (cols.titleCol > -1 && rowVals[cols.titleCol]) ? rowVals[cols.titleCol].toString().trim() : "";
    if (!rawTitle || rawTitle === "-" || rawTitle.startsWith("#")) {
      continue;
    }

    const existingLink = (cols.revLinkCol > -1 && rowVals[cols.revLinkCol]) ? rowVals[cols.revLinkCol].toString().trim() : "";
    if (existingLink && (existingLink.startsWith("http://") || existingLink.startsWith("https://"))) {
      skippedCount++;
      continue;
    }

    try {
      generateAndSaveStatement(sheet, rowVals, cols, rowNum);
      generatedCount++;
    } catch (e) {
      Logger.log(`Error on Row ${rowNum} (${rawTitle}): ` + e.message);
    }
  }

  const summary = `⚡ Batch Statement Generation Complete!\n\n• Generated & Linked in Col AL: ${generatedCount}\n• Already Had Links (Skipped): ${skippedCount}`;
  Logger.log(summary);
  try { SpreadsheetApp.getUi().alert(summary); } catch(e){}
}

/**
 * Action 3: Shows an interactive preview of the statement for the selected row
 */
function triggerPreviewSelectedStatement() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const range = sheet.getActiveRange();
  if (!range) return;
  const rowNum = range.getRow();
  if (rowNum === 1) return;

  const numCols = sheet.getLastColumn();
  const headers = sheet.getRange(1, 1, 1, numCols).getValues()[0];
  const rowVals = sheet.getRange(rowNum, 1, 1, numCols).getValues()[0];
  const cols = resolveStatementColumns(headers);

  const data = extractRowStatementData(rowVals, cols, rowNum);
  const htmlContent = buildStatementHtml(data);

  try {
    const htmlOutput = HtmlService.createHtmlOutput(htmlContent)
      .setWidth(900)
      .setHeight(650);
    SpreadsheetApp.getUi().showModalDialog(htmlOutput, `Statement Preview: ${data.title}`);
  } catch(e) {
    Logger.log("Preview modal failed: " + e.message);
  }
}

/**
 * Inlined Template String for Standalone Resilience
 */
function getStatementTemplateString() {
  return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Revenue Statement | Pocket FM</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Open Sans', sans-serif;
            background-color: #f4f4f4;
            color: #000000;
            padding: 40px 20px 100px 20px;
        }
        .document-container {
            max-width: 850px;
            margin: 0 auto 60px auto;
            background-color: #ffffff;
            border: none;
            padding: 20px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.06);
            position: relative;
        }
        .inner-wrapper {
            border: 1px solid #000000;
            padding: 15px;
        }
        .content-padding {
            padding: 30px;
        }
        .header {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background-color: #0c0c0c;
            padding: 22px 20px 18px 20px;
            color: #ffffff;
            position: relative;
            overflow: hidden;
            border-radius: 8px 8px 0 0;
            text-align: center;
        }
        .logo {
            height: 52px;
            margin-bottom: 6px;
            object-fit: contain;
        }
        .header-title {
            font-size: 30px;
            font-weight: 700;
            margin-bottom: 3px;
        }
        .header-title span { color: #E51A4D; }
        .company-title {
            font-size: 14px;
            color: #cccccc;
        }
        .intro-block {
            margin: 25px 0;
            font-size: 14px;
            line-height: 1.6;
            color: #333333;
        }
        .intro-greeting {
            font-weight: 700;
            font-size: 16px;
            margin-bottom: 8px;
            color: #000000;
        }
        .metrics-row {
            display: flex;
            gap: 20px;
            margin: 30px 0;
        }
        .metric-box {
            flex: 1;
            display: flex;
            border: 1px solid #000000;
        }
        .metric-label {
            flex: 1;
            padding: 12px;
            font-weight: 700;
            font-size: 13px;
            background-color: #f0f0f0;
            border-right: 1px solid #000000;
            display: flex;
            align-items: center;
        }
        .metric-value {
            flex: 1;
            padding: 12px;
            font-size: 18px;
            font-weight: 700;
            text-align: right;
            background-color: #ffffff;
            display: flex;
            align-items: center;
            justify-content: flex-end;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }
        th, td {
            border: 1px solid #000000;
            padding: 10px 12px;
            vertical-align: middle;
        }
        .info-table {
            margin-bottom: 30px;
        }
        .info-table td:first-child {
            font-weight: 700;
            background-color: #f0f0f0;
            width: 35%;
        }
        .info-table td:last-child {
            font-weight: 700;
            color: #000000;
        }
        .items-table {
            margin-bottom: 35px;
        }
        .items-table th {
            font-weight: 700;
            text-align: left;
            background-color: #E51A4D;
            color: #ffffff;
            text-transform: uppercase;
            font-size: 13px;
            letter-spacing: 0.5px;
        }
        .items-table td:first-child { text-align: left; }
        .items-table td:last-child { text-align: right; }
        .payout-row {
            background-color: #d9d9d9;
            font-weight: 700;
            font-size: 15px;
        }
        .notes-block {
            margin-bottom: 35px;
            font-size: 13.5px;
            color: #333333;
            line-height: 1.6;
        }
        .notes-title {
            font-weight: 700;
            font-size: 15px;
            margin-bottom: 8px;
            color: #000000;
        }
        .notes-block ul {
            margin: 0;
            padding-left: 20px;
        }
        .notes-block li {
            margin-bottom: 4px;
        }
        .footer {
            border-top: 1px solid #b3b3b3;
            padding-top: 10px;
            margin-top: 50px;
            font-size: 11px;
            color: #444444;
            line-height: 1.6;
        }
        .download-btn {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background-color: #E51A4D;
            color: #ffffff;
            border: none;
            padding: 14px 24px;
            font-size: 15px;
            font-weight: 600;
            border-radius: 50px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(229, 26, 77, 0.4);
            display: flex;
            align-items: center;
            gap: 8px;
            transition: background 0.2s ease, transform 0.2s ease;
        }
        .download-btn:hover {
            background-color: #c4123e;
            transform: translateY(-2px);
        }
        @media print {
            body { background-color: #ffffff; padding: 0; }
            .document-container { box-shadow: none; margin: 0; padding: 0; max-width: 100%; }
            .download-btn { display: none; }
        }
    </style>
</head>
<body>
    <button class="download-btn" onclick="window.print()">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="7 10 12 15 17 10"></polyline>
            <line x1="12" y1="15" x2="12" y2="3"></line>
        </svg>
        Download PDF
    </button>
    <div class="document-container">
        <div class="inner-wrapper">
            <div class="content-padding">
                <div class="header">
                    <img src="https://d2p67bdkbtpxn2.cloudfront.net/c8b7ada83f09146d4b2c2ba3a5c3c1b8ea36e459.jpg" alt="Pocket FM Logo" class="logo">
                    <div class="header-title"><span>Revenue</span> Statement</div>
                    <div class="company-title">Pocket Entertainment Services LLC</div>
                </div>
                <div class="intro-block">
                    <div class="intro-greeting">Hi {{FIRST_NAME}},</div>
                    <div>{{INTRO_LABEL}} <span style="font-weight: 700; color: #000;">{{SERIES_NAME}}</span>. Thank you for partnering with Pocket FM. Below is a summary of your show's performance and revenue calculations.</div>
                </div>
                <div class="metrics-row">
                    <div class="metric-box">
                        <div class="metric-label">TOTAL PLAYS</div>
                        <div class="metric-value">{{TOTAL_PLAYS}}</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-label">TOTAL LISTENERS</div>
                        <div class="metric-value">{{TOTAL_LISTENERS}}</div>
                    </div>
                </div>
                <table class="info-table">
                    <tr>
                        <td>Series Name</td>
                        <td>{{SERIES_NAME}}</td>
                    </tr>
                    <tr>
                        <td>Author</td>
                        <td>{{AUTHOR_NAME}}</td>
                    </tr>
                    <tr>
                        <td>Reporting Period</td>
                        <td>{{REPORTING_PERIOD}}</td>
                    </tr>
                </table>
                <table class="items-table">
                    <thead>
                        <tr>
                            <th colspan="2">Revenue Breakdown</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="font-weight: 700;">Revenue Generated (Gross) $</td>
                            <td>{{REVENUE_GROSS}}</td>
                        </tr>
                        <tr>
                            <td>Revenue Share at {{REV_SHARE_PERCENT}}% Gross Revenue $</td>
                            <td>{{REV_SHARE_AMOUNT}}</td>
                        </tr>
                        <tr>
                            <td style="color: transparent;">-</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td>MG Paid $</td>
                            <td>{{MG_PAID}}</td>
                        </tr>
                        <tr>
                            <td>MG to be recouped $</td>
                            <td>{{MG_RECOUPED}}</td>
                        </tr>
                        <tr class="payout-row">
                            <td style="padding: 12px;">Final Payout $</td>
                            <td style="padding: 12px;">{{FINAL_PAYOUT}}</td>
                        </tr>
                    </tbody>
                </table>
                <div class="notes-block">
                    <div class="notes-title">Please Note</div>
                    <ul>
                        <li>Revenue is first adjusted against your Minimum Guarantee (MG).</li>
                        <li>Once the MG has been fully recouped, future quarterly statements will include payable earnings.</li>
                    </ul>
                </div>
                <div class="footer">
                    <div><strong>Address:</strong> Pocket Entertainment Services LLC, 13 West Main Street, PO BOX 953, Felton, Delaware, USA 19943</div>
                    <div style="display: flex; justify-content: space-between;">
                        <div><strong>Email:</strong> us-licensing@pocketfm.com</div>
                        <div>Page 1 of 1</div>
                    </div>
                    <div><strong>Website:</strong> <a href="https://www.pocketfm.com" style="color: #0056b3;">www.pocketfm.com</a></div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>`;
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
  Logger.log("[CMS] openCmsScraperWindow triggered from menu. Opening interactive live scraper popup dialog inside Google Sheets...");
  if (typeof openCmsScraperDialog === "function") {
    Logger.log("[CMS] Delegating to openCmsScraperDialog()...");
    openCmsScraperDialog();
    Logger.log("[CMS] Dialog opened successfully. User interacts with the scraper in the popup window.");
    return;
  }
  Logger.log("[CMS] openCmsScraperDialog not found in current namespace. Displaying fallback launcher...");
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
