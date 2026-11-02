/**
 * =======================================================================
 * POCKET FM CMS SCRAPER & DATA MANAGER - MODULE 3: SYNC ENGINE
 * File: CmsSyncEngine.gs (or CmsSyncEngine.js)
 * =======================================================================
 * Core sheet synchronization engine:
 * - Updates existing rows or appends new shows to 'CMS Show Data'
 * - Loops across all shows with real-time safe logging & toasts
 * - Imports newly created Show IDs from the Master Lifecycle Tracker
 * - Audits missing show metrics and provides professional formatting
 */

/**
 * Updates an existing show row or appends a new row if not present
 * @param {GoogleAppsScript.Spreadsheet.Sheet} sheet 
 * @param {Object} show - { showId, showName, plays, duration, ratings, reviews, comments, listeningHours }
 * @returns {boolean} True if successfully updated/inserted
 */
function updateOrAppendCmsShow(sheet, show) {
  if (!show || !show.showId) return false;
  const cleanId = extractShowId(show.showId);
  if (!cleanId) return false;

  const colMap = resolveCmsHeaderMap(sheet);
  const lastRow = sheet.getLastRow();
  let targetRow = -1;

  if (lastRow > 1) {
    const showIdVals = sheet.getRange(2, colMap.showId, lastRow - 1, 1).getValues();
    for (let i = 0; i < showIdVals.length; i++) {
      const existingId = extractShowId(showIdVals[i][0]);
      if (existingId && existingId === cleanId) {
        targetRow = i + 2;
        break;
      }
    }
  }

  const nowStr = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy-MM-dd HH:mm:ss");

  // If show already exists in CMS sheet, update cells
  if (targetRow > 1) {
    if (show.showName && colMap.showName) sheet.getRange(targetRow, colMap.showName).setValue(show.showName);
    if (show.plays !== undefined && colMap.plays) sheet.getRange(targetRow, colMap.plays).setValue(cleanCmsMetric(show.plays));
    if (show.duration !== undefined && colMap.duration) sheet.getRange(targetRow, colMap.duration).setValue(cleanCmsMetric(show.duration));
    if (show.ratings !== undefined && colMap.ratings) sheet.getRange(targetRow, colMap.ratings).setValue(cleanCmsMetric(show.ratings));
    if (show.reviews !== undefined && colMap.reviews) sheet.getRange(targetRow, colMap.reviews).setValue(cleanCmsMetric(show.reviews));
    if (show.comments !== undefined && colMap.comments) sheet.getRange(targetRow, colMap.comments).setValue(cleanCmsMetric(show.comments));
    if (show.listeningHours !== undefined && colMap.listeningHours) sheet.getRange(targetRow, colMap.listeningHours).setValue(cleanCmsMetric(show.listeningHours));
    if (colMap.lastSynced) sheet.getRange(targetRow, colMap.lastSynced).setValue(nowStr);
    return true;
  }

  // Otherwise, append a new show row
  const newRow = new Array(Math.max(...Object.values(colMap))).fill("");
  newRow[colMap.showId - 1] = cleanId;
  newRow[colMap.showName - 1] = show.showName || "";
  newRow[colMap.plays - 1] = cleanCmsMetric(show.plays || 0);
  newRow[colMap.duration - 1] = cleanCmsMetric(show.duration || 0);
  newRow[colMap.ratings - 1] = cleanCmsMetric(show.ratings || 0);
  newRow[colMap.reviews - 1] = cleanCmsMetric(show.reviews || 0);
  newRow[colMap.comments - 1] = cleanCmsMetric(show.comments || 0);
  newRow[colMap.listeningHours - 1] = cleanCmsMetric(show.listeningHours || show.duration || 0);
  if (colMap.status) newRow[colMap.status - 1] = show.status || "Active";
  if (colMap.lastSynced) newRow[colMap.lastSynced - 1] = nowStr;

  sheet.appendRow(newRow);
  return true;
}

/**
 * Syncs all shows currently listed in 'CMS Show Data' tab directly from CMS
 * @returns {Object} Summary { total, updated, failed }
 */
