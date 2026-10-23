/**
 * =============================================================
 * POCKET FM LIFECYCLE CRM AUTOMATION - MODULE 1: CONFIG & UTILS
 * File: Config.gs (or Config.js)
 * =============================================================
 * Single source of truth for:
 * - Spreadsheet IDs & GIDs
 * - Central Row Filter (isTrackerRowFilled)
 * - Safe Multi-Format Date Parser (parseDateSafe)
 * - Email and CC Sanitizers (cleanEmail, cleanCcList, isValidEmail)
 * - Sheet and Column Resolvers
 */

// Global Spreadsheet Constants
const SPREADSHEET_ID = "1A1vJ0DsmDxtCFZiuyu6vtuQFWqClPyK7e1_lHKddGdQ";
const POST_SALES_TRACKER_GID = 120747375;

/**
 * Returns the active or target Google Spreadsheet instance
 */
function getSpreadsheet() {
  try {
    return SpreadsheetApp.getActiveSpreadsheet() || SpreadsheetApp.openById(SPREADSHEET_ID);
  } catch (err) {
    return SpreadsheetApp.openById(SPREADSHEET_ID);
  }
}

/**
 * Returns the Post-Sales Tracker sheet tab using exact GID matching and fuzzy name fallbacks
 */
function getPostSalesTrackerSheet(ss = null) {
  const spreadsheet = ss || getSpreadsheet();
  for (let s of spreadsheet.getSheets()) {
    if (s.getSheetId() === POST_SALES_TRACKER_GID) return s;
    let sName = s.getName().toLowerCase().trim().replace("–", "-").replace("—", "-");
    if (sName.includes("post-sales tracker") || sName.includes("post sales tracker") || sName.includes("post sale comms tracker")) {
      return s;
    }
  }
  return null;
}

/**
 * Returns the Lifecycle Tracker - Master sheet tab
 */
function getMainTrackerSheet(ss = null) {
  const spreadsheet = ss || getSpreadsheet();
  for (let s of spreadsheet.getSheets()) {
    let sName = s.getName().toLowerCase().trim().replace("–", "-").replace("—", "-");
    if (sName === "lifecycle tracker - master" || sName.includes("lifecycle tracker - master")) {
      return s;
    }
  }
  return null;
}

/**
 * Returns the Queue sheet tab for logging GMass queue data
 */
function getQueueSheet(ss = null) {
  const spreadsheet = ss || getSpreadsheet();
  if (!spreadsheet) return null;
  // 1. Exact match 'queue' or common variations
  for (let s of spreadsheet.getSheets()) {
    let name = s.getName().toLowerCase().trim();
    if (name === "queue" || name === "gmass queue" || name === "email queue" || name === "outreach queue") return s;
  }
  // 2. Fuzzy match containing 'queue'
  for (let s of spreadsheet.getSheets()) {
    let name = s.getName().toLowerCase().trim();
    if (name.includes("queue")) return s;
  }
  // 3. Fallback: auto-create 'Queue' sheet if missing
  try {
    let newSheet = spreadsheet.insertSheet("Queue");
    newSheet.appendRow([
      "Queue ID", "Recipient Email", "Sender Email", "Template Name", "Subject",
      "Body", "Send Date", "Send Time", "Status", "Tracker Row",
      "Sheet Name", "CC", "Status Col", "Stage Type"
    ]);
    return newSheet;
  } catch (e) {
    return null;
  }
}

/**
 * Returns the Argus Show Data sheet tab
 */
function getArgusSheet(ss = null) {
  const spreadsheet = ss || getSpreadsheet();
  return spreadsheet.getSheets().find(s => s.getName().toLowerCase().includes("argus")) || null;
}

/**
 * CENTRAL BLANK ROW GATEKEEPER:
 * Ensures triggers and batch runners strictly run for rows populated with real data.
 * Skips blank or empty placeholder rows (e.g. Rows 113 to 996).
 * 
 * @param {Array} rowVals - Array of row cell values
 * @param {number} titleCol - Column index for Title / IP (default 2)
 * @returns {boolean} True if row contains valid Title / IP and actual deal data, false if blank
 */
function isTrackerRowFilled(rowVals, titleCol = 2) {
  if (!rowVals || rowVals.length === 0) return false;
  let rawTitle = (titleCol > -1 && rowVals.length > titleCol && rowVals[titleCol]) 
                 ? rowVals[titleCol].toString().trim() : "";
  if (!rawTitle || rawTitle === "" || rawTitle === "-" || rawTitle === "#N/A" || 
      rawTitle.toLowerCase() === "n/a" || rawTitle.startsWith("#")) {
    return false;
  }
  // Check that row has at least one other non-empty cell beside title
  for (let c = 0; c < rowVals.length; c++) {
    if (c === titleCol) continue;
    let val = rowVals[c];
    if (val !== null && val !== undefined && val.toString().trim() !== "" && val.toString().trim() !== "-") {
      return true;
    }
  }
  return false;
}

