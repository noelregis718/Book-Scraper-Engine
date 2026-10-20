/**
 * =============================================================
 * POCKET FM LIFECYCLE CRM AUTOMATION - MODULE 5: MAIN & TRIGGERS
 * File: Main.gs (or Main.js)
 * =============================================================
 * 9 INDIVIDUAL ISOLATED STAGE TRIGGERS:
 * 1. Welcome Emails Only
 * 2. Vendor Onboarding Only
 * 3. MG Payout Initiated Only
 * 4. MG Payout Confirmation Only
 * 5. Author Check-In 1 (15 Days) Only
 * 6. Author Check-In 2 (30 Days) Only
 * 7. Show Launch Announcements Only
 * 8. Newsletter (The Author Edit) Only
 * 9. Quarterly Revenue Statements Only
 * Bonus: Sync Sent Emails Only
 *
 * ZERO COMMOTION: Each button evaluates and runs ONLY its specific condition!
 * No master "all running together" button.
 */

// Global in-memory log buffer for the current session
var GLOBAL_SESSION_LOGS = [];

/**
 * GOOGLE SHEETS TOP-BAR MENU BUILDER:
 * Creates the "Pocket FM Automation" menu with 9 INDIVIDUAL STAGE TRIGGERS.
 */
function onOpen() {
  try {
    SpreadsheetApp.getUi()
      .createMenu("Pocket FM Automation")
      .addItem("1️⃣ ✉️ Run Welcome Emails Only", "triggerWelcomeEmailsOnly")
      .addItem("2️⃣ 📝 Run Vendor Onboarding Only", "triggerVendorOnboardingOnly")
      .addItem("3️⃣ 💰 Run MG Payout Initiated Only", "triggerMgInitiatedOnly")
      .addItem("4️⃣ ✅ Run MG Payout Confirmation Only", "triggerMgConfirmedOnly")
      .addItem("5️⃣ 📅 Run Author Check-In 1 (15 Days) Only", "triggerCheckIn1Only")
      .addItem("6️⃣ 📆 Run Author Check-In 2 (30 Days) Only", "triggerCheckIn2Only")
      .addItem("7️⃣ 🚀 Run Show Launch Announcements Only", "triggerLaunchAnnouncementsOnly")
      .addItem("8️⃣ 📰 Run Newsletter (The Author Edit) Only", "triggerNewsletterOnly")
      .addItem("🧪 ✉️ Test Newsletter Draft (Generate Directly to My Gmail)", "triggerTestNewsletterDraft")
      .addItem("9️⃣ 📊 Run Quarterly Revenue Statements Only", "triggerRevenueStatementsOnly")
      .addSeparator()
      .addItem("🔄 Sync Sent Emails Only", "triggerSyncSentEmailsOnly")
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
 * 9. TRIGGER: QUARTERLY REVENUE STATEMENTS ONLY
 * Condition: Evaluates AMJ, JAS, OND quarterly statement due dates & links.
 */
function triggerRevenueStatementsOnly() {
  return runSingleStage('revStatement', '9. Quarterly Revenue Statements');
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
