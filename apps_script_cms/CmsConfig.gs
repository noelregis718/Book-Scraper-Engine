/**
 * =======================================================================
 * POCKET FM CMS SCRAPER & DATA MANAGER - MODULE 1: CONFIGURATION
 * File: CmsConfig.gs (or CmsConfig.js)
 * =======================================================================
 * Single source of truth for:
 * - Target spreadsheet ID & sheet names
 * - Column mapping definitions
 * - CMS API & Base URLs
 * - Secure Script Properties (Session Token / Cookies)
 * - Metric sanitizers and number formatters
 */

// Target Sheet Configuration
const SPREADSHEET_ID = "1JFT4_f9Du6UZWi6aM0FjYvyR-mcAsbARq7JyxJwLPZc";
const CMS_SHEET_NAME = "CMS Show Data";
const MASTER_TRACKER_SHEET_NAME = "Lifecycle Tracker - Master";
const POST_SALES_SHEET_NAME = "Post-Sales Tracker";

// Standard Column Headers for CMS Show Data Tab
const CMS_COLUMNS = [
  "Show ID",
  "Show Name",
  "Plays",
  "Duration",
  "Ratings",
  "Reviews",
  "Comments",
  "Listening Hours",
  "Status",
  "Last Synced"
];

// Pocket FM CMS Base URLs
const CMS_BASE_URL = "https://cms.pocketfm.com";
const CMS_SHOW_URL = "https://cms.pocketfm.com/shows/audiobooks?tab=published&id=";

// Secure Script Property Key for Session Authentication
const PROP_CMS_AUTH_TOKEN = "POCKETFM_CMS_SESSION_TOKEN";
const PROP_WEBHOOK_SECRET = "CMS_WEBHOOK_SECRET_KEY";

/**
 * Returns the active or target Google Spreadsheet instance (works both container-bound and standalone)
 * @returns {GoogleAppsScript.Spreadsheet.Spreadsheet}
 */
function getCmsSpreadsheet() {
  try {
    return SpreadsheetApp.getActiveSpreadsheet() || SpreadsheetApp.openById(SPREADSHEET_ID);
  } catch (err) {
    return SpreadsheetApp.openById(SPREADSHEET_ID);
  }
}

/**
 * Finds or auto-creates the 'CMS Show Data' tab (with fallback to existing data tabs)
 * @param {GoogleAppsScript.Spreadsheet.Spreadsheet} ss - Optional spreadsheet instance
 * @returns {GoogleAppsScript.Spreadsheet.Sheet}
 */
function getOrCreateCmsSheet(ss = null) {
  const spreadsheet = ss || getCmsSpreadsheet();
  let sheet = spreadsheet.getSheets().find(s => {
    const n = s.getName().toLowerCase().trim();
    return n.includes("cms show") || n.includes("cms data") || n.includes("argus");
  });

  if (!sheet) {
    sheet = spreadsheet.insertSheet(CMS_SHEET_NAME);
    sheet.appendRow(CMS_COLUMNS);
    sheet.setFrozenRows(1);
    sheet.getRange(1, 1, 1, CMS_COLUMNS.length)
      .setBackground("#7a0000")
      .setFontColor("#ffffff")
      .setFontWeight("bold");
  }
  return sheet;
}

/**
 * Resolves column index mapping dynamically from the sheet header row (1-based index)
 * @param {GoogleAppsScript.Spreadsheet.Sheet} sheet 
 * @returns {Object} Map of column names to 1-based column indices
 */