/**
 * EMAIL SANITIZATION & VALIDATION HELPERS
 */
function cleanEmail(rawEmail) {
  if (!rawEmail) return "";
  let str = rawEmail.toString().trim();
  let bracketMatch = str.match(/<([^>]+)>/);
  if (bracketMatch) {
    str = bracketMatch[1].trim();
  } else {
    str = str.replace(/^[<"'\s]+|[>"'\s;]+$/g, "");
  }
  return str;
}

function isValidEmail(emailStr) {
  if (!emailStr) return false;
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailStr);
}

function cleanCcList(rawCc) {
  if (!rawCc) return "";
  let parts = rawCc.toString().split(/[,;]/);
  let cleaned = parts.map(p => cleanEmail(p)).filter(p => isValidEmail(p));
  return cleaned.join(", ");
}

/**
 * SAFE MULTI-FORMAT DATE PARSER:
 * Handles:
 * - Date objects
 * - Excel serial dates (e.g. 45571)
 * - Ordinal text dates ("2nd october", "6 th october", "10th october 2026")
 * - DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD
 */
function parseDateSafe(dateVal) {
  if (!dateVal) return null;
  if (dateVal instanceof Date) {
    if (!isNaN(dateVal.getTime())) return dateVal;
    return null;
  }

  // Handle Excel Serial Numbers (e.g. 45000+)
  if (typeof dateVal === 'number' && dateVal > 30000 && dateVal < 60000) {
    let d = new Date(Math.round((dateVal - 25569) * 86400 * 1000));
    if (!isNaN(d.getTime())) return d;
  }

  let cleanStr = dateVal.toString().trim().replace(/–|—/g, "-");
  if (cleanStr === "" || cleanStr === "-" || cleanStr === "N/A" || cleanStr === "#N/A") return null;

  // Handle textual ordinals without year: e.g. "2nd october", "6 th october", "10th october"
  let ordinalMatch = cleanStr.match(/^(\d{1,2})(?:st|nd|rd|th)?\s+([a-zA-Z]+)(?:\s+(\d{4}))?$/i);
  if (ordinalMatch) {
    let day = parseInt(ordinalMatch[1], 10);
    let monthName = ordinalMatch[2];
    let year = ordinalMatch[3] ? parseInt(ordinalMatch[3], 10) : new Date().getFullYear();
    let d = new Date(`${monthName} ${day}, ${year}`);
    if (!isNaN(d.getTime())) return d;
  }

  // Handle "October 2nd", "Oct 6"
  let textMatch2 = cleanStr.match(/^([a-zA-Z]+)\s+(\d{1,2})(?:st|nd|rd|th)?(?:\s+(\d{4}))?$/i);
  if (textMatch2) {
    let monthName = textMatch2[1];
    let day = parseInt(textMatch2[2], 10);
    let year = textMatch2[3] ? parseInt(textMatch2[3], 10) : new Date().getFullYear();
    let d = new Date(`${monthName} ${day}, ${year}`);
    if (!isNaN(d.getTime())) return d;
  }

  // Check for DD/MM/YYYY or DD-MM-YYYY (with optional time)
  let dmyMatch = cleanStr.match(/^(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})(?:[\sT].*)?$/);
  if (dmyMatch) {
    let p1 = parseInt(dmyMatch[1], 10);
    let p2 = parseInt(dmyMatch[2], 10);
    let year = parseInt(dmyMatch[3], 10);
    if (p1 > 12 && p2 <= 12) {
      return new Date(year, p2 - 1, p1);
    }
    if (p1 <= 12 && p2 > 12) {
      return new Date(year, p1 - 1, p2);
    }
    return new Date(year, p2 - 1, p1);
  }

  // Check for YYYY-MM-DD
  let ymdMatch = cleanStr.match(/^(\d{4})[\/\-](\d{1,2})[\/\-](\d{1,2})(?:[\sT].*)?$/);
  if (ymdMatch) {
    return new Date(parseInt(ymdMatch[1], 10), parseInt(ymdMatch[2], 10) - 1, parseInt(ymdMatch[3], 10));
  }

  const currentYear = new Date().getFullYear();
  let strWithYear = cleanStr;
  if (!/\b\d{4}\b/.test(cleanStr)) {
    strWithYear = cleanStr + " " + currentYear;
  }

  let parsed = new Date(strWithYear);
  if (!isNaN(parsed.getTime())) {
    return parsed;
  }

  parsed = new Date(cleanStr);
  if (!isNaN(parsed.getTime())) {
    if (parsed.getFullYear() < 2000) {
      parsed.setFullYear(currentYear);
    }
    return parsed;
  }

  return null;
}