function syncAllCmsShows() {
  const ss = getCmsSpreadsheet();
  const sheet = getOrCreateCmsSheet(ss);
  const colMap = resolveCmsHeaderMap(sheet);
  const lastRow = sheet.getLastRow();

  if (lastRow <= 1) {
    safeToast(ss, "No shows found in CMS Show Data. Please import shows from Tracker first.", "Pocket FM CMS", 5);
    return { total: 0, updated: 0, failed: 0 };
  }

  const idRange = sheet.getRange(2, colMap.showId, lastRow - 1, 1).getValues();
  const showList = [];

  for (let r = 0; r < idRange.length; r++) {
    const rawId = idRange[r][0];
    const cleanId = extractShowId(rawId);
    if (cleanId) {
      showList.push({ rowIdx: r + 2, showId: cleanId });
    }
  }

  const total = showList.length;
  let updated = 0;
  let failed = 0;
  const errors = [];

  safeToast(ss, `Starting sync for ${total} shows from Pocket FM CMS...`, "Pocket FM CMS", 4);

  for (let i = 0; i < total; i++) {
    const item = showList[i];
    safeToast(ss, `Syncing show [${i + 1}/${total}]: ${item.showId.substring(0, 10)}...`, "CMS Syncing", 2);

    const metrics = fetchShowMetricsFromCms(item.showId);
    if (metrics.success) {
      updateOrAppendCmsShow(sheet, metrics);
      updated++;
    } else {
      failed++;
      errors.push(`${item.showId.substring(0, 10)}: ${metrics.error || "Failed"}`);
    }

    // Gentle buffer to prevent CMS rate limiting
    Utilities.sleep(400);
  }

  SpreadsheetApp.flush();
  const summaryMsg = `CMS Sync Finished!\n\n• Total Shows: ${total}\n• Successfully Updated: ${updated}\n• Failed / Unreachable: ${failed}`;
  Logger.log(summaryMsg);
  
  if (failed > 0) {
    safeAlert("Pocket FM CMS Sync", `${summaryMsg}\n\nTop Errors:\n${errors.slice(0, 5).join("\n")}`);
  } else {
    safeToast(ss, `Sync Complete! Updated all ${updated} shows.`, "Pocket FM CMS", 6);
  }

  return { total, updated, failed };
}

/**
 * Syncs only the show in the currently selected row of the active sheet
 */
function syncActiveRowShow() {
  const ss = getCmsSpreadsheet();
  let sheet = null;
  let activeRow = -1;

  try {
    sheet = ss.getActiveSheet();
    activeRow = sheet.getActiveCell().getRow();
  } catch (e) {
    Logger.log("No active cell context in standalone execution. Please run syncAllCmsShows instead.");
    return;
  }

  if (activeRow <= 1) {
    safeToast(ss, "Please select a valid data row (row 2 or below).", "Pocket FM CMS", 4);
    return;
  }

  const rowVals = sheet.getRange(activeRow, 1, 1, sheet.getLastColumn()).getValues()[0];
  let showId = "";

  // Scan row cells to find 40-char hex show ID
  for (let val of rowVals) {
    const extracted = extractShowId(val);
    if (extracted) {
      showId = extracted;
      break;
    }
  }

  if (!showId) {
    safeToast(ss, "No valid 40-character Show ID found in the selected row.", "Pocket FM CMS", 4);
    return;
  }

  safeToast(ss, `Fetching metrics for Show ID ${showId.substring(0, 10)}...`, "CMS Scraper", 3);
  const metrics = fetchShowMetricsFromCms(showId);

  if (metrics.success) {
    const cmsSheet = getOrCreateCmsSheet(ss);
    updateOrAppendCmsShow(cmsSheet, metrics);
    SpreadsheetApp.flush();
    safeToast(ss, `Updated: "${metrics.showName || showId}" | Plays: ${metrics.plays} | Dur: ${metrics.duration}`, "CMS Scraper", 6);
  } else {
    safeToast(ss, `Sync Failed: ${metrics.error}`, "Pocket FM CMS Error", 6);
  }
}

/**
 * Scans Master / Post-Sales Tracker, discovers newly added Show IDs, and auto-imports them to CMS sheet
 * @returns {number} Count of newly imported shows
 */
function importNewShowsFromTracker() {
  const ss = getCmsSpreadsheet();
  const cmsSheet = getOrCreateCmsSheet(ss);
  const colMap = resolveCmsHeaderMap(cmsSheet);

  // 1. Get existing Show IDs in CMS Sheet
  const existingIds = new Set();
  const lastRowCms = cmsSheet.getLastRow();
  if (lastRowCms > 1) {
    const aVals = cmsSheet.getRange(2, colMap.showId, lastRowCms - 1, 1).getValues();
    aVals.forEach(r => {
      const sid = extractShowId(r[0]);
      if (sid) existingIds.add(sid);
    });
  }

  // 2. Locate Master Tracker Sheet
  const masterSheet = ss.getSheets().find(s => {
    const name = s.getName().toLowerCase().trim();
    return name.includes("lifecycle tracker - master") || name.includes("post-sales");
  });

  if (!masterSheet) {
    safeToast(ss, "Could not find Master Lifecycle Tracker sheet to import from.", "Pocket FM CMS", 5);
    return 0;
  }

  const mHeaders = masterSheet.getRange(1, 1, 1, masterSheet.getLastColumn()).getValues()[0];
  const sidColIdx = mHeaders.findIndex(h => (h || "").toString().toLowerCase().includes("show id")) + 1;
  const titleColIdx = mHeaders.findIndex(h => {
    const s = (h || "").toString().toLowerCase();
    return s.includes("title") || s.includes("show name") || s.includes("ip");
  }) + 1;

  if (sidColIdx === 0) {
    safeToast(ss, "Could not locate 'Show ID' column in Master Tracker.", "Pocket FM CMS", 5);
    return 0;
  }

  const mLastRow = masterSheet.getLastRow();
  let importedCount = 0;

  if (mLastRow > 1) {
    const mData = masterSheet.getRange(2, 1, mLastRow - 1, masterSheet.getLastColumn()).getValues();
    mData.forEach(row => {
      const rawSid = row[sidColIdx - 1];
      const sid = extractShowId(rawSid);
      const title = titleColIdx > 0 ? (row[titleColIdx - 1] || "").toString().trim() : "";

      if (sid && !existingIds.has(sid)) {
        updateOrAppendCmsShow(cmsSheet, {
          showId: sid,
          showName: title,
          plays: 0,
          duration: 0,
          ratings: 0,
          reviews: 0,
          comments: 0,
          listeningHours: 0
        });
        existingIds.add(sid);
        importedCount++;
      }
    });
  }

  SpreadsheetApp.flush();
  safeToast(ss, `Imported ${importedCount} new shows from Master Tracker into CMS sheet!`, "Pocket FM CMS", 6);
  return importedCount;
}