function resolveCmsHeaderMap(sheet) {
  const lastCol = Math.max(sheet.getLastColumn(), CMS_COLUMNS.length);
  const headers = sheet.getRange(1, 1, 1, lastCol).getValues()[0];
  const colMap = {};

  const findIdx = (keywords) => {
    return headers.findIndex(h => {
      const str = (h || "").toString().toLowerCase().trim();
      return keywords.some(k => str.includes(k.toLowerCase()));
    });
  };

  colMap.showId = findIdx(["show id", "show_id", "id"]) + 1;
  colMap.showName = findIdx(["show name", "title", "name"]) + 1;
  colMap.plays = findIdx(["plays", "ldau", "listeners"]) + 1;
  colMap.duration = findIdx(["duration", "duration produced", "hours"]) + 1;
  colMap.ratings = findIdx(["ratings", "rating"]) + 1;
  colMap.reviews = findIdx(["reviews", "review"]) + 1;
  colMap.comments = findIdx(["comments", "comment"]) + 1;
  colMap.listeningHours = findIdx(["listening hour", "listening hours"]) + 1;
  colMap.status = findIdx(["status"]) + 1;
  colMap.lastSynced = findIdx(["last synced", "last updated", "synced at"]) + 1;

  // Fallbacks if columns don't exist yet
  if (colMap.showId === 0) colMap.showId = 1;
  if (colMap.showName === 0) colMap.showName = 2;
  if (colMap.plays === 0) colMap.plays = 3;
  if (colMap.duration === 0) colMap.duration = 4;
  if (colMap.ratings === 0) colMap.ratings = 5;
  if (colMap.reviews === 0) colMap.reviews = 6;
  if (colMap.comments === 0) colMap.comments = 7;
  if (colMap.listeningHours === 0) colMap.listeningHours = 8;
  if (colMap.status === 0) colMap.status = 9;
  if (colMap.lastSynced === 0) colMap.lastSynced = 10;

  return colMap;
}

/**
 * Clean & normalize numeric metric strings
 * @param {*} val 
 * @returns {number|string}
 */
function cleanCmsMetric(val) {
  if (val === null || val === undefined) return 0;
  const s = val.toString().trim().replace(/,/g, "");
  if (!s || s.toLowerCase() === "nan" || s.toLowerCase().includes("no ")) return 0;
  const num = Number(s);
  return isNaN(num) ? s : num;
}

/**
 * Extracts a valid 40-character hex Show ID from any URL or string
 * @param {string} raw 
 * @returns {string} 40-char Show ID or empty string
 */
function extractShowId(raw) {
  if (!raw) return "";
  const match = raw.toString().match(/[a-f0-9]{40}/i);
  return match ? match[0].toLowerCase() : "";
}

/**
 * Stores the Pocket FM CMS session token / cookie securely in Script Properties
 * @param {string} token 
 */
function setCmsAuthToken(token) {
  const props = PropertiesService.getScriptProperties();
  if (token && token.trim()) {
    props.setProperty(PROP_CMS_AUTH_TOKEN, token.trim());
  } else {
    props.deleteProperty(PROP_CMS_AUTH_TOKEN);
  }
}

/**
 * Retrieves the stored Pocket FM CMS session token
 * @returns {string}
 */
function getCmsAuthToken() {
  return PropertiesService.getScriptProperties().getProperty(PROP_CMS_AUTH_TOKEN) || "";
}

/**
 * Generates or retrieves the Webhook security secret token
 * @returns {string}
 */
function getWebhookSecret() {
  const props = PropertiesService.getScriptProperties();
  let secret = props.getProperty(PROP_WEBHOOK_SECRET);
  if (!secret) {
    secret = Utilities.getUuid().replace(/-/g, "").substring(0, 16);
    props.setProperty(PROP_WEBHOOK_SECRET, secret);
  }
  return secret;
}

/**
 * Safe toast notification that works in container-bound UI and gracefully falls back to Logger in standalone/headless context
 * @param {GoogleAppsScript.Spreadsheet.Spreadsheet} ss 
 * @param {string} msg 
 * @param {string} title 
 * @param {number} timeoutSec 
 */
function safeToast(ss, msg, title = "Pocket FM CMS", timeoutSec = 3) {
  try {
    if (ss && typeof ss.toast === "function") {
      ss.toast(msg, title, timeoutSec);
      return;
    }
  } catch (e) {
    // Standalone or background execution has no UI notification context
  }
  Logger.log(`[${title}] ${msg}`);
}

/**
 * Safe UI alert that works in container-bound UI and gracefully falls back to Logger in standalone/headless context
 * @param {string} title 
 * @param {string} message 
 */
function safeAlert(title, message) {
  try {
    const ui = SpreadsheetApp.getUi();
    if (ui) {
      ui.alert(title, message, ui.ButtonSet.OK);
      return;
    }
  } catch (e) {
    // Standalone execution has no UI
  }
  Logger.log(`[ALERT: ${title}]\n${message}`);
}