function isDueTodayOrPast(dateVal) {
  if (!dateVal) return false;
  let target = parseDateSafe(dateVal);
  if (!target) return false;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  let cmp = new Date(target.getTime());
  cmp.setHours(0, 0, 0, 0);
  return today.getTime() >= cmp.getTime();
}

function isDaysAgo(dateVal, days) {
  if (!dateVal) return false;
  let targetDate = parseDateSafe(dateVal);
  if (!targetDate) return false;
  const today = new Date();
  today.setHours(0,0,0,0);
  targetDate.setHours(0,0,0,0);
  const diffTime = Math.abs(today.getTime() - targetDate.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)); 
  return diffDays === days;
}

function isDaysAgoOrMore(dateVal, days) {
  if (!dateVal) return false;
  let targetDate = parseDateSafe(dateVal);
  if (!targetDate) return false;
  const today = new Date();
  today.setHours(0,0,0,0);
  targetDate.setHours(0,0,0,0);
  const diffTime = today.getTime() - targetDate.getTime();
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24)); 
  return diffDays >= days;
}

function isToday(dateVal) {
  if (!dateVal) return false;
  let target = parseDateSafe(dateVal);
  if (!target) return false;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  let cmp = new Date(target.getTime());
  cmp.setHours(0, 0, 0, 0);
  return today.getTime() === cmp.getTime();
}

/**
 * Checks if a contract / deal was signed before 1st September 2026.
 * @param {*} dateVal - Date object, date string, or serial date
 * @returns {boolean} True if deal was signed before 1st September 2026
 */
function isDealSignedBeforeSept1(dateVal) {
  if (!dateVal) return false;
  let target = parseDateSafe(dateVal);
  if (!target) return false;
  let cmp = new Date(target.getTime());
  cmp.setHours(0, 0, 0, 0);
  let cutoff = new Date(2026, 8, 1, 0, 0, 0, 0); // September 1, 2026 (Month index 8 = September)
  return cmp.getTime() <= cutoff.getTime(); // Inclusive: deals signed on or before 1st September
}


/**
 * DYNAMIC COLUMN RESOLVER FOR POST-SALES TRACKER HEADERS (Row 3)
 */