/**
 * Audits shows in Master Tracker that are missing from CMS Show Data
 */
function auditMissingCmsData() {
  const ss = getCmsSpreadsheet();
  const cmsSheet = getOrCreateCmsSheet(ss);
  const colMap = resolveCmsHeaderMap(cmsSheet);

  const existingIds = new Set();
  const lastRow = cmsSheet.getLastRow();
  if (lastRow > 1) {
    const aVals = cmsSheet.getRange(2, colMap.showId, lastRow - 1, 1).getValues();
    aVals.forEach(r => {
      const sid = extractShowId(r[0]);
      if (sid) existingIds.add(sid);
    });
  }

  const masterSheet = ss.getSheets().find(s => {
    const name = s.getName().toLowerCase().trim();
    return name.includes("lifecycle tracker - master") || name.includes("post-sales");
  });

  if (!masterSheet) {
    safeAlert("Audit Error", "Could not locate Master Lifecycle Tracker sheet.");
    return;
  }

  const mHeaders = masterSheet.getRange(1, 1, 1, masterSheet.getLastColumn()).getValues()[0];
  const sidColIdx = mHeaders.findIndex(h => (h || "").toString().toLowerCase().includes("show id")) + 1;
  const titleColIdx = mHeaders.findIndex(h => {
    const s = (h || "").toString().toLowerCase();
    return s.includes("title") || s.includes("show name") || s.includes("ip");
  }) + 1;

  const missingList = [];
  const mLastRow = masterSheet.getLastRow();
  if (mLastRow > 1 && sidColIdx > 0) {
    const mData = masterSheet.getRange(2, 1, mLastRow - 1, masterSheet.getLastColumn()).getValues();
    mData.forEach((row, idx) => {
      const sid = extractShowId(row[sidColIdx - 1]);
      const title = titleColIdx > 0 ? (row[titleColIdx - 1] || `Row ${idx + 2}`) : `Row ${idx + 2}`;
      if (sid && !existingIds.has(sid)) {
        missingList.push(`• Row ${idx + 2}: "${title}" (ID: ${sid.substring(0, 10)}...)`);
      }
    });
  }

  if (missingList.length === 0) {
    safeAlert("CMS Data Audit", "All shows with a Show ID in Master Tracker are present in CMS Show Data! 100% matched.");
  } else {
    safeAlert("CMS Data Audit", `Found ${missingList.length} shows missing from CMS:\n\n${missingList.slice(0, 12).join("\n")}\n\nTip: Click 'Import New Shows from Master Tracker' to add them automatically.`);
  }
}

/**
 * Applies clean Pocket FM crimson branding and formatting to 'CMS Show Data' tab
 */
function cleanAndFormatCmsSheet() {
  const ss = getCmsSpreadsheet();
  const sheet = getOrCreateCmsSheet(ss);
  const lastCol = sheet.getLastColumn();
  const lastRow = sheet.getLastRow();

  if (lastCol < 1) return;

  sheet.setFrozenRows(1);
  const headerRange = sheet.getRange(1, 1, 1, lastCol);
  headerRange
    .setBackground("#7a0000")
    .setFontColor("#ffffff")
    .setFontWeight("bold")
    .setHorizontalAlignment("center");

  if (lastRow > 1) {
    const dataRange = sheet.getRange(2, 1, lastRow - 1, lastCol);
    dataRange.setFontFamily("Arial").setFontSize(10);
  }

  // Auto-resize standard columns
  sheet.autoResizeColumns(1, Math.min(lastCol, 10));
  safeToast(ss, "CMS Show Data tab formatted with Pocket FM styling!", "Pocket FM CMS", 4);
}
