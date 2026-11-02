/**
 * =======================================================================
 * POCKET FM CMS SCRAPER & DATA MANAGER - MODULE 4: UI & MENUS
 * File: CmsMenu.gs (or CmsMenu.js)
 * =======================================================================
 * Custom Google Sheets UI Menu & Interactive User Dialogs:
 * - One-click master runners for CMS sync
 * - Interactive session token setup dialogs
 * - Audit, import, and webhook inspection dialogs
 */

/**
 * Standard Google Sheets onOpen trigger to install custom menu
 */
function onOpen() {
  installCmsMenu();
}

/**
 * Adds the dedicated 'Pocket FM CMS Scraper' menu to Google Sheets UI
 */
function installCmsMenu() {
  try {
    const ui = SpreadsheetApp.getUi();
    ui.createMenu("Pocket FM CMS Scraper")
      .addItem("▶️ Sync All Shows from CMS", "syncAllCmsShows")
      .addItem("🎯 Sync Currently Selected Show", "syncActiveRowShow")
      .addSeparator()
      .addItem("📥 Import Missing Shows from Tracker", "importNewShowsFromTracker")
      .addItem("📊 Audit Shows Missing from CMS", "auditMissingCmsData")
      .addSeparator()
      .addItem("🔑 Set / Update CMS Session Token", "promptSetCmsAuthToken")
      .addItem("👁️ Check CMS Auth Token Status", "checkCmsAuthStatus")
      .addItem("🌐 View Webhook URL & Secret Key", "showWebhookDetailsDialog")
      .addSeparator()
      .addItem("🧹 Clean & Format CMS Sheet", "cleanAndFormatCmsSheet")
      .addToUi();
  } catch (e) {
    Logger.log("CMS menu already loaded or headless execution: " + e);
  }
}

/**
 * UI Prompt allowing users to securely enter or update their CMS session cookie / token
 */
function promptSetCmsAuthToken() {
  const ui = SpreadsheetApp.getUi();
  const currentToken = getCmsAuthToken();
  const maskedCurrent = currentToken ? `(Currently configured: ${currentToken.substring(0, 15)}...)` : "(Currently blank)";

  const promptResult = ui.prompt(
    "Set Pocket FM CMS Session Token",
    `Paste your active Pocket FM CMS session cookie or authorization token.\n${maskedCurrent}\n\nHow to get it:\n1. Open cms.pocketfm.com in Chrome\n2. Press F12 -> Application -> Cookies -> 'https://cms.pocketfm.com'\n3. Copy the session cookie (or from Network tab Authorization header)\n\nPaste value below (or leave empty to clear):`,
    ui.ButtonSet.OK_CANCEL
  );

  if (promptResult.getSelectedButton() === ui.Button.OK) {
    const entered = promptResult.getResponseText().trim();
    if (entered) {
      setCmsAuthToken(entered);
      ui.alert("CMS Auth Token Updated", "Session token has been safely stored in Google Script Properties!\nYou can now run 'Sync All Shows from CMS'.", ui.ButtonSet.OK);
    } else {
      setCmsAuthToken("");
      ui.alert("CMS Auth Token Cleared", "The stored session token has been cleared.", ui.ButtonSet.OK);
    }
  }
}

/**
 * Displays current authentication status
 */
function checkCmsAuthStatus() {
  const ui = SpreadsheetApp.getUi();
  const token = getCmsAuthToken();

  if (token) {
    ui.alert(
      "CMS Token Status: Active",
      `A session token is currently saved in Script Properties.\n\n• Token Preview: ${token.substring(0, 20)}...\n• Length: ${token.length} characters\n\nIf sync returns 401/redirect errors, your session may have expired—simply click 'Set / Update CMS Session Token' to update.`,
      ui.ButtonSet.OK
    );
  } else {
    ui.alert(
      "CMS Token Status: Not Configured",
      "No CMS session token is currently stored.\n\nPlease click 'Set / Update CMS Session Token' to enter your session cookie before syncing directly from Google Sheets.",
      ui.ButtonSet.OK
    );
  }
}

/**
 * Displays Webhook integration details for external scrapers (e.g. Python Playwright)
 */
function showWebhookDetailsDialog() {
  const ui = SpreadsheetApp.getUi();
  const secret = getWebhookSecret();

  const msg = `WEBHOOK INTEGRATION DETAILS\n\n` +
    `You can push metrics directly to this Google Sheet from external Python scripts:\n\n` +
    `• Method: POST\n` +
    `• Payload Format: JSON\n` +
    `• Secret Key: ${secret}\n\n` +
    `Example JSON Payload:\n` +
    `{\n` +
    `  "secret": "${secret}",\n` +
    `  "shows": [\n` +
    `    {\n` +
    `      "showId": "38feeb49bb...",\n` +
    `      "showName": "My Show Title",\n` +
    `      "plays": 12500,\n` +
    `      "duration": 4.5,\n` +
    `      "ratings": 4.8,\n` +
    `      "reviews": 320,\n` +
    `      "comments": 45\n` +
    `    }\n` +
    `  ]\n` +
    `}\n\n` +
    `To deploy this endpoint:\n` +
    `1. Go to Apps Script Editor -> Deploy -> New deployment\n` +
    `2. Select 'Web app' -> Execute as: Me -> Access: Anyone\n` +
    `3. Copy the Web app URL.`;

  ui.alert("Pocket FM CMS Webhook Endpoint", msg, ui.ButtonSet.OK);
}