function resolveTrackerColumns(headers) {
  const findCol = (name) => headers.findIndex(h => h.toString().toLowerCase().includes(name.toLowerCase()));

  return {
    titleCol: findCol("Title / IP") > -1 ? findCol("Title / IP") : 2,
    authorCol: findCol("Author Name") > -1 ? findCol("Author Name") : 1,
    contractDateCol: findCol("Contract Signing date") > -1 ? findCol("Contract Signing date") : 3,
    mgPayoutDueCol: findCol("MG payout due") > -1 ? findCol("MG payout due") : 4,
    emailCol: findCol("Receiver Email ID") > -1 ? findCol("Receiver Email ID") : 5,
    ccCol: findCol("CC Mail ID") > -1 ? findCol("CC Mail ID") : 6,
    firstNameCol: findCol("Receiver First Name") > -1 ? findCol("Receiver First Name") : 7,
    showIdCol: findCol("Show ID") > -1 ? findCol("Show ID") : 8,
    launchDateCol: headers.findIndex(h => {
      let s = h.toString().toLowerCase().trim();
      return s === "launch date" || (s.includes("launch") && s.includes("date") && !s.includes("sent") && !s.includes("announcement"));
    }) > -1 ? headers.findIndex(h => {
      let s = h.toString().toLowerCase().trim();
      return s === "launch date" || (s.includes("launch") && s.includes("date") && !s.includes("sent") && !s.includes("announcement"));
    }) : 9,
    statusCol: findCol("Launch Status") > -1 ? findCol("Launch Status") : 10,
    linkCol: findCol("Show Link") > -1 ? findCol("Show Link") : 11,
    showNameCol: findCol("Show Name") > -1 ? findCol("Show Name") : 12,
    scriptDateCol: headers.findIndex(h => {
      let s = h.toString().toLowerCase().trim();
      return s.includes("script") && s.includes("date");
    }) > -1 ? headers.findIndex(h => {
      let s = h.toString().toLowerCase().trim();
      return s.includes("script") && s.includes("date");
    }) : 14,
    postSalesEligibleCol: findCol("Post Sales Eligible") > -1 ? findCol("Post Sales Eligible") : 15,
    nextActionDueCol: findCol("Next Action Due") > -1 ? findCol("Next Action Due") : 16,
    welcomeCol: findCol("Welcome Email") > -1 ? findCol("Welcome Email") : 17,
    vendorCol: findCol("Vendor Onboarding Email") > -1 ? findCol("Vendor Onboarding Email") : 18,
    mgPayoutInitiatedCol: findCol("MG Payout Initiated") > -1 ? findCol("MG Payout Initiated") : 19,
    mgPayoutConfirmationCol: findCol("MG Payout Confirmation") > -1 ? findCol("MG Payout Confirmation") : 20,
    feedbackMailDateCol: headers.findIndex(h => {
      let s = h.toString().toLowerCase().trim();
      return s.includes("feedback") && s.includes("date");
    }) > -1 ? headers.findIndex(h => {
      let s = h.toString().toLowerCase().trim();
      return s.includes("feedback") && s.includes("date");
    }) : 21,
    checkIn1Col: headers.findIndex(h => {
      let s = h.toString().toLowerCase().trim();
      return s.includes("15 days") && !s.includes("newsletter") && !s.includes("date");
    }) > -1 ? headers.findIndex(h => {
      let s = h.toString().toLowerCase().trim();
      return s.includes("15 days") && !s.includes("newsletter") && !s.includes("date");
    }) : 22,
    checkIn1DateCol: headers.findIndex(h => {
      let s = h.toString().toLowerCase().trim();
      return s.includes("15 days") && !s.includes("newsletter") && s.includes("date");
    }) > -1 ? headers.findIndex(h => {
      let s = h.toString().toLowerCase().trim();
      return s.includes("15 days") && !s.includes("newsletter") && s.includes("date");
    }) : 23,
    checkIn2Col: headers.findIndex(h => {
      let s = h.toString().toLowerCase().trim();
      return s.includes("30 days") && !s.includes("date");
    }) > -1 ? headers.findIndex(h => {
      let s = h.toString().toLowerCase().trim();
      return s.includes("30 days") && !s.includes("date");
    }) : 24,
    checkIn2DateCol: headers.findIndex(h => {
      let s = h.toString().toLowerCase().trim();
      return s.includes("30 days") && s.includes("date");
    }) > -1 ? headers.findIndex(h => {
      let s = h.toString().toLowerCase().trim();
      return s.includes("30 days") && s.includes("date");
    }) : 25,
    colAA: headers.findIndex(h => {
      let s = h.toString().toLowerCase().trim();
      return (s.includes("launch") && s.includes("announcement") && s.includes("status")) || s === "show launch announcement status";
    }) > -1 ? headers.findIndex(h => {
      let s = h.toString().toLowerCase().trim();
      return (s.includes("launch") && s.includes("announcement") && s.includes("status")) || s === "show launch announcement status";
    }) : 26,
    colAB: headers.findIndex(h => {
      let s = h.toString().toLowerCase().trim();
      return (s.includes("launch") && s.includes("announcement") && (s.includes("sent") || s.includes("email sent")) && !s.includes("date"));
    }) > -1 ? headers.findIndex(h => {
      let s = h.toString().toLowerCase().trim();
      return (s.includes("launch") && s.includes("announcement") && (s.includes("sent") || s.includes("email sent")) && !s.includes("date"));
    }) : 27,
    colAC: headers.findIndex(h => {
      let s = h.toString().toLowerCase().trim();
      return (s.includes("launch") && s.includes("announcement") && s.includes("date")) || (s.includes("launch") && s.includes("sent") && s.includes("date"));
    }) > -1 ? headers.findIndex(h => {
      let s = h.toString().toLowerCase().trim();
      return (s.includes("launch") && s.includes("announcement") && s.includes("date")) || (s.includes("launch") && s.includes("sent") && s.includes("date"));
    }) : 28,
    newsletterCol: headers.findIndex(h => {
      let s = h.toString().toLowerCase().trim();
      return s.includes("newsletter") && !s.includes("date");
    }) > -1 ? headers.findIndex(h => {
      let s = h.toString().toLowerCase().trim();
      return s.includes("newsletter") && !s.includes("date");
    }) : 29
  };
}

/**
 * DELETE ALL PROJECT TRIGGERS:
 * Cleans up triggers if resetting the project.
 */
function deleteAllTriggers() {
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    ScriptApp.deleteTrigger(triggers[i]);
  }
  Logger.log("Successfully deleted all " + triggers.length + " triggers!");
}
