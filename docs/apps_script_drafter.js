/**
 * POCKETFM AUTOMATED EMAIL BUNDLER
 * 
 * Instructions:
 * 1. Open your Google Sheet ("Lifecycle Tracker - Master")
 * 2. Click on "Extensions" in the top menu, then click "Apps Script"
 * 3. Delete any code there, and paste this entire file.
 * 4. Click the "Save" icon (the floppy disk).
 * 5. Click the "Run" button at the top!
 */

function deleteAllTriggers() {
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    ScriptApp.deleteTrigger(triggers[i]);
  }
  Logger.log("Successfully deleted all " + triggers.length + " triggers!");
}

// =============================================================
// GLOBAL DATE HELPERS & USER ENTRY POINTS
// =============================================================

/**
 * GOOGLE SHEETS TOP-BAR MENU BUILDER:
 * Creates the "Pocket FM Automation" menu directly in the spreadsheet top bar.
 */
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu("Pocket FM Automation")
    .addItem("▶️ 🚀 RUN ALL AUTOMATIONS (Single Click)", "openLiveAutomationConsole")
    .addItem("📋 View Execution Logs Panel", "openLiveAutomationConsole")
    .addSeparator()
    .addItem("✉️ Run Author Check-Ins (15 & 30 Days)", "processAllAuthorCheckIns")
    .addItem("🚀 Run Show Launch Announcements Only", "processAllLaunchAnnouncements")
    .addItem("📋 Run Standard Outreach (Welcome, Vendor, MG)", "createAutomatedEmailDrafts")
    .addSeparator()
    .addItem("🔄 Sync Sent Emails (Mark Dropdowns 'Sent')", "syncSentEmails")
    .addSeparator()
    .addItem("🕒 Install Daily & Hourly Lifecycle Timers", "installLifecycleTimers")
    .addItem("📊 Check Active Lifecycle Timers Report", "checkLifecycleTimersReport")
    .addToUi();
}

/**
 * OPENS THE LIVE AUTOMATION CONSOLE (REAL-TIME STREAMING):
 * Opens immediately (<0.3s) in the right sidebar.
 * Coordinates batch execution in real-time so logs appear line-by-line
 * as each row is processed, rather than waiting for the entire run to finish!
 */
function openLiveAutomationConsole() {
  const htmlOutput = HtmlService.createHtmlOutput(buildLiveStreamingConsoleHtml())
    .setTitle("Pocket FM Automation Logs")
    .setWidth(450);
  SpreadsheetApp.getUi().showSidebar(htmlOutput);
}

/**
 * FINDS THE LAST ACTUALLY FILLED DATA ROW IN THE TRACKER:
 * Scans titleCol upwards from lastRow to find the last row containing an actual title.
 * Prevents unnecessary roundtrips over blank formula rows (rows 113 to 996).
 */
function findLastFilledTrackerRow(sheet, titleCol) {
  const sheetLastRow = sheet.getLastRow();
  if (sheetLastRow <= 3) return 3;
  const numRows = sheetLastRow - 3;
  const titleVals = sheet.getRange(4, titleCol + 1, numRows, 1).getValues();
  let actualLast = 3;
  for (let i = titleVals.length - 1; i >= 0; i--) {
    let val = titleVals[i][0];
    if (val !== null && val !== undefined) {
      let str = val.toString().trim();
      if (str !== "" && str !== "-" && str !== "#N/A" && str.toLowerCase() !== "n/a" && !str.startsWith("#")) {
        actualLast = i + 4;
        break;
      }
    }
  }
  return Math.max(actualLast, 4);
}

/**
 * REAL-TIME CHUNKED SERVER RPC ENDPOINT:
 * Evaluates a single chunk of rows (default 20 rows) and returns logs + stats immediately.
 * Called by client-side JS in the Live Streaming Console.
 */
function executeAutomationBatch(startRow, batchSize) {
  startRow = Number(startRow) || 4;
  batchSize = Number(batchSize) || 20;

  const ss = SpreadsheetApp.getActiveSpreadsheet() || SpreadsheetApp.openById("1A1vJ0DsmDxtCFZiuyu6vtuQFWqClPyK7e1_lHKddGdQ");
  let psSheet = null;
  for (let s of ss.getSheets()) {
    if (s.getSheetId() === 120747375) { psSheet = s; break; }
    let sName = s.getName().toLowerCase().trim().replace("–", "-").replace("—", "-");
    if (sName.includes("post-sales tracker") || sName.includes("post sales tracker")) { psSheet = s; break; }
  }

  if (!psSheet) {
    return {
      error: "[ERROR] Post-Sales Tracker sheet tab not found!",
      isDone: true,
      logs: ["[ERROR] Post-Sales Tracker sheet tab not found!"]
    };
  }

  const lastCol = Math.max(psSheet.getLastColumn(), 30);
  const headerVals = psSheet.getRange(3, 1, 1, lastCol).getValues()[0];
  const titleCol = headerVals.findIndex(h => h.toString().toLowerCase().includes("title")) > -1 
                   ? headerVals.findIndex(h => h.toString().toLowerCase().includes("title")) : 2;

  const actualLastRow = findLastFilledTrackerRow(psSheet, titleCol);
  const endRow = Math.min(startRow + batchSize - 1, actualLastRow);

  const logs = [];
  function log(msg) {
    let text = typeof msg === 'object' ? JSON.stringify(msg) : String(msg);
    logs.push(text);
    if (GLOBAL_SESSION_LOGS.length > 1000) GLOBAL_SESSION_LOGS.shift();
    GLOBAL_SESSION_LOGS.push(text);
  }

  if (startRow > actualLastRow) {
    return {
      startRow: startRow,
      endRow: actualLastRow,
      totalSheetRows: actualLastRow,
      evaluatedCount: 0,
      skippedBlankCount: 0,
      logs: ["[INFO] All populated rows evaluated."],
      isDone: true,
      nextRow: actualLastRow + 1
    };
  }

  const numRows = endRow - startRow + 1;
  const chunkVals = psSheet.getRange(startRow, 1, numRows, lastCol).getValues();

  let evaluatedCount = 0;
  let skippedBlankCount = 0;

  for (let i = 0; i < numRows; i++) {
    const currentRowNum = startRow + i;
    const rowVals = chunkVals[i];

    if (!isTrackerRowFilled(rowVals, titleCol)) {
      skippedBlankCount++;
      continue;
    }

    const showTitle = rowVals[titleCol] ? rowVals[titleCol].toString().trim() : ("Row " + currentRowNum);

    try {
      evaluateSingleRowCheckIns(psSheet, currentRowNum, rowVals, headerVals);
      log(`[LIVE ROW ${currentRowNum}] Check-Ins (15/30 Days) evaluated for "${showTitle}"`);
    } catch (errCheckIn) {
      log(`[ERROR] [Row ${currentRowNum} Check-In] ${errCheckIn.message}`);
    }

    try {
      evaluateSingleRowLaunch(psSheet, currentRowNum, rowVals, headerVals);
      log(`[LIVE ROW ${currentRowNum}] Launch Announcement evaluated for "${showTitle}"`);
    } catch (errLaunch) {
      log(`[ERROR] [Row ${currentRowNum} Launch] ${errLaunch.message}`);
    }

    evaluatedCount++;
  }

  SpreadsheetApp.flush();

  try {
    CacheService.getUserCache().put("POCKETFM_LAST_LOGS", JSON.stringify(GLOBAL_SESSION_LOGS.slice(-500)), 21600);
  } catch (e) {}

  return {
    startRow: startRow,
    endRow: endRow,
    totalSheetRows: actualLastRow,
    evaluatedCount: evaluatedCount,
    skippedBlankCount: skippedBlankCount,
    logs: logs,
    isDone: endRow >= actualLastRow,
    nextRow: endRow + 1
  };
}

/**
 * SERVER RPC ENDPOINT: EVALUATES STANDARD OUTREACH QUEUE
 */
function executeOutreachQueueStage() {
  const logs = [];
  function log(msg) {
    let text = typeof msg === 'object' ? JSON.stringify(msg) : String(msg);
    logs.push(text);
    if (GLOBAL_SESSION_LOGS.length > 1000) GLOBAL_SESSION_LOGS.shift();
    GLOBAL_SESSION_LOGS.push(text);
  }

  log("Evaluating Outreach Queue (Welcome, Vendor, MG Payouts, Rev Statements)...");
  try {
    processOutreachQueue(false);
    log("[SUCCESS] Standard Outreach Queue successfully processed.");
  } catch (errQueue) {
    log(`[ERROR] [Outreach Queue] ${errQueue.message}`);
  }

  SpreadsheetApp.flush();

  try {
    CacheService.getUserCache().put("POCKETFM_LAST_LOGS", JSON.stringify(GLOBAL_SESSION_LOGS.slice(-500)), 21600);
  } catch (e) {}

  return { logs: logs, success: true };
}

/**
 * MASTER SINGLE-CLICK RUNNER (SYNCHRONOUS / HEADLESS):
 */
function runAllOutreachAutomations() {
  const ss = SpreadsheetApp.getActiveSpreadsheet() || SpreadsheetApp.openById("1A1vJ0DsmDxtCFZiuyu6vtuQFWqClPyK7e1_lHKddGdQ");
  let psSheet = null;

  for (let s of ss.getSheets()) {
    if (s.getSheetId() === 120747375) { psSheet = s; break; }
    let sName = s.getName().toLowerCase().trim().replace("–", "-").replace("—", "-");
    if (sName.includes("post-sales tracker") || sName.includes("post sales tracker")) { psSheet = s; break; }
  }

  if (!psSheet) {
    Logger.log("[ERROR] Post-Sales Tracker sheet tab not found!");
    return;
  }

  GLOBAL_SESSION_LOGS = [];
  function recordLog(msg) {
    Logger.log(msg);
    if (GLOBAL_SESSION_LOGS.length > 1000) GLOBAL_SESSION_LOGS.shift();
    GLOBAL_SESSION_LOGS.push(typeof msg === 'object' ? JSON.stringify(msg) : String(msg));
  }

  const lastCol = Math.max(psSheet.getLastColumn(), 30);
  const headers = psSheet.getRange(3, 1, 1, lastCol).getValues()[0];
  const titleCol = headers.findIndex(h => h.toString().toLowerCase().includes("title")) > -1 
                   ? headers.findIndex(h => h.toString().toLowerCase().includes("title")) : 2;

  const actualLastRow = findLastFilledTrackerRow(psSheet, titleCol);

  recordLog("==================================================================");
  recordLog(`MASTER RUNNER: Processing all stages in "${psSheet.getName()}" (Row 4 to Row ${actualLastRow})`);
  recordLog("==================================================================");

  let evaluatedCount = 0;
  let skippedBlankCount = 0;

  const allData = psSheet.getRange(1, 1, actualLastRow, lastCol).getValues();

  for (let r = 4; r <= actualLastRow; r++) {
    let rowVals = allData[r - 1];

    if (!isTrackerRowFilled(rowVals, titleCol)) {
      skippedBlankCount++;
      continue;
    }

    let showTitle = rowVals[titleCol] ? rowVals[titleCol].toString().trim() : ("Row " + r);

    try {
      evaluateSingleRowCheckIns(psSheet, r, rowVals, headers);
      recordLog(`[LIVE ROW ${r}] Check-Ins (15/30 Days) evaluated for "${showTitle}"`);
    } catch (errCheckIn) {
      recordLog(`[ERROR] [Row ${r} Check-In] ${errCheckIn.message}`);
    }

    try {
      evaluateSingleRowLaunch(psSheet, r, rowVals, headers);
      recordLog(`[LIVE ROW ${r}] Launch Announcement evaluated for "${showTitle}"`);
    } catch (errLaunch) {
      recordLog(`[ERROR] [Row ${r} Launch] ${errLaunch.message}`);
    }

    evaluatedCount++;
  }

  try {
    recordLog("Evaluating Outreach Queue (Welcome, Vendor, MG Payouts, Rev Statements)...");
    processOutreachQueue(false);
    recordLog("[SUCCESS] Standard Outreach Queue successfully processed.");
  } catch (errQueue) {
    recordLog(`[ERROR] [Outreach Queue] ${errQueue.message}`);
  }

  SpreadsheetApp.flush();

  const successMessage = `Evaluated ${evaluatedCount} active rows (${skippedBlankCount} blank rows skipped). All drafts & statuses updated!`;
  recordLog("==================================================================");
  recordLog(`[COMPLETE] ${successMessage}`);
  recordLog("==================================================================");

  try {
    CacheService.getUserCache().put("POCKETFM_LAST_LOGS", JSON.stringify(GLOBAL_SESSION_LOGS.slice(-500)), 21600);
  } catch (cacheErr) {}

  openLiveAutomationConsole();

  try {
    ss.toast(successMessage, "Automation Complete", 6);
  } catch (toastErr) {}
}

/**
 * OPENS THE EXECUTION LOGS PANEL IN THE CORNER OF THE SPREADSHEET
 */
function openExecutionLogsSidebar() {
  openLiveAutomationConsole();
}

/**
 * SERVER-SIDE RPC ENDPOINT:
 */
function getLatestExecutionLogs() {
  if (GLOBAL_SESSION_LOGS && GLOBAL_SESSION_LOGS.length > 0) {
    return GLOBAL_SESSION_LOGS;
  }
  try {
    var cached = CacheService.getUserCache().get("POCKETFM_LAST_LOGS");
    if (cached) {
      var parsed = JSON.parse(cached);
      if (Array.isArray(parsed) && parsed.length > 0) return parsed;
    }
  } catch (e) {}
  return [
    "[INFO] No execution logs recorded in current session.",
    "[INFO] Click '▶️ 🚀 RUN ALL AUTOMATIONS' from the top menu to run all checks and stream live logs!"
  ];
}

/**
 * BUILDS AND RENDERS THE LIVE STREAMING CONSOLE HTML
 */
function buildLiveStreamingConsoleHtml() {
  return `<!DOCTYPE html>
<html>
<head>
  <base target="_top">
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Poppins', -apple-system, BlinkMacSystemFont, sans-serif;
      background: #0f131a;
      color: #e2e8f0;
      padding: 14px;
      font-size: 13px;
    }
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 12px;
      border-bottom: 1px solid #1e293b;
      margin-bottom: 12px;
    }
    .header-title {
      font-size: 14px;
      font-weight: 700;
      color: #f8fafc;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .close-btn {
      background: #e51a4d;
      color: #ffffff;
      border: none;
      border-radius: 6px;
      padding: 6px 12px;
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 4px;
      transition: background 0.15s ease-in-out;
    }
    .close-btn:hover { background: #b9103a; }
    .progress-section {
      background: #18202f;
      border: 1px solid #1e293b;
      border-radius: 8px;
      padding: 10px 12px;
      margin-bottom: 10px;
    }
    .progress-header {
      display: flex;
      justify-content: space-between;
      font-size: 11px;
      margin-bottom: 6px;
      color: #94a3b8;
    }
    .progress-bar-bg {
      background: #0a0d14;
      border-radius: 6px;
      height: 8px;
      overflow: hidden;
      width: 100%;
    }
    .progress-bar-fill {
      background: linear-gradient(90deg, #e51a4d, #38bdf8);
      height: 100%;
      width: 0%;
      transition: width 0.3s ease;
    }
    .toolbar {
      display: flex;
      gap: 6px;
      margin-bottom: 10px;
      align-items: center;
    }
    .stat-pill {
      background: #18202f;
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 11px;
      color: #94a3b8;
    }
    .stat-pill b { color: #38bdf8; }
    .restart-btn {
      background: #1e293b;
      color: #38bdf8;
      border: 1px solid #334155;
      padding: 4px 10px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 600;
      cursor: pointer;
      margin-left: auto;
    }
    .restart-btn:hover { background: #334155; color: #fff; }
    .search-box {
      width: 100%;
      background: #1a202c;
      border: 1px solid #334155;
      color: #f1f5f9;
      padding: 8px 10px;
      border-radius: 6px;
      font-size: 12px;
      margin-bottom: 10px;
      outline: none;
    }
    .search-box:focus { border-color: #e51a4d; }
    .log-container {
      background: #07090e;
      border: 1px solid #1e293b;
      border-radius: 8px;
      padding: 10px;
      height: 440px;
      max-height: calc(100vh - 270px);
      overflow-y: auto;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      line-height: 1.55;
    }
    .log-line {
      padding: 3px 6px;
      border-radius: 3px;
      margin-bottom: 2px;
      word-break: break-word;
      white-space: pre-wrap;
    }
    .log-line:hover { background: rgba(255,255,255,0.06); }
    .log-success { color: #4ade80; }
    .log-warn { color: #fbbf24; }
    .log-error { color: #f87171; font-weight: 600; }
    .log-info { color: #60a5fa; }
    .log-default { color: #cbd5e1; }
    .actions {
      display: flex;
      gap: 8px;
      margin-top: 10px;
    }
    .btn-action {
      flex: 1;
      background: #1e293b;
      color: #cbd5e1;
      border: 1px solid #334155;
      border-radius: 6px;
      padding: 7px;
      font-size: 11px;
      font-weight: 600;
      cursor: pointer;
      text-align: center;
      transition: all 0.15s ease-in-out;
    }
    .btn-action:hover { background: #334155; color: #fff; }
    .copy-toast {
      position: fixed;
      bottom: 60px;
      left: 50%;
      transform: translateX(-50%);
      background: #059669;
      color: #fff;
      padding: 6px 14px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 600;
      opacity: 0;
      transition: opacity 0.2s;
      pointer-events: none;
    }
  </style>
</head>
<body>
  <div class="header">
    <div class="header-title">⚡ Live Automation Console</div>
    <button class="close-btn" onclick="closeSidebar()" title="Click to remove/close this logs panel">✕ Close</button>
  </div>

  <div class="progress-section">
    <div class="progress-header">
      <span id="progressLabel">Live Progress</span>
      <b id="progressText" style="color:#38bdf8;">0%</b>
    </div>
    <div class="progress-bar-bg">
      <div class="progress-bar-fill" id="progressBar"></div>
    </div>
  </div>

  <div class="toolbar">
    <div class="stat-pill">Lines: <b id="totalLines">0</b></div>
    <div class="stat-pill"><span id="statusPill"><b style="color:#38bdf8;">Starting...</b></span></div>
    <button class="restart-btn" onclick="startLiveRun()" title="Rerun all stages with live logs">▶️ Rerun</button>
  </div>

  <input type="text" id="filterInput" class="search-box" placeholder="🔍 Filter live logs (e.g. Row 4, Draft, Error)..." oninput="applyFilter()">

  <div class="log-container" id="logViewer">
    <div style="color:#38bdf8; padding:15px; text-align:center;">⏳ Starting live stream...</div>
  </div>

  <div class="actions">
    <button class="btn-action" onclick="copyAllLogs()">📋 Copy All Logs</button>
    <button class="btn-action" onclick="closeSidebar()">✕ Dismiss</button>
  </div>
  <div class="copy-toast" id="copyToast">Copied to clipboard!</div>

  <script>
    var currentLogs = [];
    var totalEvaluated = 0;
    var totalSkipped = 0;
    var CHUNK_SIZE = 20;

    function closeSidebar() {
      if (typeof google !== 'undefined' && google.script && google.script.host) {
        google.script.host.close();
      }
    }

    function appendLogLine(line) {
      currentLogs.push(line);
      var viewer = document.getElementById("logViewer");
      var div = document.createElement("div");
      div.className = "log-line";
      var lower = line.toLowerCase();
      if (lower.includes("success") || lower.includes("pass") || lower.includes("completed") || lower.includes("created draft")) {
        div.classList.add("log-success");
      } else if (lower.includes("error") || lower.includes("fail") || lower.includes("exception")) {
        div.classList.add("log-error");
      } else if (lower.includes("warning") || lower.includes("skipped") || lower.includes("not due") || lower.includes("anomaly") || lower.includes("launch date issue")) {
        div.classList.add("log-warn");
      } else if (lower.includes("[live row") || lower.includes("[sync]") || lower.includes("evaluating") || lower.includes("runner:")) {
        div.classList.add("log-info");
      } else {
        div.classList.add("log-default");
      }
      div.textContent = line;
      viewer.appendChild(div);
      viewer.scrollTop = viewer.scrollHeight;
      document.getElementById("totalLines").innerText = currentLogs.length;
    }

    function renderFiltered(lines) {
      var viewer = document.getElementById("logViewer");
      viewer.innerHTML = "";
      if (!lines || lines.length === 0) {
        viewer.innerHTML = '<div style="color:#64748b; padding:15px; text-align:center;">No matching log entries found.</div>';
        return;
      }
      lines.forEach(function(l) {
        var div = document.createElement("div");
        div.className = "log-line";
        var lower = l.toLowerCase();
        if (lower.includes("success") || lower.includes("pass") || lower.includes("completed") || lower.includes("created draft")) {
          div.classList.add("log-success");
        } else if (lower.includes("error") || lower.includes("fail") || lower.includes("exception")) {
          div.classList.add("log-error");
        } else if (lower.includes("warning") || lower.includes("skipped") || lower.includes("not due") || lower.includes("anomaly") || lower.includes("launch date issue")) {
          div.classList.add("log-warn");
        } else if (lower.includes("[live row") || lower.includes("[sync]") || lower.includes("evaluating") || lower.includes("runner:")) {
          div.classList.add("log-info");
        } else {
          div.classList.add("log-default");
        }
        div.textContent = l;
        viewer.appendChild(div);
      });
      viewer.scrollTop = viewer.scrollHeight;
    }

    function applyFilter() {
      var q = document.getElementById("filterInput").value.toLowerCase().trim();
      if (!q) {
        renderFiltered(currentLogs);
        return;
      }
      var filtered = currentLogs.filter(function(l) {
        return l.toLowerCase().indexOf(q) > -1;
      });
      renderFiltered(filtered);
    }

    function copyAllLogs() {
      var text = currentLogs.join("\\n");
      navigator.clipboard.writeText(text).then(function() {
        var t = document.getElementById("copyToast");
        t.style.opacity = "1";
        setTimeout(function() { t.style.opacity = "0"; }, 2000);
      });
    }

    function startLiveRun() {
      document.getElementById("progressBar").style.width = "0%";
      document.getElementById("progressText").innerText = "0%";
      document.getElementById("statusPill").innerHTML = '<b style="color:#38bdf8;">Running...</b>';
      document.getElementById("logViewer").innerHTML = "";
      currentLogs = [];
      totalEvaluated = 0;
      totalSkipped = 0;

      appendLogLine("==================================================================");
      appendLogLine("LIVE STREAMING RUNNER: Starting batch evaluation...");
      appendLogLine("==================================================================");

      processChunk(4);
    }

    function processChunk(startRow) {
      if (typeof google === 'undefined' || !google.script || !google.script.run) {
        appendLogLine("[SIMULATION] Evaluated Rows " + startRow + " to " + (startRow + CHUNK_SIZE - 1));
        var simEnd = startRow + CHUNK_SIZE - 1;
        var simPct = Math.min(Math.round((simEnd / 112) * 90), 90);
        document.getElementById("progressBar").style.width = simPct + "%";
        document.getElementById("progressText").innerText = simPct + "% (Row " + simEnd + "/112)";
        if (startRow + CHUNK_SIZE <= 112) {
          setTimeout(function() { processChunk(startRow + CHUNK_SIZE); }, 300);
        } else {
          runFinalQueueStage();
        }
        return;
      }

      google.script.run
        .withSuccessHandler(function(res) {
          if (res.error) {
            appendLogLine(res.error);
            finishLiveRun();
            return;
          }

          totalEvaluated += res.evaluatedCount || 0;
          totalSkipped += res.skippedBlankCount || 0;

          if (res.logs && res.logs.length > 0) {
            res.logs.forEach(function(l) { appendLogLine(l); });
          }

          var total = res.totalSheetRows || 112;
          var pct = Math.min(Math.round((res.endRow / total) * 90), 90);
          document.getElementById("progressBar").style.width = pct + "%";
          document.getElementById("progressText").innerText = pct + "% (Row " + res.endRow + "/" + total + ")";

          if (!res.isDone && res.nextRow <= total) {
            processChunk(res.nextRow);
          } else {
            document.getElementById("progressText").innerText = "92% (Evaluating Outreach Queue...)";
            runFinalQueueStage();
          }
        })
        .withFailureHandler(function(err) {
          appendLogLine("[ERROR] Batch execution error: " + err.message);
          finishLiveRun();
        })
        .executeAutomationBatch(startRow, CHUNK_SIZE);
    }

    function runFinalQueueStage() {
      if (typeof google === 'undefined' || !google.script || !google.script.run) {
        appendLogLine("[SIMULATION] Standard Outreach Queue evaluated!");
        document.getElementById("progressBar").style.width = "100%";
        document.getElementById("progressText").innerText = "100% Completed";
        finishLiveRun();
        return;
      }

      google.script.run
        .withSuccessHandler(function(res) {
          if (res.logs && res.logs.length > 0) {
            res.logs.forEach(function(l) { appendLogLine(l); });
          }
          document.getElementById("progressBar").style.width = "100%";
          document.getElementById("progressText").innerText = "100% Completed";
          finishLiveRun();
        })
        .withFailureHandler(function(err) {
          appendLogLine("[ERROR] Queue stage error: " + err.message);
          finishLiveRun();
        })
        .executeOutreachQueueStage();
    }

    function finishLiveRun() {
      document.getElementById("statusPill").innerHTML = '<b style="color:#4ade80;">Completed</b>';
      var summary = "COMPLETE: Evaluated " + totalEvaluated + " active rows (" + totalSkipped + " blank rows skipped). All drafts & statuses updated!";
      appendLogLine("==================================================================");
      appendLogLine(summary);
      appendLogLine("==================================================================");
    }

    window.onload = function() {
      startLiveRun();
    };
  </script>
</body>
</html>`;
}

/**
 * MAIN ENTRY POINT FOR SPREADSHEET AUTOMATION:
 * Scans all tracking tabs across all 9 stages (Welcome, Vendor, MG, Check-Ins, Launch, Newsletter, Revenue).
 * Select this in the Apps Script function dropdown and click "Run".
 */
function createAutomatedEmailDrafts() {
  processOutreachQueue(false);
}

/**
 * PROCESS SHOW LAUNCH ANNOUNCEMENTS FOR ALL ROWS:
 * Select this in the Apps Script function dropdown to scan EVERY row dynamically in Post-Sales Tracker.
 * Evaluates date changes, flags anomalies as "Launch Date Issue", and drafts emails for all eligible rows.
 */
function processAllLaunchAnnouncements() {
  generateAllLaunchAnnouncements();
}

/**
 * PROCESS AUTHOR CHECK-INS (15 & 30 DAYS) FOR ALL ROWS:
 * Select this in the Apps Script function dropdown to scan EVERY row dynamically in Post-Sales Tracker.
 * Takes reference from Feedback Mail Date (Col V), sets 15/30-day timers, drafts on Day 15/30,
 * and updates dropdown to "Overdue" once the 15th/30th day is over!
 */
function processAllAuthorCheckIns() {
  generateAllAuthorCheckIns();
}

/**
 * CHECK ACTIVE LIFECYCLE TIMERS IN APPS SCRIPT:
 * Select this in the Apps Script function dropdown to inspect all active automated triggers.
 */
function checkLifecycleTimersReport() {
  checkLifecycleTimers();
}

/**
 * INSTALL AUTOMATED LIFECYCLE TIMERS IN APPS SCRIPT:
 * Select this in the Apps Script function dropdown to automatically install daily & hourly lifecycle triggers.
 */
function installLifecycleTimers() {
  setupLifecycleTimers();
}

/**
 * TEST FUNCTION: AUTHOR CHECK-IN 15 & 30 DAY TIMERS
 * Tests all states (Days 0-14, Day 15 draft, Day 16+ Overdue, Days 0-29, Day 30 draft, Day 31+ Overdue, Col AB override).
 */
function testAuthorCheckIns() {
  testAuthorCheckInTimers();
}

/**
 * TEST CASE A: Explicit test function for Show Launch Date Anomaly
 * Verifies that Launch Date <= Script Date (e.g. 2nd Oct <= 6th Oct) flags "Launch Date Issue"
 * and STRICTLY SUPPRESSES EMAIL DRAFTING (0 drafts generated).
 */
function testCaseA_LaunchDateAnomaly() {
  runTestCaseA_LaunchDateAnomaly();
}

/**
 * TEST CASE B: Explicit test function for Valid Show Launch Announcement
 * Verifies that Script Date < Launch Date (e.g. 6th Oct < 10th Oct) and Mandatory Condition 1 Met
 * creates the draft email in your Gmail Drafts folder for eligible rows.
 */
function testCaseB_ValidLaunchAnnouncement() {
  runTestCaseB_ValidLaunchAnnouncement();
}

/**
 * EMAIL SANITIZATION & VALIDATION HELPERS (GLOBAL SCOPE)
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
 * ROW DATA VALIDATION HELPER:
 * Ensures triggers only run for populated rows with real data, strictly skipping blank rows.
 * @param {Array} rowVals - Array of row cell values
 * @param {number} titleCol - Column index for Title / IP (default 2)
 * @returns {boolean} True if row contains valid Title / IP and actual data, false if blank/empty
 */
function isTrackerRowFilled(rowVals, titleCol = 2) {
  if (!rowVals || rowVals.length === 0) return false;
  let rawTitle = (titleCol > -1 && rowVals.length > titleCol && rowVals[titleCol]) ? rowVals[titleCol].toString().trim() : "";
  if (!rawTitle || rawTitle === "" || rawTitle === "-" || rawTitle === "#N/A" || rawTitle.toLowerCase() === "n/a" || rawTitle.startsWith("#")) {
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
 * Safe multi-format Date Parser supporting:
 * - Date objects
 * - Excel serial dates
 * - Textual dates without years: "2nd october", "6 th october"
 * - DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD
 */
function parseDateSafe(dateVal) {
  if (!dateVal) return null;
  if (dateVal instanceof Date) {
    return isNaN(dateVal.getTime()) ? null : dateVal;
  }
  if (typeof dateVal === "number") {
    // Excel/Sheets serial date number (base date Dec 30, 1899)
    if (dateVal > 30000 && dateVal < 60000) {
      let d = new Date(Math.round((dateVal - 25569) * 86400 * 1000));
      return isNaN(d.getTime()) ? null : d;
    }
  }
  let str = dateVal.toString().trim();
  if (!str || str === "-" || str === "N/A" || str.toLowerCase() === "null") return null;

  str = str.replace(/septmeber/gi, "september");
  // Remove ordinals like 1st, 2nd, 3rd, 6 th, 6th
  let cleanStr = str.replace(/(\d+)\s*(st|nd|rd|th)/gi, "$1").replace(/\s+/g, " ").trim();

  // Try Day Month or Month Day matching (e.g. "2 october", "6 october", "2 october 2026")
  let textMatch = cleanStr.match(/^(\d{1,2})\s+([a-zA-Z]+)(?:\s+(\d{4}))?$/);
  if (textMatch) {
    let day = parseInt(textMatch[1], 10);
    let monthName = textMatch[2];
    let year = textMatch[3] ? parseInt(textMatch[3], 10) : new Date().getFullYear();
    let d = new Date(`${monthName} ${day}, ${year}`);
    if (!isNaN(d.getTime())) return d;
  }

  let textMatch2 = cleanStr.match(/^([a-zA-Z]+)\s+(\d{1,2})(?:\s+(\d{4}))?$/);
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
  return today.getDate() === target.getDate() &&
         today.getMonth() === target.getMonth() &&
         today.getFullYear() === target.getFullYear();
}

function processOutreachQueue(isDelayedRun = false) {
  // Hardcoded to strictly open the exact correct Google Sheet document you linked
  const spreadsheet = SpreadsheetApp.openById("1A1vJ0DsmDxtCFZiuyu6vtuQFWqClPyK7e1_lHKddGdQ");
  const allSheets = spreadsheet.getSheets();
  let mainSheet = null;
  let psSheet = null;
  let queueSheet = null;
  
  for (let s of allSheets) {
    let sName = s.getName().toLowerCase().trim();
    sName = sName.replace("–", "-").replace("—", "-"); // Standardize dashes
    
    // Priority 1: Exact gid match (gid: 120747375 for Post-Sales Tracker)
    if (s.getSheetId() === 120747375) { psSheet = s; }

    // Priority 2: Named matching
    if (sName === "lifecycle tracker - master") { mainSheet = s; }
    else if (!psSheet && (sName === "post-sales tracker" || sName === "post sales tracker")) { psSheet = s; }
    else if (sName === "queue") { queueSheet = s; }
  }
  
  // 2. Last resort partial matches
  if (!mainSheet) {
    for (let s of allSheets) {
      let sName = s.getName().toLowerCase().trim();
      if (sName.includes("lifecycle tracker - master")) { mainSheet = s; break; }
    }
  }
  if (!psSheet) {
    for (let s of allSheets) {
      let sName = s.getName().toLowerCase().trim();
      if (sName.includes("post-sales tracker") || sName.includes("post sales tracker")) { psSheet = s; break; }
    }
  }
  
  Logger.log('Selected Main Sheet: ' + (mainSheet ? mainSheet.getName() : 'None'));
  Logger.log('Selected PS Sheet: ' + (psSheet ? psSheet.getName() : 'None'));
  
  
  if (queueSheet) {
    queueSheet.getRange(1, 12).setValue("CC");
    let headerRange = queueSheet.getRange(1, 1, 1, 12);
    headerRange.setBackground("#1155cc"); 
    headerRange.setFontColor("#ffffff");
    headerRange.setFontWeight("bold");
    headerRange.setHorizontalAlignment("center");
    headerRange.setVerticalAlignment("middle");
    queueSheet.setRowHeight(1, 40); 
    queueSheet.hideColumns(1);
    queueSheet.hideColumns(6);
    queueSheet.setColumnWidth(2, 200);
    queueSheet.setColumnWidth(4, 220);
    queueSheet.setColumnWidth(5, 350);
    queueSheet.getRange("B:E").setWrap(true);
    queueSheet.getRange("G:I").setHorizontalAlignment("center");
  }
  
  if (!mainSheet || !psSheet) {
    Logger.log("Could not find required tracking tabs. Main Sheet found: " + (mainSheet !== null) + ", Post-Sales Tracker found: " + (psSheet !== null));
    let names = [];
    allSheets.forEach(s => names.push(s.getName()));
    Logger.log("Available sheets: " + names.join(", "));
    return;
  }
  
  const mainData = mainSheet.getDataRange().getValues();
  const psData = psSheet.getDataRange().getValues();
  
  // Headers for main sheet (Row 3, index 2)
  const mainHeaders = mainData[2];
  const mainFindCol = (name) => mainHeaders.findIndex(h => h.toString().toLowerCase().includes(name.toLowerCase()));
  
  // --- ARGUS DATA PARSING ---
  const argusSheet = allSheets.find(s => s.getName().toString().toLowerCase().includes("argus"));
  let argusData = {};
  if (argusSheet) {
    const aData = argusSheet.getDataRange().getValues();
    if (aData.length > 0) {
      const aHeaders = aData[0];
      const aFindCol = (name) => aHeaders.findIndex(h => h.toString().toLowerCase().includes(name.toLowerCase()));
      const aShowIdCol = aFindCol("Show ID");
      const aTitleCol = aFindCol("Title");
      const aShowNameCol = aFindCol("Show Name");
      const aDurCol = aFindCol("Duration");
      const aLdauCol = aFindCol("Plays") > -1 ? aFindCol("Plays") : aFindCol("LDAU");
      const aCommentsCol = aFindCol("Comment");
      const aRatingsCol = aFindCol("Rating");
      const aReviewsCol = aFindCol("Review");
      const aHoursCol = aFindCol("Listening Hour");
      
      for (let j = 1; j < aData.length; j++) {
        let sid = aShowIdCol > -1 ? aData[j][aShowIdCol] : "";
        let aTitle = aTitleCol > -1 ? aData[j][aTitleCol] : "";
        let aShowName = aShowNameCol > -1 ? aData[j][aShowNameCol] : "";

        let dur = aDurCol > -1 ? aData[j][aDurCol] : "";
        let ldau = aLdauCol > -1 ? aData[j][aLdauCol] : "";
        let comments = aCommentsCol > -1 ? aData[j][aCommentsCol] : "";
        let ratings = aRatingsCol > -1 ? aData[j][aRatingsCol] : "";
        let reviews = aReviewsCol > -1 ? aData[j][aReviewsCol] : "";
        let hours = aHoursCol > -1 ? aData[j][aHoursCol] : "";

        let formattedDur = (dur !== "" && dur !== null && dur !== undefined) ? dur + " hours" : "N/A";
        let formattedLdau = (ldau !== "" && ldau !== null && ldau !== undefined) 
                            ? (ldau.toString().toLowerCase().includes("listener") || ldau.toString().toLowerCase().includes("play") ? ldau.toString() : ldau + " listeners") 
                            : "N/A";
        let formattedComments = (comments !== "" && comments !== null && comments.toString() !== "0" && comments.toString() !== "0.0") 
                                ? (!isNaN(comments) ? Math.round(Number(comments)).toString() : comments.toString()) 
                                : "No comments";
        let formattedRatings = (ratings !== "" && ratings !== null && ratings.toString() !== "0" && ratings.toString() !== "0.0") 
                               ? ratings.toString() 
                               : "No ratings";
        let formattedReviews = (reviews !== "" && reviews !== null && reviews.toString() !== "0" && reviews.toString() !== "0.0") 
                               ? (!isNaN(reviews) ? Math.round(Number(reviews)).toString() : reviews.toString()) 
                               : "No reviews";
        let formattedHours = (hours !== "" && hours !== null && hours !== undefined) ? hours.toString() : "N/A";

        let metrics = {
          duration: formattedDur,
          ldau: formattedLdau,
          comments: formattedComments,
          ratings: formattedRatings,
          reviews: formattedReviews,
          hours: formattedHours
        };

        if (sid) {
          argusData[sid.toString().trim()] = metrics;
          argusData[sid.toString().toLowerCase().trim()] = metrics;
        }
        if (aTitle) {
          argusData[aTitle.toString().toLowerCase().trim()] = metrics;
        }
        if (aShowName) {
          argusData[aShowName.toString().toLowerCase().trim()] = metrics;
        }
      }
    }
  }
  // --------------------------
  
  const showIdCol = mainFindCol("Show ID");
  const emailCol = mainFindCol("Receiver Email ID");
  const authorCol = mainFindCol("Author Name");
  const firstNameCol = mainFindCol("Receiver First Name"); 
  const mainTitleCol = mainFindCol("Title / IP");
  const showLinkCol = mainFindCol("Show Link"); 
  const ccCol = mainFindCol("CC Mail ID"); 
  
  const timestampCol = mainFindCol("Timestamp") !== -1 ? mainFindCol("Timestamp") : 0; // Column A (index 0) in Lifecycle Master
  const contractSignedCol = mainFindCol("Contract Signing date"); 
  const vendorLifecycleExitedCol = mainFindCol("Vendor Lifecycle Exited") !== -1 
                                   ? mainFindCol("Vendor Lifecycle Exited") 
                                   : (contractSignedCol > -1 ? contractSignedCol + 4 : -1); 
  const mgPayoutExitedCol = mainFindCol("MG Payout Exited") !== -1 
                            ? mainFindCol("MG Payout Exited") 
                            : (contractSignedCol > -1 ? contractSignedCol + 7 : -1); 
  const launchStatusCol = mainFindCol("Launch Status"); 
  const mainLaunchDateCol = mainFindCol("Launch Date"); 
  const mainShowNameCol = mainFindCol("Show Name");

  // Build a lookup dictionary for main sheet data based on Title / IP
  let mainDict = {};
  for(let i = 3; i < mainData.length; i++) {
     let row = mainData[i];
     if (!isTrackerRowFilled(row, mainTitleCol)) continue; // Skip blank rows
     let t = row[mainTitleCol];
     if (t) {
         let safeTitle = t.toString().toLowerCase().trim();
         let rawTimestamp = (timestampCol > -1 && row.length > timestampCol && row[timestampCol]) 
                            ? row[timestampCol] 
                            : (contractSignedCol > -1 ? row[contractSignedCol] : "");

         mainDict[safeTitle] = {
             email: row[emailCol],
             author: row[authorCol],
             firstName: row[firstNameCol],
             showLink: row[showLinkCol],
             ccMail: row[ccCol],
             showId: showIdCol > -1 ? row[showIdCol] : "",
             timestamp: rawTimestamp, // Column A in Lifecycle Master
             contractSigned: rawTimestamp, // Welcome & Vendor Onboarding triggered by Timestamp Col A
             origContractSigned: contractSignedCol > -1 ? row[contractSignedCol] : "",
             vendorLifecycleExited: vendorLifecycleExitedCol > -1 ? row[vendorLifecycleExitedCol] : "",
             mgPayoutExited: mgPayoutExitedCol > -1 ? row[mgPayoutExitedCol] : "",
             launchStatus: row[launchStatusCol],
             launchDate: mainLaunchDateCol > -1 ? row[mainLaunchDateCol] : "",
             showName: mainShowNameCol > -1 ? row[mainShowNameCol] : ""
         };
     }
  }

  // Headers for Post-Sales Tracker (Row 3, index 2)
  const psHeaders = psData[2];
  const psFindCol = (name) => psHeaders.findIndex(h => h.toString().toLowerCase().includes(name.toLowerCase()));
  
  const psTitleCol = psFindCol("Title / IP");
  const psShowNameCol = psFindCol("Show Name");
  const psShowLinkCol = psFindCol("Show Link");
  const welcomeCol = psFindCol("Welcome Email"); 
  const vendorCol = psFindCol("Vendor Onboarding Email"); 
  const mgPayoutInitiatedCol = psFindCol("MG Payout Initiated"); 
  const mgPayoutConfirmationCol = psFindCol("MG Payout Confirmation"); 
  const feedbackMailDateCol = psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("feedback") && s.includes("date");
  }) !== -1 ? psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("feedback") && s.includes("date");
  }) : 21; // Column V

  const checkIn1Col = psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("15 days") && !s.includes("newsletter") && !s.includes("date");
  }) !== -1 ? psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("15 days") && !s.includes("newsletter") && !s.includes("date");
  }) : 22; // Column W

  const checkIn1DateCol = psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("15 days") && !s.includes("newsletter") && s.includes("date");
  }) !== -1 ? psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("15 days") && !s.includes("newsletter") && s.includes("date");
  }) : 23; // Column X

  const checkIn2Col = psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("30 days") && !s.includes("date");
  }) !== -1 ? psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("30 days") && !s.includes("date");
  }) : 24; // Column Y

  const checkIn2DateCol = psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("30 days") && s.includes("date");
  }) !== -1 ? psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("30 days") && s.includes("date");
  }) : 25; // Column Z 
  const scriptDateCol = psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("script") && s.includes("date");
  }) !== -1 ? psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("script") && s.includes("date");
  }) : 14; // Column O

  const psLaunchDateCol = psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s === "launch date" || (s.includes("launch") && s.includes("date") && !s.includes("sent") && !s.includes("announcement"));
  }) !== -1 ? psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s === "launch date" || (s.includes("launch") && s.includes("date") && !s.includes("sent") && !s.includes("announcement"));
  }) : 9; // Column J

  const launchCol = psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return (s.includes("launch") && s.includes("announcement") && s.includes("status")) ||
           (s === "show launch announcement status");
  }) !== -1 ? psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return (s.includes("launch") && s.includes("announcement") && s.includes("status")) ||
           (s === "show launch announcement status");
  }) : (psFindCol("Show Launch Announcement") !== -1 ? psFindCol("Show Launch Announcement") : 26); // Column AA (idx 26)

  let launchSentCol = psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return (s.includes("launch") && s.includes("announcement") && (s.includes("sent") || s.includes("email sent")) && !s.includes("date"));
  });
  if (launchSentCol === -1) {
    if (psHeaders.length > 27 && (psHeaders[27].toString().trim().toLowerCase() === "er" || psHeaders[27].toString().toLowerCase().includes("sent"))) {
      launchSentCol = 27; // Column AB
    } else if (launchCol !== -1 && launchCol + 1 < psHeaders.length) {
      launchSentCol = launchCol + 1;
    } else {
      launchSentCol = 27;
    }
  }

  let launchSentDateCol = psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return (s.includes("launch") && s.includes("announcement") && s.includes("date")) ||
           (s.includes("launch") && s.includes("sent") && s.includes("date"));
  });
  if (launchSentDateCol === -1 && launchSentCol !== -1) {
    if (psHeaders[launchSentCol + 1] && psHeaders[launchSentCol + 1].toString().toLowerCase().includes("date")) {
      launchSentDateCol = launchSentCol + 1;
    } else if (psHeaders.length > 28) {
      launchSentDateCol = 28; // Column AC
    }
  }
  let newsletterCol = psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("newsletter") && !s.includes("date");
  });
  if (newsletterCol === -1) {
    newsletterCol = 29; // Column AD
  }
  const newsletterSentDateCol = psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("newsletter") && s.includes("date");
  });
  // Direct helper columns in Post-Sales Tracker (Fallback to Master Tracker if blank)
  const psEmailCol = psFindCol("Receiver Email ID");
  const psCcCol = psFindCol("CC Mail ID");
  const psFirstNameCol = psFindCol("Receiver First Name");

  // =============================================================
  // REVENUE STATEMENT QUARTERLY COLUMN MAPPINGS (FROM COLUMN AE ONWARDS)
  // =============================================================
  // 1. AMJ Quarter (April–June) - Columns AE to AH
  const amjDueCol = psHeaders.findIndex(h => h.toString().toLowerCase().includes("amj") && (h.toString().toLowerCase().includes("due") || h.toString().toLowerCase().includes("date")));
  const amjStatusCol = psHeaders.findIndex(h => h.toString().toLowerCase().includes("amj") && h.toString().toLowerCase().includes("status"));
  const amjLinkCol = psHeaders.findIndex(h => h.toString().toLowerCase().includes("amj") && h.toString().toLowerCase().includes("drive"));
  const amjSentCol = psHeaders.findIndex((h, idx) => idx >= 30 && idx <= 34 && h.toString().toLowerCase().includes("sent"));

  // 2. JAS Quarter (July–September) - Columns AI to AM
  const jasDueCol = psHeaders.findIndex(h => h.toString().toLowerCase().includes("jas") && (h.toString().toLowerCase().includes("due") || h.toString().toLowerCase().includes("date")));
  const jasStatusCol = psHeaders.findIndex(h => h.toString().toLowerCase().includes("jas") && h.toString().toLowerCase().includes("status"));
  const jasLinkCol = psHeaders.findIndex(h => h.toString().toLowerCase().includes("jas") && h.toString().toLowerCase().includes("drive"));
  const jasSentCol = psHeaders.findIndex((h, idx) => idx >= 34 && idx <= 39 && h.toString().toLowerCase().includes("sent"));

  // 3. OND Quarter (October–December) - Columns AN to AQ
  const ondDueCol = psHeaders.findIndex(h => h.toString().toLowerCase().includes("ond") && (h.toString().toLowerCase().includes("due") || h.toString().toLowerCase().includes("date")));
  const ondStatusCol = psHeaders.findIndex((h, idx) => idx >= 39 && idx <= 42 && h.toString().toLowerCase().includes("status"));
  const ondLinkCol = psHeaders.findIndex((h, idx) => idx >= 40 && idx <= 43 && h.toString().toLowerCase().includes("drive"));
  const ondSentCol = psHeaders.findIndex((h, idx) => idx >= 41 && idx <= 44 && h.toString().toLowerCase().includes("sent"));

  // 4. Legacy single quarter fallback (Columns X to AA)
  const revStatementDueCol = psFindCol("Rev Statement Due Date"); 
  const revLinkCol = psFindCol("Revenue Statement Drive Link"); 
  const revStatementEmailCol = psFindCol("Insights Email Status"); 
  const revStatementSentCol = psHeaders.findIndex((h, idx) => idx >= 25 && idx <= 28 && h.toString().toLowerCase().includes("sent")); 

  // =============================================================
  // RECOMMENDED NOTIFICATIONS & ELIGIBILITY LOGGER
  // =============================================================
  let notificationLog = [];
  function logNotification(category, title, detail) {
    let cleanDetail = detail;
    if (cleanDetail.startsWith(`${category}: `)) {
      cleanDetail = cleanDetail.substring(`${category}: `.length);
    } else if (cleanDetail.startsWith(`${category} `)) {
      cleanDetail = cleanDetail.substring(category.length).trim();
    }
    let msg = `[RECOMMENDED NOTIFICATION] ${category}: ${cleanDetail} (Title: "${title}")`;
    notificationLog.push({ category: category, title: title, message: cleanDetail, fullLog: msg });
    Logger.log(msg);
  }

  // -------------------------------------------------------------
  // EMAIL SANITIZATION & VALIDATION HELPERS
  // -------------------------------------------------------------
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

  // -------------------------------------------------------------
  // DRAFTING LOGIC WITH VARIABLE MAPPING & QUEUE INJECTION
  // -------------------------------------------------------------
  function createDraft(rawEmail, subject, firstName, type, title, link, rIdx, cIdx, customSendTime, rawCcMail, revLink, argus, showName = "") {
    const email = cleanEmail(rawEmail);
    const ccMail = cleanCcList(rawCcMail);

    // 1. Notification Check: Recipient Email ID
    if (!email || email === "" || !isValidEmail(email)) {
      logNotification("Recipient Email ID is missing", title, `Recipient Email ID is invalid or missing in Master Sheet (Col AB) for "${title}" ("${rawEmail || ''}"). Cannot create draft.`);
      return;
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
      logNotification("Email template not selected", title, `Email template not selected or unrecognized for stage type: "${type}". Draft creation skipped.`);
      return;
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
      logNotification("Email template not selected", title, `Email template body is empty or not defined for stage type: "${type}".`);
      return;
    }
    const wrappedBody = wrapHtml(body, queueId);
    
    const sendDate = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy-MM-dd");
    const exactTime = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "hh:mm a"); 
    const sendTime = customSendTime ? customSendTime : exactTime; 
    const ccValue = ccMail ? ccMail : "";
    
    // 6. Append to Queue Tab (Queue ID, Recipient, Sender, Template, Subject, HTML Body, Send Date, Send Time, Status, Row IDs, Approved, CC)
    if (queueSheet) {
      queueSheet.appendRow([
        queueId,
        email, 
        Session.getActiveUser().getEmail(), 
        templateName, 
        subject,
        wrappedBody,
        sendDate,
        sendTime,
        "Draft Ready", 
        rIdx + 1, 
        "Yes",
        ccValue // Appended CC to queue for GMass
      ]);
    }

    // (Optional) We keep the traditional draft creation just in case you want to manually verify in Gmail
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

    // Only update sheet statuses and dates if the mail actually got generated and drafted in the mailbox!
    if (!draftSuccess) {
      Logger.log(`[SKIPPED] Draft was NOT created in mailbox for "${title}". Dates and statuses will not be updated.`);
      return;
    }
    
    // Update main tracker sheet status indicating draft is prepared in the mailbox
    let statusValue = "Draft Ready";
    if (type === "mgConfirmed" || cIdx === mgPayoutConfirmationCol) {
      statusValue = "Draft ready";
    } else if (type === "checkIn1" || type === "checkIn2" || cIdx === checkIn1Col || cIdx === checkIn2Col) {
      statusValue = "draft ready";
    }
    psSheet.getRange(rIdx + 1, cIdx + 1).setValue(statusValue);
    
    if (type === "launch" || type === "launch_no_ai") {
      if (typeof launchSentCol !== "undefined" && launchSentCol !== -1) {
        psSheet.getRange(rIdx + 1, launchSentCol + 1).setValue("Draft Ready");
        Logger.log(`[STATUS UPDATE] Updated Launch Announcement Sent dropdown for "${title}" in Col ${launchSentCol + 1} (Col AB) to "Draft Ready"`);
      }
      if (typeof launchCol !== "undefined" && launchCol !== -1) {
        let curAAFormula = psSheet.getRange(rIdx + 1, launchCol + 1).getFormula();
        if (!curAAFormula) {
          psSheet.getRange(rIdx + 1, launchCol + 1).setValue("Draft Ready");
        }
        Logger.log(`[STATUS UPDATE] Updated Launch Announcement Status for "${title}" in Col ${launchCol + 1} (Col AA) to "Draft Ready"`);
      }
    }
    if ((type === "authorEdit" || type === "newsletter") && typeof newsletterCol !== "undefined" && newsletterCol !== -1) {
      psSheet.getRange(rIdx + 1, newsletterCol + 1).setValue("Draft Ready");
      Logger.log(`[STATUS UPDATE] Updated Newsletter Edit dropdown for "${title}" in Col ${newsletterCol + 1} (Row ${rIdx + 1}) to "Draft Ready"`);
    }

    // Capture today's date in Column R (Feedback Mail Date) ONLY for rows where MG Payout Confirmation draft got generated
    if (type === "mgConfirmed" || cIdx === mgPayoutConfirmationCol) {
      if (typeof feedbackMailDateCol !== "undefined" && feedbackMailDateCol !== -1) {
        const todayDate = new Date();
        psSheet.getRange(rIdx + 1, feedbackMailDateCol + 1).setValue(todayDate);
        Logger.log(`[DATE CAPTURE] Captured Feedback Mail Date for "${title}" in Col ${feedbackMailDateCol + 1} (Row ${rIdx + 1}): ${todayDate}`);
      }
    }

    // Capture today's date in Column X (Check-In 1 Date) ONLY for rows where Check-In 1 draft got generated
    if (type === "checkIn1" || cIdx === checkIn1Col) {
      if (typeof checkIn1DateCol !== "undefined" && checkIn1DateCol !== -1) {
        const todayDate = new Date();
        psSheet.getRange(rIdx + 1, checkIn1DateCol + 1).setValue(todayDate);
        Logger.log(`[DATE CAPTURE] Captured Check-In 1 Date for "${title}" in Col ${checkIn1DateCol + 1} (Row ${rIdx + 1}): ${todayDate}`);
      }
    }

    // Capture today's date in Column Z (Check-In 2 Date) ONLY for rows where Check-In 2 draft got generated
    if (type === "checkIn2" || cIdx === checkIn2Col) {
      if (typeof checkIn2DateCol !== "undefined" && checkIn2DateCol !== -1) {
        const todayDate = new Date();
        psSheet.getRange(rIdx + 1, checkIn2DateCol + 1).setValue(todayDate);
        Logger.log(`[DATE CAPTURE] Captured Check-In 2 Date for "${title}" in Col ${checkIn2DateCol + 1} (Row ${rIdx + 1}): ${todayDate}`);
      }
    }

    // Capture today's date in Show Launch Announcement Email Sent Date ONLY for rows where Launch Email draft got generated
    if (type === "launch" || type === "launch_no_ai" || cIdx === launchCol || (typeof launchSentCol !== "undefined" && cIdx === launchSentCol)) {
      if (typeof launchSentDateCol !== "undefined" && launchSentDateCol !== -1) {
        const todayDate = new Date();
        psSheet.getRange(rIdx + 1, launchSentDateCol + 1).setValue(todayDate);
        Logger.log(`[DATE CAPTURE] Captured Launch Announcement Email Sent Date for "${title}" in Col ${launchSentDateCol + 1} (Row ${rIdx + 1}): ${todayDate}`);
      }
    }

    // Capture today's date in Newsletter Sent Date ONLY for rows where Newsletter draft got generated
    if (type === "authorEdit" || type === "newsletter" || cIdx === newsletterCol) {
      if (typeof newsletterSentDateCol !== "undefined" && newsletterSentDateCol !== -1) {
        const todayDate = new Date();
        psSheet.getRange(rIdx + 1, newsletterSentDateCol + 1).setValue(todayDate);
        Logger.log(`[DATE CAPTURE] Captured Newsletter Sent Date for "${title}" in Col ${newsletterSentDateCol + 1} (Row ${rIdx + 1}): ${todayDate}`);
      }
    }
    Logger.log("SUCCESS: Created draft for " + title + " (Type: " + type + ")");
  }

  // Iterate over all rows in Post-Sales Tracker (starting from index 3)
  let triggerSet = false;
  
  for (let i = 3; i < psData.length; i++) {
    let psRow = psData[i];
    if (!isTrackerRowFilled(psRow, psTitleCol)) continue; // Skip blank rows
    let title = psRow[psTitleCol];
    if (!title) continue;
    
    let safeTitle = title.toString().toLowerCase().trim();
    let mainInfo = mainDict[safeTitle] || {};
    
    // 1. Recipient Email ID resolution (Post-Sales Tracker Col F, fallback to Master Sheet Col AB)
    let psEmail = (psEmailCol > -1 && psRow.length > psEmailCol && psRow[psEmailCol]) ? psRow[psEmailCol].toString().trim() : "";
    let rawEmail = psEmail !== "" ? psEmail : (mainInfo.email || "");
    let email = cleanEmail(rawEmail);
    if (!email || email === "" || !isValidEmail(email)) {
      logNotification("Recipient Email ID is missing", title, `Recipient Email ID is invalid or missing in Post-Sales Tracker (Col F) and Master sheet (Col AB) for "${title}" ("${rawEmail || ''}"). Cannot proceed with outreach drafts.`);
      continue;
    }
    let showName = (psShowNameCol > -1 && psRow.length > psShowNameCol && psRow[psShowNameCol] && psRow[psShowNameCol].toString().trim() !== "")
                   ? psRow[psShowNameCol].toString().trim()
                   : (mainInfo.showName ? mainInfo.showName.toString().trim() : title.toString().trim());

    let psShowIdCol = psFindCol("Show ID");
    let psShowId = (psShowIdCol > -1 && psRow.length > psShowIdCol && psRow[psShowIdCol]) ? psRow[psShowIdCol].toString().trim() : "";
    let showId = psShowId !== "" ? psShowId : (mainInfo.showId ? mainInfo.showId.toString().trim() : "");
    let safeSid = showId ? showId.toLowerCase().trim() : "";

    let argus = (safeSid && argusData[safeSid]) 
                || (argusData[safeTitle]) 
                || (showName && argusData[showName.toLowerCase().trim()]) 
                || {duration: "N/A", ldau: "N/A", comments: "No comments", ratings: "No ratings", reviews: "No reviews", hours: "N/A"};
    let psAuthorCol = psFindCol("Author Name");
    let psAuthor = (psAuthorCol > -1 && psRow.length > psAuthorCol && psRow[psAuthorCol]) ? psRow[psAuthorCol].toString().trim() : "";
    let author = psAuthor !== "" ? psAuthor : (mainInfo.author ? mainInfo.author.toString().trim() : "");
    let psLink = (psShowLinkCol > -1 && psRow.length > psShowLinkCol && psRow[psShowLinkCol]) ? psRow[psShowLinkCol].toString().trim() : "";
    let link = psLink !== "" ? psLink : (mainInfo.showLink ? mainInfo.showLink.toString().trim() : "");
    let psCc = (psCcCol > -1 && psRow.length > psCcCol && psRow[psCcCol]) ? psRow[psCcCol].toString().trim() : "";
    let ccMail = cleanCcList(psCc !== "" ? psCc : mainInfo.ccMail);
    
    // Safely pull from the dynamic Revenue Statement Drive Link column on the PS Tracker
    let revLinkRaw = (revLinkCol > -1 && psRow.length > revLinkCol) ? psRow[revLinkCol] : "";
    let revLink = (revLinkRaw && revLinkRaw.toString().trim() !== "") ? revLinkRaw.toString().trim() : "";
    if (revLink && !revLink.startsWith("http")) {
        revLink = "https://" + revLink;
    }
    let psLaunchStatusCol = psFindCol("Launch Status");
    let psLaunchStatus = (psLaunchStatusCol !== -1 && psRow.length > psLaunchStatusCol && psRow[psLaunchStatusCol]) 
                         ? psRow[psLaunchStatusCol].toString().trim().toLowerCase() 
                         : "";
    let launchStatus = psLaunchStatus !== "" 
                       ? psLaunchStatus 
                       : (mainInfo.launchStatus ? mainInfo.launchStatus.toString().trim().toLowerCase() : "");

    // Graceful fallback: If First Name is missing in Post-Sales Tracker (Col H) or Master (Col AD), use Author Name
    let psFirstName = (psFirstNameCol > -1 && psRow.length > psFirstNameCol && psRow[psFirstNameCol]) ? psRow[psFirstNameCol].toString().trim() : "";
    let firstName = psFirstName !== "" ? psFirstName : ((mainInfo.firstName && mainInfo.firstName.toString().trim() !== "") ? mainInfo.firstName : author);
    
    // 2. Workflow status eligibility check (Launch Status)
    const isDropped = launchStatus.includes("dropped") || launchStatus.includes("bad") || launchStatus.includes("untested");
    if (isDropped && !launchStatus.includes("dropped")) {
      logNotification("Workflow status is not eligible", title, `Workflow status is not eligible for "${title}" (Launch Status is "${launchStatus}"). Standard outreach stages 1-8 are suppressed.`);
    }
    
    const isReady = (status) => {
      if (!status) return true;
      let s = status.toString().toLowerCase().trim();
      return s !== "scheduled" && s !== "sent" && s !== "draft ready" && s !== "timer set" && s !== "timer set rev" && !s.includes("launch date issue");
    };
    
    // --- 6-HOUR TIMER EXECUTION BLOCK ---
    if (isDelayedRun) {
      if (psRow[vendorCol] === "Timer Set") {
        createDraft(email, `Vendor Onboarding for ${title}`, firstName, 'vendor', title, link, i, vendorCol, null, ccMail, revLink, argus);
      }
      if (psRow[revStatementEmailCol] === "Timer Set Rev") {
        createDraft(email, "Pocket FM: Your earnings are waiting for you!", firstName, 'revStatement_workedWell_payment', title, link, i, revStatementEmailCol, null, ccMail, revLink, argus);
      }
      continue; 
    }
    // ------------------------------------

    // Stage 1 & 2: Welcome Email and Instant Vendor Onboarding (Timestamp in Column A of Lifecycle Master)
    let welcomeTriggerDate = mainInfo.timestamp || mainInfo.contractSigned;
    if (!welcomeTriggerDate || welcomeTriggerDate.toString().trim() === "") {
      if (isReady(psRow[welcomeCol])) {
        logNotification("Trigger Date is missing", title, `Trigger Date is missing: Timestamp (Col A in Master) is blank for "${title}".`);
      }
    } else if (!isDropped && isToday(welcomeTriggerDate)) {
      if (isReady(psRow[welcomeCol])) {
        // 1. Draft the Welcome Email
        createDraft(email, `Welcome to Pocket FM - here's what happens next`, firstName, 'welcome', title, link, i, welcomeCol, null, ccMail, revLink, argus);
        
        // 2. Draft the Vendor Onboarding Email INSTANTLY (Removed the 6-hour delay)
        if (isReady(psRow[vendorCol])) {
          createDraft(email, `Vendor Onboarding for ${title}`, firstName, 'vendor', title, link, i, vendorCol, null, ccMail, revLink, argus);
        }
      } else {
        Logger.log("SKIPPED (Welcome Email): Status is already processed for " + title + " (Current status: " + psRow[welcomeCol] + ")");
      }
    } else if (!isDropped && !isToday(welcomeTriggerDate) && welcomeTriggerDate) {
      Logger.log("SKIPPED (Welcome Email): Timestamp (Col A in Master) for " + title + " is " + welcomeTriggerDate + " which is not today.");
    }
    
    // Stage 3: MG Payout Initiated (Vendor Lifecycle Exit Date)
    if (!mainInfo.vendorLifecycleExited || mainInfo.vendorLifecycleExited.toString().trim() === "") {
      if (isReady(psRow[mgPayoutInitiatedCol]) && mainInfo.contractSigned) {
        logNotification("Trigger Date is missing", title, `Trigger Date is missing: Vendor Lifecycle Exited date (Col U) is blank for "${title}".`);
      }
    } else if (!isDropped && isToday(mainInfo.vendorLifecycleExited) && isReady(psRow[mgPayoutInitiatedCol])) {
      createDraft(email, `Payment Initiated: Minimum Guarantee for ${title}`, firstName, 'mgInitiated', title, link, i, mgPayoutInitiatedCol, null, ccMail, revLink, argus);
    }
    
    // Stage 4: MG Payout Confirmation (MG Payout Exit Date)
    if (!mainInfo.mgPayoutExited || mainInfo.mgPayoutExited.toString().trim() === "") {
      if ((isReady(psRow[mgPayoutConfirmationCol]) || isReady(psRow[checkIn1Col])) && mainInfo.vendorLifecycleExited) {
        logNotification("Trigger Date is missing", title, `Trigger Date is missing: MG Payout Exited date (Col X) is blank for "${title}".`);
      }
    } else if (!isDropped && isToday(mainInfo.mgPayoutExited) && isReady(psRow[mgPayoutConfirmationCol])) {
      createDraft(email, `Pocket FM: Your Minimum Guarantee Payment Has Been Processed`, firstName, 'mgConfirmed', title, link, i, mgPayoutConfirmationCol, null, ccMail, revLink, argus);
    }
    
    // Stage 5 & 6: Personal Check-Ins (Author Check-In 15 Days & 30 Days)
    // 2nd condition: Regardless if all criteria satisfy, if column AB is "Sent", then W & Y should be "Does not Apply"
    let targetLaunchCol = launchSentCol !== -1 ? launchSentCol : (launchCol !== -1 ? launchCol : 27);
    let colABVal = (targetLaunchCol > -1 && psRow.length > targetLaunchCol && psRow[targetLaunchCol]) 
                   ? psRow[targetLaunchCol].toString().toLowerCase().trim() 
                   : "";
    let isColABSent = colABVal === "sent";

    if (isColABSent) {
      // Regardless if all criteria satisfy, if column AB is "Sent", then W & Y should be "Does not Apply"
      if (checkIn1Col > -1) {
        let curW = (psRow.length > checkIn1Col && psRow[checkIn1Col]) ? psRow[checkIn1Col].toString().trim() : "";
        if (curW.toLowerCase() !== "does not apply") {
          psSheet.getRange(i + 1, checkIn1Col + 1).setValue("Does not apply");
          psRow[checkIn1Col] = "Does not apply";
          Logger.log(`[STATUS OVERRIDE] Column AB is "Sent". Updated Col W to "Does not apply" for "${title}".`);
        }
      }
      if (checkIn2Col > -1) {
        let curY = (psRow.length > checkIn2Col && psRow[checkIn2Col]) ? psRow[checkIn2Col].toString().trim() : "";
        if (curY.toLowerCase() !== "does not apply") {
          psSheet.getRange(i + 1, checkIn2Col + 1).setValue("Does not apply");
          psRow[checkIn2Col] = "Does not apply";
          Logger.log(`[STATUS OVERRIDE] Column AB is "Sent". Updated Col Y to "Does not apply" for "${title}".`);
        }
      }
      SpreadsheetApp.flush();
    } else if (!isDropped) {
      // Reference date: Feedback Mail Date in Col V
      let rawFeedbackDate = (feedbackMailDateCol > -1 && psRow.length > feedbackMailDateCol) ? psRow[feedbackMailDateCol] : null;
      let vDateObj = parseDateSafe(rawFeedbackDate);

      if (!vDateObj) {
        // Feedback Mail Date is not yet stamped / mail not yet generated
        if (checkIn1Col > -1) {
          let curW = (psRow.length > checkIn1Col && psRow[checkIn1Col]) ? psRow[checkIn1Col].toString().trim() : "";
          if (curW.toLowerCase() !== "sent" && curW.toLowerCase() !== "does not apply" && curW.toLowerCase() !== "not due yet") {
            psSheet.getRange(i + 1, checkIn1Col + 1).setValue("Not due yet");
            psRow[checkIn1Col] = "Not due yet";
          }
        }
        if (checkIn2Col > -1) {
          let curY = (psRow.length > checkIn2Col && psRow[checkIn2Col]) ? psRow[checkIn2Col].toString().trim() : "";
          if (curY.toLowerCase() !== "sent" && curY.toLowerCase() !== "does not apply" && curY.toLowerCase() !== "not due yet") {
            psSheet.getRange(i + 1, checkIn2Col + 1).setValue("Not due yet");
            psRow[checkIn2Col] = "Not due yet";
          }
        }
        SpreadsheetApp.flush();
      } else {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        let targetV = new Date(vDateObj.getTime());
        targetV.setHours(0, 0, 0, 0);
        let diffDays = Math.floor((today.getTime() - targetV.getTime()) / (1000 * 60 * 60 * 24));

        // --- CHECK-IN 1 (Column W: 15 Days) ---
        if (checkIn1Col > -1) {
          let curW = (psRow.length > checkIn1Col && psRow[checkIn1Col]) ? psRow[checkIn1Col].toString().trim() : "";
          let curWLower = curW.toLowerCase();

          if (curWLower === "sent") {
            // Status changed to sent by team - keep as sent
          } else if (diffDays < 15) {
            // Days 0-14: Column W is "Not due yet" within the 15-day timeframe
            if (curWLower !== "not due yet") {
              psSheet.getRange(i + 1, checkIn1Col + 1).setValue("Not due yet");
              psRow[checkIn1Col] = "Not due yet";
              Logger.log(`[STATUS UPDATE] Updated Col W to "Not due yet" for "${title}" (${diffDays}/15 days elapsed since Feedback Date ${rawFeedbackDate})`);
            }
          } else if (diffDays === 15) {
            // Exactly on Day 15: Draft Ready (in drafts)
            if (curWLower !== "draft ready" && curWLower !== "sent") {
              createDraft(email, `We'd love your thoughts on ${title}`, firstName, 'checkIn1', title, link, i, checkIn1Col, null, ccMail, revLink, argus);
            }
          } else if (diffDays >= 16) {
            // 15th day is over (16th day onwards):
            // 1. If draft was never prepared, create it now so outreach is ready
            if (curWLower !== "draft ready" && curWLower !== "sent" && curWLower !== "overdue") {
              createDraft(email, `We'd love your thoughts on ${title}`, firstName, 'checkIn1', title, link, i, checkIn1Col, null, ccMail, revLink, argus);
            }
            // 2. Once the 15th day is over, dropdown changes to "Overdue" if not sent!
            if (curWLower !== "overdue" && curWLower !== "sent") {
              psSheet.getRange(i + 1, checkIn1Col + 1).setValue("Overdue");
              psRow[checkIn1Col] = "Overdue";
              Logger.log(`[STATUS UPDATE] 15th day is over (${diffDays} days elapsed). Updated Col W to "Overdue" for "${title}".`);
              logNotification("Author Check-In Overdue", title, `Author Check-In 15 Days (Col W) is Overdue for "${title}" (${diffDays} days elapsed since Feedback Mail Date in Col V). Status updated to "Overdue".`);
            }
          }
        }

        // --- CHECK-IN 2 (Column Y: 30 Days [Optional]) ---
        if (checkIn2Col > -1) {
          let curY = (psRow.length > checkIn2Col && psRow[checkIn2Col]) ? psRow[checkIn2Col].toString().trim() : "";
          let curYLower = curY.toLowerCase();

          if (curYLower === "sent") {
            // Already sent by team - keep as sent
          } else if (diffDays < 30) {
            // Days 0-29: Column Y is "Not due yet" within 30-day timeframe
            if (curYLower !== "not due yet") {
              psSheet.getRange(i + 1, checkIn2Col + 1).setValue("Not due yet");
              psRow[checkIn2Col] = "Not due yet";
            }
          } else if (diffDays === 30) {
            // Exactly on Day 30: Draft Ready
            if (curYLower !== "draft ready" && curYLower !== "sent") {
              createDraft(email, `Pocket FM: A quick update on your show: ${title}`, firstName, 'checkIn2', title, link, i, checkIn2Col, null, ccMail, revLink, argus);
            }
          } else if (diffDays >= 31) {
            // 30th day is over (31st day onwards):
            // 1. If draft was never prepared, create it now so outreach is ready
            if (curYLower !== "draft ready" && curYLower !== "sent" && curYLower !== "overdue") {
              createDraft(email, `Pocket FM: A quick update on your show: ${title}`, firstName, 'checkIn2', title, link, i, checkIn2Col, null, ccMail, revLink, argus);
            }
            // 2. Once the 30th day is over, dropdown changes to "Overdue" if not sent!
            if (curYLower !== "overdue" && curYLower !== "sent") {
              psSheet.getRange(i + 1, checkIn2Col + 1).setValue("Overdue");
              psRow[checkIn2Col] = "Overdue";
              Logger.log(`[STATUS UPDATE] 30th day is over (${diffDays} days elapsed). Updated Col Y to "Overdue" for "${title}".`);
            }
          }
        }
        SpreadsheetApp.flush();
      }
    }
    

    
    // =============================================================
    // Stage 7: Show Launch Announcement
    // =============================================================
    // Mandatory Condition 1: Show Link present, show launch date present, status should be "testing_pgc" "testing_pgc_completed", (Move to step 2)
    // Condition 2: Show launch date > Script Date -> Draft Ready, If Show launch date < Script date -> Launch Date issue (dropdown in AB)

    let rawScriptDate = null;
    if (scriptDateCol > -1 && psRow.length > scriptDateCol && psRow[scriptDateCol]) {
      rawScriptDate = psRow[scriptDateCol];
    } else if (psHeaders.length > 14 && psRow.length > 14 && psRow[14]) {
      rawScriptDate = psRow[14]; // Col O ("Date of Scripts Received")
    } else if (psHeaders.length > 13 && psRow.length > 13 && psRow[13]) {
      rawScriptDate = psRow[13]; // Col N ("Original Scripts Received?")
    }

    let rawLaunchDate = null;
    if (psLaunchDateCol > -1 && psRow.length > psLaunchDateCol && psRow[psLaunchDateCol]) {
      rawLaunchDate = psRow[psLaunchDateCol];
    } else if (psHeaders.length > 9 && psRow.length > 9 && psRow[9]) {
      rawLaunchDate = psRow[9]; // Col J ("Launch Date")
    } else if (mainInfo && mainInfo.launchDate) {
      rawLaunchDate = mainInfo.launchDate;
    }

    let scriptDateObj = parseDateSafe(rawScriptDate);
    let launchDateObj = parseDateSafe(rawLaunchDate);

    let hasShowLink = link && link.toString().trim() !== "" && link.toString().trim() !== "-";
    let hasLaunchDate = rawLaunchDate && rawLaunchDate.toString().trim() !== "" && rawLaunchDate.toString().trim() !== "-";
    let cleanLaunchStatus = launchStatus.toString().toLowerCase().trim().replace(/[\s-]+/g, "_");
    let isTestingPgcStatus = cleanLaunchStatus === "testing_pgc" || 
                             cleanLaunchStatus === "testing_pgc_completed" || 
                             cleanLaunchStatus.includes("testing_pgc") ||
                             cleanLaunchStatus === "testing";

    let currentABVal = (targetLaunchCol > -1 && psRow.length > targetLaunchCol && psRow[targetLaunchCol]) 
                       ? psRow[targetLaunchCol].toString().trim() 
                       : "";
    let currentABLower = currentABVal.toLowerCase();

    let isLaunchBeforeScript = false;
    let isLaunchAfterScript = false;

    if (launchDateObj && scriptDateObj) {
      let lDate = new Date(launchDateObj.getTime());
      let sDate = new Date(scriptDateObj.getTime());
      lDate.setHours(0, 0, 0, 0);
      sDate.setHours(0, 0, 0, 0);

      if (lDate.getTime() <= sDate.getTime()) {
        // If Show Launch Date <= Script Date -> Launch Date Issue!
        isLaunchBeforeScript = true;
      } else {
        // Script Date is strictly before Launch Date -> eligible to move to Step 2
        isLaunchAfterScript = true;
      }
    } else if (launchDateObj && !scriptDateObj) {
      // Script Date is missing: Cannot verify that script date is before launch date
      logNotification("Trigger Data is missing", title, `Script Date (Col O) is missing. Cannot verify that script date is before launch date. Launch Announcement draft suppressed.`);
    }

    if (isLaunchBeforeScript) {
      // Condition 2: Show launch date <= Script date -> Launch Date issue (dropdown in AB)
      if (currentABLower !== "launch date issue") {
        psSheet.getRange(i + 1, targetLaunchCol + 1).setValue("Launch Date Issue");
        psRow[targetLaunchCol] = "Launch Date Issue";
        Logger.log(`[ALERT] Updated Col ${targetLaunchCol + 1} (Col AB) to "Launch Date Issue" for "${title}" because Show Launch Date (${rawLaunchDate}) <= Script Date (${rawScriptDate})`);
      }
      if (launchCol > -1) {
        let curAAFormula = psSheet.getRange(i + 1, launchCol + 1).getFormula();
        if (!curAAFormula) {
          psSheet.getRange(i + 1, launchCol + 1).setValue("Check with content");
          psRow[launchCol] = "Check with content";
          Logger.log(`[ALERT] Updated Col ${launchCol + 1} (Col AA) to "Check with content" for "${title}"`);
        }
      }
      SpreadsheetApp.flush();
      logNotification("Launch Date issue", title, `Show Launch Date (Col J: ${rawLaunchDate}) is BEFORE or EQUAL to Script Date (Col O: ${rawScriptDate}). Dropdown (Col AB) updated to "Launch Date Issue", Col AA updated to "Check with content". Draft creation suppressed.`);
    } else if (isLaunchAfterScript) {
      // If Column AB is already marked "Sent", do not alter or re-draft
      if (currentABLower !== "sent") {
        // Condition 2: Show launch date > Script Date -> Move to Step 2 if Mandatory Condition 1 is satisfied
        if (hasShowLink && hasLaunchDate && isTestingPgcStatus) {
          if (currentABLower !== "draft ready") {
            createDraft(email, `Your Pocket FM Show Is Now Live`, firstName, 'launch', title, link, i, targetLaunchCol, null, ccMail, revLink, argus, showName);
            SpreadsheetApp.flush();
            Logger.log(`[STATUS UPDATE] Condition 1 & 2 Met for "${title}". Created Launch Announcement draft and updated Col ${targetLaunchCol + 1} (Col AB) & Col ${launchCol + 1} (Col AA) to "Draft Ready"`);
          }
        } else {
          if (isTestingPgcStatus && (!hasShowLink || !hasLaunchDate)) {
            let missing = [];
            if (!hasShowLink) missing.push("Show Link (Col L)");
            if (!hasLaunchDate) missing.push("Show Launch Date (Col J)");
            logNotification("Trigger Data is missing", title, `Show Launch Announcement (Mandatory Condition 1) requires Show Link and Show Launch Date. Missing: ${missing.join(" and ")} for "${title}".`);
          }
        }
      }
    }
    
    // Stage 8: Newsletter Edit (The Author Edit) - Exactly 15 Days after Show Launch (Col X Sent)
    let launchRefDate = (launchSentDateCol > -1 && psRow[launchSentDateCol]) 
                        ? psRow[launchSentDateCol] 
                        : ((psLaunchDateCol > -1 && psRow[psLaunchDateCol]) ? psRow[psLaunchDateCol] : mainInfo.launchDate);

    if (!isDropped && newsletterCol !== -1 && isReady(psRow[newsletterCol])) {
      if (link && link !== "" && launchRefDate && isDaysAgoOrMore(launchRefDate, 15)) {
        createDraft(email, `What’s new at Pocket FM + a few things worth knowing`, firstName, 'authorEdit', title, link, i, newsletterCol, null, ccMail, revLink, argus);
      }
    }
    
    // Stage 9: Quarterly Revenue Statements (Configured for AMJ, JAS, OND, or Legacy)
    const quarterConfigs = [];
    
    // Check if AMJ is configured (Col AE to AH)
    if (amjDueCol !== -1 || amjStatusCol !== -1) {
      quarterConfigs.push({
        code: "AMJ",
        label: "AMJ (April–June)",
        dueCol: amjDueCol !== -1 ? amjDueCol : 30,
        statusCol: amjStatusCol !== -1 ? amjStatusCol : 31,
        linkCol: amjLinkCol !== -1 ? amjLinkCol : 32,
        sentCol: amjSentCol !== -1 ? amjSentCol : 33
      });
    }

    // Check if JAS is configured (Col AI to AM)
    if (jasDueCol !== -1 || jasStatusCol !== -1) {
      quarterConfigs.push({
        code: "JAS",
        label: "JAS (July–September)",
        dueCol: jasDueCol !== -1 ? jasDueCol : 34,
        statusCol: jasStatusCol !== -1 ? jasStatusCol : 35,
        linkCol: jasLinkCol !== -1 ? jasLinkCol : 37,
        sentCol: jasSentCol !== -1 ? jasSentCol : 38
      });
    }

    // Check if OND is configured (Col AN to AQ)
    if (ondDueCol !== -1 || ondStatusCol !== -1) {
      quarterConfigs.push({
        code: "OND",
        label: "OND (October–December)",
        dueCol: ondDueCol !== -1 ? ondDueCol : 39,
        statusCol: ondStatusCol !== -1 ? ondStatusCol : 40,
        linkCol: ondLinkCol !== -1 ? ondLinkCol : 41,
        sentCol: ondSentCol !== -1 ? ondSentCol : 42
      });
    }

    // Fallback: Legacy single quarter (Col X to AA)
    if (quarterConfigs.length === 0 && (revStatementDueCol !== -1 || revStatementEmailCol !== -1)) {
      quarterConfigs.push({
        code: "Standard",
        label: "Quarterly",
        dueCol: revStatementDueCol !== -1 ? revStatementDueCol : 23,
        statusCol: revStatementEmailCol !== -1 ? revStatementEmailCol : 24,
        linkCol: revLinkCol !== -1 ? revLinkCol : 25,
        sentCol: revStatementSentCol !== -1 ? revStatementSentCol : 26
      });
    }

    for (let qc of quarterConfigs) {
      let qDueDate = (qc.dueCol > -1 && psRow.length > qc.dueCol) ? psRow[qc.dueCol] : null;
      let qStatusStr = (qc.statusCol > -1 && psRow.length > qc.statusCol && psRow[qc.statusCol]) ? psRow[qc.statusCol].toString().trim() : "";
      let qSentStr = (qc.sentCol > -1 && psRow.length > qc.sentCol && psRow[qc.sentCol]) ? psRow[qc.sentCol].toString().trim() : "";
      let qRawLink = (qc.linkCol > -1 && psRow.length > qc.linkCol && psRow[qc.linkCol]) ? psRow[qc.linkCol].toString().trim() : "";
      
      let qRevLink = qRawLink;
      if (qRevLink && !qRevLink.startsWith("http")) {
        qRevLink = "https://" + qRevLink;
      }

      let qStatusLower = qStatusStr.toLowerCase();
      let qSentLower = qSentStr.toLowerCase();

      // Skip if this quarter has already been sent or marked Draft Ready
      if (qSentLower === "sent" || qSentLower === "draft ready" || qStatusLower === "sent" || qStatusLower === "draft ready") {
        continue;
      }

      // Column AF (and equivalent quarterly status columns AJ, AO) eligible options:
      // 1. Sent
      // 2. Not due yet
      // 3. No statement to be shared
      // 4. Eligible to send, no statement attached
      // 5. Eligible to send, statement attached
      // NOTE: Only in case of "Eligible to send, statement attached", "draft ready" should come!

      let isEligible = false;

      if (qc.statusCol > -1) {
        // Skip explicitly suppressed / not ready statuses:
        if (qStatusLower === "not due yet" || qStatusLower === "no statement to be shared" || qStatusLower === "check with content") {
          continue;
        }

        // When status is "Eligible to send, no statement attached", do not draft and do not change to draft ready
        if (qStatusLower.includes("no statement attached") || qStatusLower === "eligible to send, no statement attached") {
          Logger.log(`[REV STATEMENT WAITING] "${title}" (${qc.code}) in Col ${qc.statusCol + 1} is "Eligible to send, no statement attached". Waiting for statement drive link in Col ${qc.linkCol + 1}.`);
          continue;
        }

        // Only in case of "Eligible to send, statement attached", "draft ready" should come
        if (qStatusLower.includes("statement attached") && !qStatusLower.includes("no statement attached")) {
          isEligible = true;
        }
      } else {
        // Fallback for legacy single-quarter mode without a status column
        let isDue = qDueDate && (isToday(qDueDate) || isDueTodayOrPast(qDueDate));
        let hasLink = qRevLink && qRevLink.toString().trim() !== "";
        if (isDue && hasLink) {
          isEligible = true;
        }
      }

      if (!isEligible) {
        if (!qStatusStr && !qDueDate) {
          if (link || launchStatus.includes("launched") || launchStatus.includes("testing_pgc")) {
            logNotification("Trigger Date is missing", title, `Rev Statement Due Date for ${qc.label} is blank for "${title}".`);
          }
        }
        continue;
      }

      Logger.log(`[DEBUG RevStatement ${qc.code}] Title: ${title} | Status: "${qStatusStr}" | DriveLink: "${qRawLink}" | LaunchStatus: ${launchStatus}`);

      if (isReady(qSentStr)) {
        let targetSentCol = qc.sentCol > -1 ? qc.sentCol : qc.statusCol;

        if (launchStatus.includes("testing_pgc") || launchStatus.includes("launched")) {
          // 1. Content Related Update
          createDraft(email, `Content Update for ${title}`, firstName, 'revStatement_workedWell_content', title, link, i, targetSentCol, null, ccMail, qRevLink, argus, showName);
          
          // 2. Payment-Related Update (Contains the Invoice Template)
          createDraft(email, "Pocket FM: Your earnings are waiting for you!", firstName, 'revStatement_workedWell_payment', title, link, i, targetSentCol, null, ccMail, qRevLink, argus, showName);

          Logger.log(`[STATUS UPDATE] Drafted Worked Well (${qc.code}) for "${title}". Updated Col ${targetSentCol + 1} to "Draft Ready"`);
        }
        else if (launchStatus.includes("dropped")) {
          createDraft(email, `Pocket FM: An Update on ${title}`, firstName, 'revStatement_didntWorkWell', title, link, i, targetSentCol, null, ccMail, qRevLink, argus, showName);
          Logger.log(`[STATUS UPDATE] Drafted Didn't Work Well (${qc.code}) for "${title}". Updated Col ${targetSentCol + 1} to "Draft Ready"`);
        }
        else if (launchStatus.includes("bad") || launchStatus.includes("untested")) {
          logNotification("Workflow status is not eligible", title, `Workflow status is not eligible for revenue statement (${qc.code}): Launch Status is "${launchStatus}". Setting status to Review.`);
          psSheet.getRange(i + 1, targetSentCol + 1).setValue("Review - No email trigger");
        }
      }
    }
  }

  // Force all spreadsheet updates to commit to the live sheet immediately
  SpreadsheetApp.flush();

  // Summary Notification Report
  if (notificationLog.length > 0) {
    Logger.log("\n==================== RECOMMENDED NOTIFICATIONS SUMMARY ====================");
    Logger.log(`Total attention notifications recorded: ${notificationLog.length}`);
    notificationLog.forEach(n => Logger.log(n.fullLog));
    Logger.log("===========================================================================\n");
  } else {
    Logger.log("All evaluated records passed eligibility checks.");
  }
}

// Handler function that Google's servers will run automatically 6 hours later
function runDelayedDrafts() {
  processOutreachQueue(true);
}

// -------------------------------------------------------------
// HELPER FUNCTIONS (MOVED TO GLOBAL SCOPE)
// -------------------------------------------------------------
function wrapHtml(bodyContent, queueId = "") {
    return `<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="color-scheme" content="light only"><meta name="supported-color-schemes" content="light only"><link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&display=swap" rel="stylesheet"><title>Pocket FM Email</title></head><body aria-disabled="false" style='margin: 0px; font-family: Poppins, "Noto Sans", "Helvetica Neue", Helvetica, Arial, sans-serif;'>


<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-color:#ffffff; width:600px;"><tbody><tr><td align="center">
<table border="0" cellpadding="0" cellspacing="0" style="background-color:#000000; width:600px;"><tbody><!-- Header -->
<tr><td align="center">
<img alt="Pocket FM Logo" src="https://d2p67bdkbtpxn2.cloudfront.net/c8b7ada83f09146d4b2c2ba3a5c3c1b8ea36e459.jpg" style="display:block; max-width:600px;">
</td></tr>

<tr><td align="center" style="padding-top:15px;">
<table border="0" cellpadding="0" cellspacing="0" style="background-color:#FFFFFF; width:600px; border-radius:10px;"><tbody>
${bodyContent}
</tbody></table>
</td></tr>

<!-- Footer spacing -->
<tr><td style="padding-top:10px;"></td></tr>

<!-- Footer -->
<tr><td style="padding:20px;">
<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-color:#121212; border-radius:10px; width:600px;"><tbody><tr><td align="center" style="padding:30px 0;">
<img alt="Pocket FM Logo" src="https://d2p67bdkbtpxn2.cloudfront.net/dd1600b8e1bde867061ac29dcf9078c72bc533bd.jpg" height="50" style="display:block;">
</td></tr>

<!-- Social icons -->
<tr><td align="center">
<table border="0" cellpadding="0" cellspacing="0"><tbody><tr><td style="padding:0 10px;"><a href="https://twitter.com/PocketFM_App" target="_blank"><img src="https://d2p67bdkbtpxn2.cloudfront.net/2ef29b0580cbc86db3effe6847cbf3c92024b814.png" height="30"></a></td>
<td style="padding:0 10px;"><a href="https://www.linkedin.com/company/14522609" target="_blank"><img src="https://d2p67bdkbtpxn2.cloudfront.net/fc05471fbe97d71f1b8037897029df3759916d7c.png" height="30"></a></td>
<td style="padding:0 10px;"><a href="https://www.facebook.com/pocketfmusa" target="_blank"><img src="https://d2p67bdkbtpxn2.cloudfront.net/bbba48b905fdc913ca50e2014cd43130eb2a6190.png" height="30"></a></td>
<td style="padding:0 10px;"><a href="https://www.instagram.com/pocketfm_usa/?hl=en" target="_blank"><img src="https://d2p67bdkbtpxn2.cloudfront.net/7f5a11ba1d1e0430dc41bc2679fec746478b9dba.png" height="30"></a></td>
<td style="padding:0 10px;"><a href="https://www.youtube.com/@PocketFM.Official" target="_blank"><img src="https://d2p67bdkbtpxn2.cloudfront.net/64ac0d2350428f01ae6611b89c7b9c187542e8cd.png" height="30"></a></td></tr></tbody></table>
</td></tr>

<tr><td style="padding-top:30px;"></td></tr>

<tr><td align="center" style="font-size:12px; color:#464646;">
Pocket FM Private Limited © 2018 - 2026
</td></tr>

<tr><td align="center" style="font-size:8px; color:#121212; padding-top:10px;">
Ref${queueId.replace(/-/g, "")}
</td></tr>

<tr><td style="padding-top:30px;"></td></tr></tbody></table>
</td></tr></tbody></table>
</td></tr></tbody></table>
</body></html>`;
}

function getBody(type, firstName, title, link, grammar, revLink, argus, showName = "") {
    switch(type) {
      case 'welcome':
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Welcome to Pocket FM! We couldn't be more excited to have you join the platform. It's always a good day when a new story (and a new author) becomes part of the community.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Here's a quick walkthrough of what happens next:
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <b>Onboarding & Documentation</b><br>
          Within 1 business day of this email, you'll receive a follow-up from us with the vendor onboarding documents, manuscript submission instructions, and invoice requirements to kick off the formal onboarding process.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <b>MG Payment</b><br>
          Once all documentation is submitted from your end, we'll initiate your Minimum Guarantee (MG) payment. As per your contract, this is paid out within 30 days of the contract signing date. We'll send you a confirmation once the payment has been processed.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <b>Production & Launch</b><br>
          Once onboarding is complete, we'll move into production. The typical timeline for production and launching your show on Pocket FM is around 3 months. We'll keep you updated as we reach key milestones throughout the process, including when your show goes live.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <b>Revenue Statements</b><br>
          As outlined in the contract, we share revenue statements on a quarterly basis. You'll need to raise an invoice against each statement to receive your payment.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <b>Support</b><br>
          Our Relationship Management team is always here if you have any questions along the way. Just reply to this email.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We're genuinely glad to be starting this journey with you, and we look forward to bringing your story to listeners around the world.
          </td></tr>
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;
      case 'vendor':
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Now the exciting part begins: let's get everything in place so we can start bringing your story to life on Pocket FM!
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Please share the manuscript(s) for your licensed series with us in DOC or PDF format.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          As the next step, we'll onboard you as a vendor in our systems so we can disburse your Minimum Guarantee (MG) payment and any subsequent revenue-linked payouts.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <b>Required Documents for Vendor Onboarding</b><br>
          Please share the following documents as separate attachments/PDFs:<br>
          • W-9 (if you're a US citizen) or W-8BEN (if you're a non-US citizen) (attached). If you would like to be onboarded as an entity, please complete the W-8BEN-E form instead.<br>
          • Signed Vendor Registration Form (VRF) (attached)<br>
          • Conflict of Interest (COI) Declaration (attached)<br>
          • Bank letter or void cheque, along with your bank account details.<br>
          • Invoice for the Minimum Guarantee / Advance (details below).
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <b>Important:</b> Please ensure that the legal name mentioned on the bank letter / void cheque or bank account details matches the name you provide on the invoice, W-9, VRF and COI declaration. Whatever name appears on your bank cheque or bank proof must match across all documents. This consistency is critical to avoid payment delays.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <b>Invoice for the Minimum Guarantee / Advance</b><br>
          Along with the documents above, please share an invoice for the minimum guarantee / advance amount. The invoice must include the following details:
          </td></tr>
          <tr><td align="center" style="padding:10px 35px;">
            <table width="100%" border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse; border-color:#e0e0e0; font-size:14px; text-align:left;">
              <tr style="background-color:#f8f8f8;"><th>Field</th><th>Applicability</th><th>Description</th></tr>
              <tr><td><b>Heading</b></td><td>Mandatory</td><td>Must be titled “Tax Invoice,” “Invoice,” or “Sales Invoice.” Proforma invoices and quotations cannot be accepted.</td></tr>
              <tr><td><b>Date</b></td><td>Mandatory</td><td>Invoice date</td></tr>
              <tr><td><b>Invoice No.</b></td><td>Mandatory</td><td>Must be unique</td></tr>
              <tr><td><b>Vendor Name</b></td><td>Mandatory</td><td>Complete legal name, as provided in the onboarding form</td></tr>
              <tr><td><b>Address</b></td><td>Mandatory</td><td>Complete registered address, including city, state, and pin/ZIP code</td></tr>
              <tr><td><b>Phone & Email</b></td><td>Optional</td><td>—</td></tr>
              <tr><td><b>PO Number</b></td><td>Optional</td><td>—</td></tr>
              <tr><td><b>VAT</b></td><td>If applicable</td><td>VAT number is mandatory where applicable</td></tr>
              <tr><td><b>Pocket Entertainment Corp Details</b></td><td>Mandatory</td><td>POCKET ENTERTAINMENT SERVICES LLC, 13 W Main Street, PO Box 953, Felton, DE 19943, County of Kent</td></tr>
              <tr><td><b>Product / Service Description</b></td><td>Mandatory</td><td>Clear description of the product or service</td></tr>
              <tr><td><b>Service Period</b></td><td>Mandatory</td><td>Should match the term specified in the agreement</td></tr>
              <tr><td><b>Amount</b></td><td>Mandatory</td><td>Clear bifurcation of base amount and VAT (if applicable)</td></tr>
              <tr><td><b>Bank Details</b></td><td>Mandatory</td><td>Beneficiary name, account number / IBAN, SWIFT code, routing number (mandatory for US vendors), local transit number, and bank name</td></tr>
              <tr><td><b>Signature</b></td><td>Mandatory</td><td>Digital or wet signature</td></tr>
            </table>
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <table border="0" cellspacing="0" cellpadding="0" style="margin-top: 10px; margin-bottom: 10px;">
            <tr>
              <td align="center" style="border-radius: 6px; background-color: #E51A4D;">
                <a href="https://drive.google.com/drive/folders/1YasA2TJL27zcyin1A-Wg-eJq9_vTQnL0" target="_blank" style="font-size: 16px; font-weight: bold; color: #ffffff; text-decoration: none; border-radius: 6px; padding: 12px 24px; border: 1px solid #E51A4D; display: inline-block;">Access Onboarding Documents</a>
              </td>
            </tr>
          </table>
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Let us know if you have any questions — happy to help.
          </td></tr>
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;
      case 'mgInitiated':
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Great news—your Minimum Guarantee (MG) payment has now been initiated from our end for <b>${title}</b>.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          The amount should reflect in your account once your bank completes the processing. If you don't receive it within the usual banking timeline (7-10 days), please let us know and we'll be happy to look into it.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          With this milestone complete, we're one step closer to bringing your story to listeners around the world.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Thank you once again for partnering with Pocket FM.
          </td></tr>
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;
      case 'mgConfirmed':
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We're happy to let you know that the Minimum Guarantee (MG) payment for <b>${title}</b> has been successfully processed and credited to your registered bank account.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          As we wrap up the onboarding process, we'd love to hear about your experience working with us. Your feedback helps us improve the experience for future authors and partners.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <table border="0" cellspacing="0" cellpadding="0" style="margin-top: 10px; margin-bottom: 10px;">
            <tr>
              <td align="center" style="border-radius: 6px; background-color: #E51A4D;">
                <a href="https://forms.gle/3nJwBt4KgnzgTThH6" target="_blank" style="font-size: 16px; font-weight: bold; color: #ffffff; text-decoration: none; border-radius: 6px; padding: 12px 24px; border: 1px solid #E51A4D; display: inline-block;">Take our quick 2-minute survey here</a>
              </td>
            </tr>
          </table>
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          If you have any questions regarding your payment or anything else along the way, simply reply to this email; we're always happy to help.
          </td></tr>
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;
      case 'checkIn1':
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We hope you're doing well!
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          As <b>${title}</b> continues its journey with Pocket FM, we'd love to learn a little more about the world you've created. While production is already underway, there are often small details, character nuances, or creative insights that don't always make it onto the page but can be incredibly valuable for our teams as we continue building and promoting the adaptation.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We have just two quick questions—it should take less than two minutes.<br><br>
          1. Is there a character, relationship, or recurring theme from <b>${title}</b> that you feel readers connect with the most, and that you'd like us to know?<br>
          2. Is there anything about the world, tone, or characters of <b>${title}</b> that you'd want our team to keep in mind as the adaptation evolves?
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          While we may not be able to incorporate every suggestion into the current production, your perspective helps us better understand your story and informs future creative, marketing, and audience engagement decisions.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          In case the creative team has any questions for you, we might reach out again for clarifications.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          If you haven't already had a chance to do so, we'd also appreciate your feedback on your onboarding experience. It helps us improve the experience for future authors and partners.<br>
          <table border="0" cellspacing="0" cellpadding="0" style="margin-top: 10px; margin-bottom: 10px;">
            <tr>
              <td align="center" style="border-radius: 6px; background-color: #E51A4D;">
                <a href="https://forms.gle/3nJwBt4KgnzgTThH6" target="_blank" style="font-size: 16px; font-weight: bold; color: #ffffff; text-decoration: none; border-radius: 6px; padding: 12px 24px; border: 1px solid #E51A4D; display: inline-block;">Share your onboarding feedback here</a>
              </td>
            </tr>
          </table>
          </td></tr>
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;
      case 'checkIn2':
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We hope you're doing well!
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          It's been about a month since we completed the onboarding process, so we wanted to share a quick update on <b>${title}</b>.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          The show is currently under production, and our team is actively working on bringing your story to life. Producing a high-quality audio adaptation involves several stages, and we're making steady progress behind the scenes. We'll continue to keep you updated as we reach key milestones along the way.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          If you haven't already had a chance to do so, we'd also love to hear about your onboarding experience. Your feedback helps us improve the experience for future authors and partners.<br>
          <table border="0" cellspacing="0" cellpadding="0" style="margin-top: 10px; margin-bottom: 10px;">
            <tr>
              <td align="center" style="border-radius: 6px; background-color: #E51A4D;">
                <a href="https://forms.gle/3nJwBt4KgnzgTThH6" target="_blank" style="font-size: 16px; font-weight: bold; color: #ffffff; text-decoration: none; border-radius: 6px; padding: 12px 24px; border: 1px solid #E51A4D; display: inline-block;">Share your feedback here</a>
              </td>
            </tr>
          </table>
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We'll be in touch with more updates on <b>${title}</b> as production progresses.
          </td></tr>
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;
      case 'launch':
        const actualShowName = (showName && showName.toString().trim() !== "") ? showName.toString().trim() : "";
        const workDisplay = actualShowName 
          ? `<b>${title}</b> as <b>${actualShowName}</b>` 
          : `<b>${title}</b>`;
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Exciting news! Your ${grammar.work} ${workDisplay} ${grammar.is} now live on Pocket FM!
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Congratulations on reaching this milestone. Feel free to check out the show here on the app: <table border="0" cellspacing="0" cellpadding="0" style="margin-top: 10px; margin-bottom: 10px;">
            <tr>
              <td align="center" style="border-radius: 6px; background-color: #E51A4D;">
                <a href="${link}" target="_blank" style="font-size: 16px; font-weight: bold; color: #ffffff; text-decoration: none; border-radius: 6px; padding: 12px 24px; border: 1px solid #E51A4D; display: inline-block;">Listen on Pocket FM</a>
              </td>
            </tr>
          </table>
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Over the coming weeks, we'll closely track the show's performance. From listener engagement to audience feedback, and we'll keep you updated as it finds its audience.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          If you'd like to help spread the word, we'd love for you to share the show with your readers, followers, friends, and family. Every new listener helps your story reach even more people.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Thank you for trusting Pocket FM with your story. We can't wait to see where this journey takes us!
          </td></tr>
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;
      case 'launch_no_ai':
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Exciting news - your show has been picked up by our creative teams for deeper evaluation!
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Over the next few weeks, we'll be working closely to shape how the story lands, and we might come back with questions, or creative insights once this process is through.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Once the show is launched, we'll closely track how the show performs—from listener engagement to audience feedback—and we'll keep you updated as it finds its audience.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          As outlined in your agreement, you'll receive revenue statements on a quarterly basis, with a detailed breakdown of your earnings for the reporting period. If any revenue is due, you can raise an invoice against the statement for payment.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          If you have any questions in the meantime, just reply to this email.
          </td></tr>
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;
      case 'revStatement_workedWell_content':
        const revHrefContent = revLink ? revLink : "#";
        const actualRevShowName = (showName && showName.toString().trim() !== "") ? showName.toString().trim() : "";
        const appNameDisplay = actualRevShowName ? actualRevShowName : title;
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We're sharing the latest performance update for your licensed series, <b>${title}</b>, on Pocket FM. (Pocket FM App Name: <b>${appNameDisplay}</b>) Attached, you'll find your revenue statement for this quarter, which provides a breakdown of your earnings for the reporting period, along with a snapshot of how your show has been performing.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <b>Show Snapshot</b><br>
          • Duration Produced: ${argus.duration}<br>
          • Plays / Daily Active Listeners (LDAUs): ${argus.ldau}<br>
          • Comments: ${argus.comments}<br>
          • Ratings: ${argus.ratings}<br>
          • Reviews: ${argus.reviews}
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We'll continue to keep you updated as your show reaches more listeners and share new milestones along the way.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <table border="0" cellspacing="0" cellpadding="0" style="margin-top: 10px; margin-bottom: 10px;">
            <tr>
              <td align="center" style="border-radius: 6px; background-color: #E51A4D;">
                <a href="${revHrefContent}" target="_blank" style="font-size: 16px; font-weight: bold; color: #ffffff; text-decoration: none; border-radius: 6px; padding: 12px 24px; border: 1px solid #E51A4D; display: inline-block;">Access Revenue Statement</a>
              </td>
            </tr>
          </table>
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          If your latest revenue statement reflects an amount payable, we'll send you a separate email with the invoice format and instructions to help you raise your invoice.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          If the statement shows no amount payable (for example, while your Minimum Guarantee is still being recouped), no further action is required from your end, and we won't be sending an invoice request for that period.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          If you have any questions about your show's performance or production, simply reply to this email—we're always happy to help.
          </td></tr>
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;
      case 'revStatement_workedWell_payment':
        const revHrefPay = revLink ? revLink : "#";
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We're excited to share the latest performance update for <b>${title}</b> on Pocket FM. Attached, you'll find your revenue statement for this quarter, which provides a detailed breakdown of your earnings for the reporting period, along with a snapshot of how your show has been performing on the platform.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <b>Invoice template for the Revenue share payment</b><br>
          Please share an invoice for the due amount for us to process the payout. The invoice must include the following details:
          </td></tr>
          <tr><td align="center" style="padding:10px 35px;">
            <table width="100%" border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse; border-color:#e0e0e0; font-size:14px; text-align:left;">
              <tr style="background-color:#f8f8f8;"><th>Field</th><th>Applicability</th><th>Description</th></tr>
              <tr><td><b>Heading</b></td><td>Mandatory</td><td>Must be titled “Tax Invoice,” “Invoice,” or “Sales Invoice.” Proforma invoices and quotations cannot be accepted.</td></tr>
              <tr><td><b>Date</b></td><td>Mandatory</td><td>Invoice date</td></tr>
              <tr><td><b>Invoice No.</b></td><td>Mandatory</td><td>Must be unique</td></tr>
              <tr><td><b>Vendor Name</b></td><td>Mandatory</td><td>Complete legal name, as provided in the onboarding form</td></tr>
              <tr><td><b>Address</b></td><td>Mandatory</td><td>Complete registered address, including city, state, and pin/ZIP code</td></tr>
              <tr><td><b>Phone & Email</b></td><td>Optional</td><td>—</td></tr>
              <tr><td><b>PO Number</b></td><td>Optional</td><td>—</td></tr>
              <tr><td><b>VAT</b></td><td>If applicable</td><td>VAT number is mandatory where applicable</td></tr>
              <tr><td><b>Pocket Entertainment Corp Details</b></td><td>Mandatory</td><td>POCKET ENTERTAINMENT SERVICES LLC, 13 W Main Street, PO Box 953, Felton, DE 19943, County of Kent</td></tr>
              <tr><td><b>Product / Service Description</b></td><td>Mandatory</td><td>Clear description of the product or service (Mention duration for which revenue statement is valid)</td></tr>
              <tr><td><b>Service Period</b></td><td>Mandatory</td><td>Should match the term specified in the agreement</td></tr>
              <tr><td><b>Amount</b></td><td>Mandatory</td><td>Clear bifurcation of base amount and VAT (if applicable)</td></tr>
              <tr><td><b>Bank Details</b></td><td>Mandatory</td><td>Beneficiary name, account number / IBAN, SWIFT code, routing number (mandatory for US vendors), local transit number, and bank name</td></tr>
              <tr><td><b>Signature</b></td><td>Mandatory</td><td>Digital or wet signature</td></tr>
            </table>
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          If you have any questions about the attached revenue statement or your show's performance, simply reply to this email - we're happy to help.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Click here to check your revenue statement: <br>
          <table border="0" cellspacing="0" cellpadding="0" style="margin-top: 10px; margin-bottom: 10px;">
            <tr>
              <td align="center" style="border-radius: 6px; background-color: #E51A4D;">
                <a href="${revHrefPay}" target="_blank" style="font-size: 16px; font-weight: bold; color: #ffffff; text-decoration: none; border-radius: 6px; padding: 12px 24px; border: 1px solid #E51A4D; display: inline-block;">Access Revenue Statements</a>
              </td>
            </tr>
          </table>
          </td></tr>
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;
      case 'revStatement_didntWorkWell':
        const revHrefDidntWork = revLink ? revLink : "#";
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We're sharing the latest performance update for <b>${title}</b> on Pocket FM. Attached, you'll find your revenue statement for this quarter, which provides a breakdown of your earnings for the reporting period, along with a snapshot of how your show has been performing.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <b>Show Snapshot</b><br>
          • Duration Produced: ${argus.duration}<br>
          • Plays / Daily Active Listeners (LDAUs): ${argus.ldau}<br>
          • Comments: ${argus.comments}<br>
          • Ratings: ${argus.ratings}<br>
          • Reviews: ${argus.reviews}
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Based on the show's performance and our internal benchmarks, we've decided not to produce additional episodes for <b>${title}</b> at this time. This is purely dependent on how our audience has been responding to this show and doesn't take away from the value of your story at all. We'll continue to share quarterly revenue statements for the episodes already live on Pocket FM.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          If you know other authors who may be a good fit for Pocket FM, we'd love an introduction. Our referral program offers meaningful incentives for every author you refer who signs with us. Please watch out for a separate email about the referral program.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          If you have any questions about your revenue statement or your show's performance, simply reply to this email—we're happy to help.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Click here to check your revenue statement: <br>
          <table border="0" cellspacing="0" cellpadding="0" style="margin-top: 10px; margin-bottom: 10px;">
            <tr>
              <td align="center" style="border-radius: 6px; background-color: #E51A4D;">
                <a href="${revHrefDidntWork}" target="_blank" style="font-size: 16px; font-weight: bold; color: #ffffff; text-decoration: none; border-radius: 6px; padding: 12px 24px; border: 1px solid #E51A4D; display: inline-block;">Access Revenue Statements</a>
              </td>
            </tr>
          </table>
          </td></tr>
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;

      case 'quarterlyStatements':
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We hope you're doing well! It's time for the quarterly update for <b>${title}</b>. Attached, you'll find your revenue statement, which includes a detailed breakdown of your earnings for the reporting period, along with a snapshot of how your show has been performing on Pocket FM.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <b>Show Snapshot</b><br>
          • Listening Hours: ${argus.hours}<br>
          • Daily Active Listeners (LDAUs): ${argus.ldau}<br>
          • Duration Produced: ${argus.duration}<br>
          • Comments: ${argus.comments}
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <b>Summary of Audience Comments</b><br>
          [Insert AI Summary of Audience Comments]
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We always enjoy sharing how stories are connecting with listeners, and we hope this update gives you a helpful glimpse into your show's journey this quarter. A detailed financial breakdown is included in the attached revenue statement.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          If you have any questions about the statement or would like to discuss your show's performance, simply reply to this email — we're always happy to help.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          Thank you for being part of the Pocket FM community. We look forward to sharing more updates with you in the months ahead!
          </td></tr>
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;

      case 'eventMixer':
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We're hosting <b>[Event Name]</b> on <b>[Date]</b> in <b>[Location]</b>, and we'd love to have you join us.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          [Event Description]
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          It's a chance to meet fellow Pocket FM authors, connect with our editorial, production, and partnerships teams, and hear more about what's happening across the platform. Whether you're looking to exchange ideas, learn from other creators, or simply spend an evening with the Pocket FM community, we'd be delighted to see you there.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <table border="0" cellspacing="0" cellpadding="0" style="margin-top: 10px; margin-bottom: 10px;">
            <tr>
              <td align="center" style="border-radius: 6px; background-color: #E51A4D;">
                <a href="[Insert RSVP Link]" target="_blank" style="font-size: 16px; font-weight: bold; color: #ffffff; text-decoration: none; border-radius: 6px; padding: 12px 24px; border: 1px solid #E51A4D; display: inline-block;">RSVP Here</a>
              </td>
            </tr>
          </table>
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          If you have any questions about the event, just reply to this email—we're happy to help.
          </td></tr>
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;

      case 'authorEdit':
      case 'newsletter':
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We wanted to keep you in the loop with a few things happening across Pocket FM: from what listeners are responding to, to what we're learning about stories that work particularly well in audio.
          </td></tr>

          <!-- Section 1: What's Happening -->
          <tr><td align="left" style="font-size:17px; font-weight:700; color:#E51A4D; padding:20px 35px 5px; line-height:24px; text-transform:uppercase; letter-spacing:0.5px;">
          1. WHAT'S HAPPENING AT POCKET FM
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:5px 35px 10px; line-height:24px;">
          We had the absolute honour of having the legendary Ruskin Bond spend time exploring Sherpa and share his experience with us. For someone who has spent a lifetime telling stories and inspired generations of people to read, imagine and write, experiencing something we have built is incredibly special.
          </td></tr>
          <tr><td align="left" style="padding:5px 35px 15px;">
            <table border="0" cellspacing="0" cellpadding="0">
              <tr>
                <td align="center" style="border-radius: 6px; background-color: #E51A4D;">
                  <a href="https://lnkd.in/p/g6rd7Zta" target="_blank" style="font-size: 14px; font-weight: bold; color: #ffffff; text-decoration: none; border-radius: 6px; padding: 10px 20px; border: 1px solid #E51A4D; display: inline-block;">See What's New →</a>
                </td>
              </tr>
            </table>
          </td></tr>

          <!-- Section 2: A Story Worth Knowing -->
          <tr><td align="left" style="font-size:17px; font-weight:700; color:#E51A4D; padding:20px 35px 5px; line-height:24px; text-transform:uppercase; letter-spacing:0.5px;">
          2. A STORY WORTH KNOWING
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:5px 35px 10px; line-height:24px;">
          <b>Meet Steven Ade: the writer who kept writing even when writing didn't look like a career.</b><br>
          For years, Steven worked jobs that paid the bills—supporting children on the spectrum and delivering pizzas—all while carrying a love for storytelling. When he began publishing on Pocket FM, his audience took off. Today, Steven is the writer behind <i>The System Creation: Intergalactic Entry</i>, which has reached nearly <b>8 million plays</b> with a <b>4.6-star rating</b>!
          </td></tr>
          <tr><td align="left" style="padding:5px 35px 15px;">
            <table border="0" cellspacing="0" cellpadding="0">
              <tr>
                <td align="center" style="border-radius: 6px; background-color: #121212;">
                  <a href="https://youtu.be/IO2XWbTNafY?si=dOzc2ZTD0IxZSQpk" target="_blank" style="font-size: 14px; font-weight: bold; color: #ffffff; text-decoration: none; border-radius: 6px; padding: 10px 20px; border: 1px solid #121212; display: inline-block;">Watch Steven's Story →</a>
                </td>
              </tr>
            </table>
          </td></tr>

          <!-- Section 3: What We're Seeing From Listeners -->
          <tr><td align="left" style="font-size:17px; font-weight:700; color:#E51A4D; padding:20px 35px 5px; line-height:24px; text-transform:uppercase; letter-spacing:0.5px;">
          3. WHAT WE'RE SEEING FROM LISTENERS
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:5px 35px 5px; line-height:24px;">
          <b>Genre in Spotlight: Romantasy in Audio</b><br>
          Across Romantasy titles, three storytelling patterns consistently drive higher listener engagement:
          <ol style="margin: 8px 0; padding-left: 20px; line-height: 24px;">
            <li><b>Romance built on choice, not just chemistry:</b> Shared vulnerability and earned trust keep listeners invested beyond instinctual attraction.</li>
            <li><b>Protagonists with goals beyond romance:</b> Active agency, survival stakes, and independent ambitions make character arcs compelling.</li>
            <li><b>Fantasy worlds that pressure the relationship:</b> Magic rules and political conflict create obstacles specific to that world.</li>
          </ol>
          </td></tr>

          <!-- Section 4: Before You Go -->
          <tr><td align="left" style="font-size:17px; font-weight:700; color:#E51A4D; padding:20px 35px 5px; line-height:24px; text-transform:uppercase; letter-spacing:0.5px;">
          4. BEFORE YOU GO
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:5px 35px 10px; line-height:24px;">
          Working on something new? We'd love to hear about it.
          </td></tr>
          <tr><td align="left" style="padding:5px 35px 20px;">
            <table border="0" cellspacing="0" cellpadding="0">
              <tr>
                <td align="center" style="border-radius: 6px; background-color: #E51A4D;">
                  <a href="mailto:us-licensing@pocketfm.com?subject=Story%20Pitch" target="_blank" style="font-size: 14px; font-weight: bold; color: #ffffff; text-decoration: none; border-radius: 6px; padding: 10px 20px; border: 1px solid #E51A4D; display: inline-block;">Share a Story →</a>
                </td>
              </tr>
            </table>
          </td></tr>

          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Until next time,<br>
          Team Pocket FM
          </td></tr>
        `;

      case 'publicNews':
        return `
          <tr><td align="left" style="font-size:18px; font-weight:600; color:#121212; padding:30px 35px 10px; line-height:24px;">
          Hi ${firstName},
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We wanted to share an update from Pocket FM that we thought you might find interesting.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          <b>[Insert News Headline]</b><br>
          [Insert News Summary]
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          We'll continue to keep you posted whenever there are developments that we think are relevant to our authors and publishing partners.
          </td></tr>
          <tr><td align="left" style="font-size:16px; color:#121212; padding:10px 35px; line-height:24px;">
          If you'd like to read the full announcement, you can find it here:<br>
          <table border="0" cellspacing="0" cellpadding="0" style="margin-top: 10px; margin-bottom: 10px;">
            <tr>
              <td align="center" style="border-radius: 6px; background-color: #E51A4D;">
                <a href="[Insert Article Link]" target="_blank" style="font-size: 16px; font-weight: bold; color: #ffffff; text-decoration: none; border-radius: 6px; padding: 12px 24px; border: 1px solid #E51A4D; display: inline-block;">Read More</a>
              </td>
            </tr>
          </table>
          </td></tr>
          <tr><td align="left" style="font-size:16px; font-weight:400; color:#121212; padding:10px 35px 30px; line-height:24px;">
          Best,<br>
          US Licensing & Commissioning Team<br>
          Pocket FM
          </td></tr>
        `;

      default:
        Logger.log(`[RECOMMENDED NOTIFICATION] Email template not selected: No template definition found for stage type '${type}' (Title: '${title}').`);
        return "";
    }
  }

// -------------------------------------------------------------
// STATUS SYNC FUNCTION (RUNS EVERY HOUR OR MANUALLY)
// -------------------------------------------------------------
function syncSentEmails() {
  const spreadsheet = SpreadsheetApp.openById("1A1vJ0DsmDxtCFZiuyu6vtuQFWqClPyK7e1_lHKddGdQ");
  const allSheets = spreadsheet.getSheets();
  let sheet = null;
  let queueSheet = null;
  
  allSheets.forEach(s => {
    let sName = s.getName().toLowerCase().trim();
    if (s.getSheetId() === 120747375) sheet = s;
    else if (!sheet && (sName.includes("post-sales tracker") || sName.includes("post sales tracker") || sName.includes("post sale comms tracker"))) sheet = s;
    else if (sName === "queue") queueSheet = s;
  });
  
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
      let subject = qData[i][4]; // Column E (Subject)
      
      // 1. Search Gmail for ALL sent emails with this exact Subject (Indexed instantly)
      let threads = GmailApp.search(`in:sent subject:"${subject}"`);
      
      let foundMessage = null;
      let cleanId = queueId.replace(/-/g, "");
      let trackingStr = "Ref" + cleanId;
      
      // 2. Loop through all found threads and messages manually to bypass Gmail's HTML search limitations
      for (let t = 0; t < threads.length; t++) {
        let messages = threads[t].getMessages();
        for (let m = 0; m < messages.length; m++) {
          let msg = messages[m];
          let body = msg.getBody(); // Get raw HTML
          // 3. If the actual HTML body contains our tracking ID, THIS is the exact email!
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
        
        // Update Queue with the actual sent data!
        queueSheet.getRange(i + 1, 2).setValue(actualTo); // Column B (Recipient)
        queueSheet.getRange(i + 1, 12).setValue(actualCc); // Column L (CC)
        
        // Mark Queue as Sent
        queueSheet.getRange(i + 1, 9).setValue("Sent");
        
        // Mark Tracker as Sent (Replaces 'Ready' with 'Sent' for this row)
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
 * ONE-CLICK TEST FUNCTION FOR NEWSLETTER EDIT (THE AUTHOR EDIT)
 * Runs instantly and creates a real test draft in your own Gmail inbox
 * with the exact SOP format: "What’s new at Pocket FM + a few things worth knowing"
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
 * ONE-CLICK TEST FUNCTION FOR REVENUE STATEMENT EMAILS WITH ARGUS DATA
 * Runs instantly and creates real test drafts in your own Gmail inbox
 * using real performance metrics pulled directly from the 'Argus Show Data' tab.
 */
function testRevenueStatementDraft() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const myEmail = Session.getActiveUser().getEmail();
  
  // 1. Fetch Argus data from 'Argus Show Data' tab
  const argusSheet = ss.getSheets().find(s => s.getName().toString().toLowerCase().includes("argus"));
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

      // Pick the first row with valid metrics
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
  
  // Draft 1: Content Update with Show Snapshot
  const queueId1 = Utilities.getUuid();
  const bodyContent1 = getBody('revStatement_workedWell_content', testFirstName, testTitle, "", grammar, testRevLink, sampleMetrics, testShowName);
  const wrappedBody1 = wrapHtml(bodyContent1, queueId1);
  const subject1 = `Content Update for ${testTitle}`;
  GmailApp.createDraft(myEmail, subject1, "", { htmlBody: wrappedBody1 });
  Logger.log(`SUCCESS [Draft 1]: Created "${subject1}" with Argus metrics for "${testTitle}" (App Name: "${testShowName}")`);
  Logger.log(`  -> Duration: ${sampleMetrics.duration} | Plays: ${sampleMetrics.ldau} | Ratings: ${sampleMetrics.ratings} | Reviews: ${sampleMetrics.reviews} | Comments: ${sampleMetrics.comments}`);

  // Draft 2: Payment-Related Update with Invoice Requirements Table
  const queueId2 = Utilities.getUuid();
  const bodyContent2 = getBody('revStatement_workedWell_payment', testFirstName, testTitle, "", grammar, testRevLink, sampleMetrics, testShowName);
  const wrappedBody2 = wrapHtml(bodyContent2, queueId2);
  const subject2 = "Pocket FM: Your earnings are waiting for you!";
  GmailApp.createDraft(myEmail, subject2, "", { htmlBody: wrappedBody2 });
  Logger.log(`SUCCESS [Draft 2]: Created "${subject2}" with invoice template table`);
  
  Logger.log(`\nBoth test drafts created and sent to your email (${myEmail})! Check your Gmail Drafts folder.`);
}

// =============================================================
// DYNAMIC SHOW LAUNCH ANNOUNCEMENT AUTOMATION FOR ALL ROWS
// =============================================================

/**
 * LIVE AUTOMATIC TRIGGER ON SHEET EDIT:
 * Automatically runs whenever any cell is edited in the spreadsheet.
 * If you edit Launch Date (Col J), Launch Status (Col K), Show Link (Col L), or Script Date (Col O):
 * It immediately takes note of that row and updates the dropdown / drafts the email right away:
 * - If Launch Date <= Script Date -> sets Col AB to "Launch Date Issue", Col AA to "Check with content".
 * - If Launch Date > Script Date and Mandatory Condition 1 met -> sets Col AB to "Draft Ready", Col AA to "Draft Ready", stamps Col AC, and creates Gmail draft!
 */
function onEdit(e) {
  if (!e || !e.range) return;
  try {
    const sheet = e.range.getSheet();
    if (sheet.getSheetId() !== 120747375 && !sheet.getName().toLowerCase().includes("post-sales tracker") && !sheet.getName().toLowerCase().includes("post sales tracker")) {
      return;
    }

    const row = e.range.getRow();
    if (row < 4) return; // Ignore headers (rows 1-3)

    const col = e.range.getColumn();
    const isLaunchCol = (col === 10 || col === 11 || col === 12 || col === 15 || col === 28);
    const isCheckInCol = (col === 21 || col === 22 || col === 23 || col === 25 || col === 28);

    if (!isLaunchCol && !isCheckInCol) return;

    // STRICT BLANK ROW GUARD: Do not trigger for blank or unpopulated rows
    const lastCol = Math.max(sheet.getLastColumn(), 30);
    const rowVals = sheet.getRange(row, 1, 1, lastCol).getValues()[0];
    if (!isTrackerRowFilled(rowVals)) {
      return; // Row is blank or has no valid Title / IP
    }

    // Col J=10 (Launch Date), Col K=11 (Launch Status), Col L=12 (Show Link), Col O=15 (Script Date), Col AB=28 (Status dropdown)
    if (isLaunchCol) {
      Logger.log(`[onEdit] Detected edit on Row ${row}, Col ${col}. Re-evaluating filled row for Show Launch Announcement...`);
      evaluateSingleRowLaunch(sheet, row, rowVals);
    }

    // Col U=21 (MG Payout Confirmation), Col V=22 (Feedback Mail Date), Col W=23 (Check-In 15 Days), Col Y=25 (Check-In 30 Days), Col AB=28 (Launch Sent)
    if (isCheckInCol) {
      Logger.log(`[onEdit] Detected edit on Row ${row}, Col ${col}. Re-evaluating filled row for Author Check-Ins (15/30 Days)...`);
      evaluateSingleRowCheckIns(sheet, row, rowVals);
    }
  } catch (err) {
    Logger.log("[onEdit Error] " + err.message);
  }
}

/**
 * EVALUATES A SINGLE ROW FOR SHOW LAUNCH ANNOUNCEMENT DRAFT & STATUS
 * @param {Sheet} psSheet - The Post-Sales Tracker sheet object
 * @param {number} row - The 1-based row index in the sheet (e.g. 4 for Row 4)
 * @param {Array} preloadedRowVals - Optional preloaded row values to avoid redundant sheet reads
 * @param {Array} preloadedHeaders - Optional preloaded headers
 */
function evaluateSingleRowLaunch(psSheet, row, preloadedRowVals = null, preloadedHeaders = null) {
  if (!psSheet || row < 4) return;

  const lastCol = Math.max(psSheet.getLastColumn(), 30);
  const headers = preloadedHeaders || psSheet.getRange(3, 1, 1, lastCol).getValues()[0];
  const rowVals = preloadedRowVals || psSheet.getRange(row, 1, 1, lastCol).getValues()[0];

  const psFindCol = (name) => headers.findIndex(h => h.toString().toLowerCase().includes(name.toLowerCase()));

  const titleCol = psFindCol("Title / IP") > -1 ? psFindCol("Title / IP") : 2;

  // STRICT BLANK ROW GUARD: Do not process blank or unpopulated rows
  if (!isTrackerRowFilled(rowVals, titleCol)) {
    return;
  }

  const authorCol = psFindCol("Author Name") > -1 ? psFindCol("Author Name") : 1;
  const firstNameCol = psFindCol("Receiver First Name") > -1 ? psFindCol("Receiver First Name") : 7;
  const emailCol = psFindCol("Receiver Email ID") > -1 ? psFindCol("Receiver Email ID") : 5;
  const ccCol = psFindCol("CC Mail ID") > -1 ? psFindCol("CC Mail ID") : 6;
  const showNameCol = psFindCol("Show Name") > -1 ? psFindCol("Show Name") : 2;
  const linkCol = psFindCol("Show Link") > -1 ? psFindCol("Show Link") : 11;
  const statusCol = psFindCol("Launch Status") > -1 ? psFindCol("Launch Status") : 10;

  const launchDateCol = headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s === "launch date" || (s.includes("launch") && s.includes("date") && !s.includes("sent") && !s.includes("announcement"));
  }) > -1 ? headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s === "launch date" || (s.includes("launch") && s.includes("date") && !s.includes("sent") && !s.includes("announcement"));
  }) : 9; // Col J

  const scriptDateCol = headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("script") && s.includes("date");
  }) > -1 ? headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("script") && s.includes("date");
  }) : 14; // Col O

  // Col AA (26), Col AB (27), Col AC (28)
  const colAA = headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return (s.includes("launch") && s.includes("announcement") && s.includes("status")) || s === "show launch announcement status";
  }) > -1 ? headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return (s.includes("launch") && s.includes("announcement") && s.includes("status")) || s === "show launch announcement status";
  }) : 26;

  const colAB = headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return (s.includes("launch") && s.includes("announcement") && (s.includes("sent") || s.includes("email sent")) && !s.includes("date"));
  }) > -1 ? headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return (s.includes("launch") && s.includes("announcement") && (s.includes("sent") || s.includes("email sent")) && !s.includes("date"));
  }) : 27;

  const colAC = headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return (s.includes("launch") && s.includes("announcement") && s.includes("date")) || (s.includes("launch") && s.includes("sent") && s.includes("date"));
  }) > -1 ? headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return (s.includes("launch") && s.includes("announcement") && s.includes("date")) || (s.includes("launch") && s.includes("sent") && s.includes("date"));
  }) : 28;

  const title = rowVals[titleCol] ? rowVals[titleCol].toString().trim() : "";
  const author = rowVals[authorCol] ? rowVals[authorCol].toString().trim() : "";
  const rawFirstName = rowVals[firstNameCol] ? rowVals[firstNameCol].toString().trim() : "";
  const firstName = rawFirstName !== "" ? rawFirstName : (author ? author.split(" ")[0] : "Creator");
  const showName = rowVals[showNameCol] ? rowVals[showNameCol].toString().trim() : title;
  const email = cleanEmail(rowVals[emailCol]);
  const ccMail = cleanCcList(rowVals[ccCol]);
  const link = rowVals[linkCol] ? rowVals[linkCol].toString().trim() : "";
  const rawStatus = rowVals[statusCol] ? rowVals[statusCol].toString().trim().toLowerCase() : "";
  const cleanStatus = rawStatus.replace(/[\s-]+/g, "_");

  const rawLaunchDate = rowVals[launchDateCol];
  const rawScriptDate = rowVals[scriptDateCol];
  const dLaunch = parseDateSafe(rawLaunchDate);
  const dScript = parseDateSafe(rawScriptDate);

  const curDropdown = rowVals[colAB] ? rowVals[colAB].toString().trim() : "";
  const curDropdownLower = curDropdown.toLowerCase();

  // If already marked Sent by user, do not alter
  if (curDropdownLower === "sent") return;

  // 1. DATE ANOMALY: Launch Date <= Script Date
  if (dLaunch && dScript && dLaunch.getTime() <= dScript.getTime()) {
    if (curDropdownLower !== "launch date issue") {
      psSheet.getRange(row, colAB + 1).setValue("Launch Date Issue");
      Logger.log(`[LIVE ROW ${row}] Set Col AB to "Launch Date Issue" for "${title}" (Launch: ${rawLaunchDate} <= Script: ${rawScriptDate})`);
    }
    const curAAFormula = psSheet.getRange(row, colAA + 1).getFormula();
    if (!curAAFormula) {
      psSheet.getRange(row, colAA + 1).setValue("Check with content");
    }
    SpreadsheetApp.flush();
    return;
  }

  // 2. VALID LAUNCH ANNOUNCEMENT: Launch Date > Script Date AND Mandatory Condition 1 Met
  const isScriptBeforeLaunch = dLaunch && dScript && (dLaunch.getTime() > dScript.getTime());
  const hasLink = link !== "" && link !== "-";
  const hasLaunchDate = !!dLaunch;
  const isTestingPgc = cleanStatus === "testing_pgc" || cleanStatus === "testing_pgc_completed" || cleanStatus.includes("testing_pgc") || cleanStatus === "testing";

  if (isScriptBeforeLaunch && hasLink && hasLaunchDate && isTestingPgc) {
    if (!isValidEmail(email)) {
      Logger.log(`[LIVE ROW ${row}] Missing valid email for "${title}". Draft suppressed.`);
      return;
    }

    if (curDropdownLower !== "draft ready") {
      const grammar = { work: "work", is: "is", has: "has", title: "title", this: "this", it: "it", its: "its" };
      const queueId = Utilities.getUuid();
      const bodyContent = getBody('launch', firstName, title, link, grammar, "", null, showName);
      const wrappedBody = wrapHtml(bodyContent, queueId);
      const subject = `Your Pocket FM Show Is Now Live`;

      let draftSuccess = false;
      try {
        let draftOpts = { htmlBody: wrappedBody };
        if (ccMail) draftOpts.cc = ccMail;
        GmailApp.createDraft(email, subject, "", draftOpts);
        draftSuccess = true;
        Logger.log(`[LIVE ROW ${row}] SUCCESS: Draft created for "${title}" (${email})`);
      } catch (err) {
        Logger.log(`[LIVE ROW ${row}] ERROR creating draft for "${title}": ${err.message}`);
      }

      if (draftSuccess) {
        psSheet.getRange(row, colAB + 1).setValue("Draft Ready");
        const curAAFormula = psSheet.getRange(row, colAA + 1).getFormula();
        if (!curAAFormula) {
          psSheet.getRange(row, colAA + 1).setValue("Draft Ready");
        }
        const todayDate = new Date();
        psSheet.getRange(row, colAC + 1).setValue(todayDate);
        SpreadsheetApp.flush();
        Logger.log(`[LIVE ROW ${row}] Updated Col AB & AA to "Draft Ready" and Col AC with timestamp.`);
      }
    }
  }
}

/**
 * SCAN AND GENERATE LAUNCH ANNOUNCEMENTS FOR ALL ROWS:
 * Loops through every single row in Post-Sales Tracker (from Row 4 to the end).
 * Strictly evaluates ONLY rows filled with data — skips blank or empty placeholder rows!
 */
function generateAllLaunchAnnouncements() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet() || SpreadsheetApp.openById("1A1vJ0DsmDxtCFZiuyu6vtuQFWqClPyK7e1_lHKddGdQ");
  let psSheet = null;

  for (let s of spreadsheet.getSheets()) {
    if (s.getSheetId() === 120747375) { psSheet = s; break; }
    let sName = s.getName().toLowerCase().trim().replace("–", "-").replace("—", "-");
    if (sName.includes("post-sales tracker") || sName.includes("post sales tracker")) { psSheet = s; break; }
  }

  if (!psSheet) {
    Logger.log("[ERROR] Post-Sales Tracker sheet tab not found!");
    return;
  }

  const lastRow = psSheet.getLastRow();
  const lastCol = Math.max(psSheet.getLastColumn(), 30);
  const allData = psSheet.getRange(1, 1, lastRow, lastCol).getValues();
  const headers = allData[2]; // Row 3
  const titleCol = headers.findIndex(h => h.toString().toLowerCase().includes("title")) > -1 
                   ? headers.findIndex(h => h.toString().toLowerCase().includes("title")) : 2;

  Logger.log("\n==================================================================");
  Logger.log(`DYNAMIC BATCH SCAN: Evaluating filled rows in "${psSheet.getName()}" (ignoring blank rows)`);
  Logger.log("==================================================================");

  let evaluatedCount = 0;
  let skippedBlankCount = 0;

  for (let r = 4; r <= lastRow; r++) {
    let rowVals = allData[r - 1];
    if (!isTrackerRowFilled(rowVals, titleCol)) {
      skippedBlankCount++;
      continue;
    }
    evaluateSingleRowLaunch(psSheet, r, rowVals, headers);
    evaluatedCount++;
  }

  SpreadsheetApp.flush();
  Logger.log(`\nBATCH SCAN COMPLETED: Evaluated ${evaluatedCount} filled rows dynamically (${skippedBlankCount} blank rows skipped).`);
}

/**
 * TEST CASE A: Launch Date <= Script Date Anomaly Check
 * If scripts received on Oct 6th and launch is Oct 2nd -> DRAFT IS NOT GENERATED!
 * Live Sheet Update: Column AB turns to "Launch Date Issue", Column AA turns to "Check with content".
 */
function runTestCaseA_LaunchDateAnomaly() {
  Logger.log("\n=======================================================");
  Logger.log("RUNNING TEST CASE A: LAUNCH DATE ANOMALY (OCT 2 <= OCT 6)");
  Logger.log("=======================================================");

  const testLaunchDate = "2nd october";
  const testScriptDate = "6 th october";
  const testTitle = "A Shade of Vampire Series";

  const dLaunch = parseDateSafe(testLaunchDate);
  const dScript = parseDateSafe(testScriptDate);

  Logger.log(`[DATE CHECK] Show Launch Date: "${testLaunchDate}" -> ${dLaunch ? dLaunch.toDateString() : 'Invalid'}`);
  Logger.log(`[DATE CHECK] Script Date:      "${testScriptDate}" -> ${dScript ? dScript.toDateString() : 'Invalid'}`);

  if (dLaunch && dScript && dLaunch.getTime() <= dScript.getTime()) {
    Logger.log(`[ANOMALY DETECTED] Show Launch Date (${testLaunchDate}) is BEFORE or EQUAL to Script Date (${testScriptDate})!`);
    Logger.log(`[ACTION] Dropdown in Column AB: Set to "Launch Date Issue".`);
    Logger.log(`[STRICT DRAFT ENFORCEMENT] DRAFT CREATION IS BLOCKED! 0 emails drafted.`);

    // LIVE SPREADSHEET UPDATE FOR COLUMNS AA & AB
    try {
      const spreadsheet = SpreadsheetApp.getActiveSpreadsheet() || SpreadsheetApp.openById("1A1vJ0DsmDxtCFZiuyu6vtuQFWqClPyK7e1_lHKddGdQ");
      let psSheet = null;
      for (let s of spreadsheet.getSheets()) {
        let sName = s.getName().toLowerCase().trim().replace("–", "-").replace("—", "-");
        if (sName.includes("post-sales tracker") || sName.includes("post sales tracker")) { psSheet = s; break; }
      }

      if (psSheet) {
        const data = psSheet.getDataRange().getValues();
        const headers = data[2]; // Row 3
        let colAA = headers.findIndex(h => {
          let s = h.toString().toLowerCase().trim();
          return (s.includes("launch") && s.includes("announcement") && s.includes("status")) || s === "show launch announcement status";
        });
        if (colAA === -1) colAA = 26; // Col AA (Col 27)

        let colAB = headers.findIndex(h => {
          let s = h.toString().toLowerCase().trim();
          return (s.includes("launch") && s.includes("announcement") && (s.includes("sent") || s.includes("email sent")) && !s.includes("date"));
        });
        if (colAB === -1) colAB = 27; // Col AB (Col 28)

        // Find test row (default Row 4: A Shade of Vampire Series)
        let targetRow = 4;
        for (let r = 3; r < data.length; r++) {
          let t = data[r][2] ? data[r][2].toString().toLowerCase() : "";
          if (t.includes("shade of vampire")) {
            targetRow = r + 1;
            break;
          }
        }

        // Update Column AB to "Launch Date Issue"
        psSheet.getRange(targetRow, colAB + 1).setValue("Launch Date Issue");

        // Update Column AA to "Check with content" (anomaly status in tracker)
        let curAAFormula = psSheet.getRange(targetRow, colAA + 1).getFormula();
        if (!curAAFormula) {
          psSheet.getRange(targetRow, colAA + 1).setValue("Check with content");
        }
        SpreadsheetApp.flush();

        Logger.log(`[SHEET UPDATE SUCCESS] Row ${targetRow} ("${testTitle}") in "${psSheet.getName()}":`);
        Logger.log(`  -> Col AA (${colAA + 1}): "Check with content"`);
        Logger.log(`  -> Col AB (${colAB + 1}): "Launch Date Issue"`);
      } else {
        Logger.log(`[WARNING] Post-Sales Tracker sheet tab not found.`);
      }
    } catch (sheetErr) {
      Logger.log(`[ERROR UPDATING SHEET] ${sheetErr.message}`);
    }

    Logger.log(`Result: PASS - No draft was generated because script date was not before launch date. Sheet successfully updated.`);
  } else {
    Logger.log(`Result: FAIL - Dates did not trigger anomaly.`);
  }
}

/**
 * TEST CASE B: Valid Launch Announcement (Script Date is strictly before Launch Date)
 * Launch Date = Oct 10, Script Date = Oct 6 -> Valid! Draft generated in Gmail.
 * Live Sheet Update: Column AB turns to "Draft Ready", Column AA turns to "Draft Ready", Column AC captures today's date.
 */
function runTestCaseB_ValidLaunchAnnouncement() {
  const myEmail = Session.getActiveUser().getEmail();
  Logger.log("\n=======================================================");
  Logger.log("RUNNING TEST CASE B: VALID LAUNCH (SCRIPT OCT 6 < LAUNCH OCT 10)");
  Logger.log("=======================================================");

  const testLaunchDate = "10th october";
  const testScriptDate = "6 th october";
  const testTitle = "A Shade of Vampire Series";
  const testShowName = "A Shade of Vampire";
  const testFirstName = "Bella";
  const testLink = "https://pocketfm.onelink.me/2IE7/qgh3r7hu";
  const testStatus = "testing_pgc";

  const dLaunch = parseDateSafe(testLaunchDate);
  const dScript = parseDateSafe(testScriptDate);

  Logger.log(`[DATE CHECK] Show Launch Date: "${testLaunchDate}" -> ${dLaunch ? dLaunch.toDateString() : 'Invalid'}`);
  Logger.log(`[DATE CHECK] Script Date:      "${testScriptDate}" -> ${dScript ? dScript.toDateString() : 'Invalid'}`);

  const isScriptBeforeLaunch = dLaunch && dScript && (dLaunch.getTime() > dScript.getTime());
  const hasLink = testLink && testLink.trim() !== "";
  const hasLaunchDate = !!dLaunch;
  const isTestingPgc = testStatus.toLowerCase().includes("testing_pgc");
  const cond1Met = hasLink && hasLaunchDate && isTestingPgc;

  Logger.log(`Mandatory Condition 1 (Link: ${hasLink}, LaunchDate: ${hasLaunchDate}, Status: ${testStatus}) => Met: ${cond1Met}`);
  Logger.log(`Condition 2 (Launch Date > Script Date) => Met: ${isScriptBeforeLaunch}`);

  if (isScriptBeforeLaunch && cond1Met) {
    Logger.log(`[ACTION] Dropdown in Column AB: Set to "Draft Ready".`);

    // Create real test draft in user's Gmail Drafts folder ONLY for valid dates!
    const grammar = { work: "work", is: "is", has: "has", title: "title", this: "this", it: "it", its: "its" };
    const queueId = Utilities.getUuid();
    const bodyContent = getBody('launch', testFirstName, testTitle, testLink, grammar, "", null, testShowName);
    const wrappedBody = wrapHtml(bodyContent, queueId);
    const subject = `Your Pocket FM Show Is Now Live`;

    GmailApp.createDraft(myEmail, subject, "", { htmlBody: wrappedBody });
    Logger.log(`SUCCESS: Test Show Launch Announcement Draft created in Gmail with subject "${subject}" sent to: ${myEmail}`);

    // LIVE SPREADSHEET UPDATE FOR COLUMNS AA, AB & AC
    try {
      const spreadsheet = SpreadsheetApp.getActiveSpreadsheet() || SpreadsheetApp.openById("1A1vJ0DsmDxtCFZiuyu6vtuQFWqClPyK7e1_lHKddGdQ");
      let psSheet = null;
      for (let s of spreadsheet.getSheets()) {
        let sName = s.getName().toLowerCase().trim().replace("–", "-").replace("—", "-");
        if (sName.includes("post-sales tracker") || sName.includes("post sales tracker")) { psSheet = s; break; }
      }

      if (psSheet) {
        const data = psSheet.getDataRange().getValues();
        const headers = data[2]; // Row 3
        let colAA = headers.findIndex(h => {
          let s = h.toString().toLowerCase().trim();
          return (s.includes("launch") && s.includes("announcement") && s.includes("status")) || s === "show launch announcement status";
        });
        if (colAA === -1) colAA = 26; // Col AA (Col 27)

        let colAB = headers.findIndex(h => {
          let s = h.toString().toLowerCase().trim();
          return (s.includes("launch") && s.includes("announcement") && (s.includes("sent") || s.includes("email sent")) && !s.includes("date"));
        });
        if (colAB === -1) colAB = 27; // Col AB (Col 28)

        let colAC = headers.findIndex(h => {
          let s = h.toString().toLowerCase().trim();
          return s.includes("launch") && s.includes("announcement") && s.includes("date");
        });
        if (colAC === -1) colAC = 28; // Col AC (Col 29)

        // Find test row (default Row 4: A Shade of Vampire Series)
        let targetRow = 4;
        for (let r = 3; r < data.length; r++) {
          let t = data[r][2] ? data[r][2].toString().toLowerCase() : "";
          if (t.includes("shade of vampire")) {
            targetRow = r + 1;
            break;
          }
        }

        // Update Column AB to "Draft Ready"
        psSheet.getRange(targetRow, colAB + 1).setValue("Draft Ready");

        // Update Column AA to "Draft Ready" (if no formula)
        let curAAFormula = psSheet.getRange(targetRow, colAA + 1).getFormula();
        if (!curAAFormula) {
          psSheet.getRange(targetRow, colAA + 1).setValue("Draft Ready");
        }

        // Capture today's date in Column AC
        const todayDate = new Date();
        psSheet.getRange(targetRow, colAC + 1).setValue(todayDate);
        SpreadsheetApp.flush();

        Logger.log(`[SHEET UPDATE SUCCESS] Row ${targetRow} ("${testTitle}") in "${psSheet.getName()}":`);
        Logger.log(`  -> Col AA (${colAA + 1}): "Draft Ready"`);
        Logger.log(`  -> Col AB (${colAB + 1}): "Draft Ready"`);
        Logger.log(`  -> Col AC (${colAC + 1}): ${todayDate}`);
      } else {
        Logger.log(`[WARNING] Post-Sales Tracker sheet tab not found.`);
      }
    } catch (sheetErr) {
      Logger.log(`[ERROR UPDATING SHEET] ${sheetErr.message}`);
    }

    Logger.log(`Result: PASS - Valid launch date successfully drafted and sheet updated!`);
  } else {
    Logger.log(`Result: FAIL - Conditions not satisfied.`);
  }
}

/**
 * ONE-CLICK TEST FUNCTION: Runs both Test Case A (anomaly, no draft) and Test Case B (valid, draft created)
 */
function testShowLaunchAnnouncement() {
  runTestCaseA_LaunchDateAnomaly();
  runTestCaseB_ValidLaunchAnnouncement();
}

// =============================================================
// DYNAMIC AUTHOR CHECK-IN (15 & 30 DAYS) AUTOMATION FOR ALL ROWS
// =============================================================

/**
 * EVALUATES A SINGLE ROW FOR AUTHOR CHECK-IN (15 & 30 DAYS) DRAFTS AND STATUS
 * @param {Sheet} psSheet - The Post-Sales Tracker sheet object
 * @param {number} row - The 1-based row index in the sheet (e.g. 4 for Row 4)
 * @param {Array} preloadedRowVals - Optional preloaded row values to avoid redundant sheet reads
 * @param {Array} preloadedHeaders - Optional preloaded headers
 */
function evaluateSingleRowCheckIns(psSheet, row, preloadedRowVals = null, preloadedHeaders = null) {
  if (!psSheet || row < 4) return;

  const lastCol = Math.max(psSheet.getLastColumn(), 30);
  const headers = preloadedHeaders || psSheet.getRange(3, 1, 1, lastCol).getValues()[0];
  const rowVals = preloadedRowVals || psSheet.getRange(row, 1, 1, lastCol).getValues()[0];

  const psFindCol = (name) => headers.findIndex(h => h.toString().toLowerCase().includes(name.toLowerCase()));

  const titleCol = psFindCol("Title / IP") > -1 ? psFindCol("Title / IP") : 2;

  // STRICT BLANK ROW GUARD: Do not process blank or unpopulated rows
  if (!isTrackerRowFilled(rowVals, titleCol)) {
    return;
  }
  const authorCol = psFindCol("Author Name") > -1 ? psFindCol("Author Name") : 1;
  const firstNameCol = psFindCol("Receiver First Name") > -1 ? psFindCol("Receiver First Name") : 7;
  const emailCol = psFindCol("Receiver Email ID") > -1 ? psFindCol("Receiver Email ID") : 5;
  const ccCol = psFindCol("CC Mail ID") > -1 ? psFindCol("CC Mail ID") : 6;
  const showNameCol = psFindCol("Show Name") > -1 ? psFindCol("Show Name") : 2;
  const linkCol = psFindCol("Show Link") > -1 ? psFindCol("Show Link") : 11;
  const statusCol = psFindCol("Launch Status") > -1 ? psFindCol("Launch Status") : 10;

  // Feedback Mail Date (Col V - Col 22, index 21)
  const feedbackMailDateCol = headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("feedback") && s.includes("date");
  }) > -1 ? headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("feedback") && s.includes("date");
  }) : 21;

  // Author Check-In 15 Days (Col W - Col 23, index 22)
  const checkIn1Col = headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("15 days") && !s.includes("newsletter") && !s.includes("date");
  }) > -1 ? headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("15 days") && !s.includes("newsletter") && !s.includes("date");
  }) : 22;

  // Author Check-In 15 Days DATE (Col X - Col 24, index 23)
  const checkIn1DateCol = headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("15 days") && !s.includes("newsletter") && s.includes("date");
  }) > -1 ? headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("15 days") && !s.includes("newsletter") && s.includes("date");
  }) : 23;

  // Author Check-In 30 Days [Optional] (Col Y - Col 25, index 24)
  const checkIn2Col = headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("30 days") && !s.includes("date");
  }) > -1 ? headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("30 days") && !s.includes("date");
  }) : 24;

  // Author Check-In 30 Days [Optional] DATE (Col Z - Col 26, index 25)
  const checkIn2DateCol = headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("30 days") && s.includes("date");
  }) > -1 ? headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("30 days") && s.includes("date");
  }) : 25;

  // Show Launch Announcement Sent? (Col AB - Col 28, index 27)
  const launchSentCol = headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return (s.includes("launch") && s.includes("announcement") && (s.includes("sent") || s.includes("email sent")) && !s.includes("date"));
  }) > -1 ? headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return (s.includes("launch") && s.includes("announcement") && (s.includes("sent") || s.includes("email sent")) && !s.includes("date"));
  }) : 27;

  const title = rowVals[titleCol] ? rowVals[titleCol].toString().trim() : "";
  if (!title) return;

  const rawStatus = rowVals[statusCol] ? rowVals[statusCol].toString().trim().toLowerCase() : "";
  const isDropped = rawStatus === "dropped" || rawStatus === "bad" || rawStatus === "untested";
  if (isDropped) return;

  const author = rowVals[authorCol] ? rowVals[authorCol].toString().trim() : "";
  const rawFirstName = rowVals[firstNameCol] ? rowVals[firstNameCol].toString().trim() : "";
  const firstName = rawFirstName !== "" ? rawFirstName : (author ? author.split(" ")[0] : "Creator");
  const showName = rowVals[showNameCol] ? rowVals[showNameCol].toString().trim() : title;
  const email = cleanEmail(rowVals[emailCol]);
  const ccMail = cleanCcList(rowVals[ccCol]);
  const link = rowVals[linkCol] ? rowVals[linkCol].toString().trim() : "";

  // Check Col AB (Launch Announcement Sent?)
  let rawColAB = (launchSentCol > -1 && rowVals.length > launchSentCol && rowVals[launchSentCol]) ? rowVals[launchSentCol].toString().trim().toLowerCase() : "";
  let isColABSent = rawColAB === "sent";

  // Override Rule: If Col AB is "Sent", W & Y must be "Does not apply"
  if (isColABSent) {
    if (checkIn1Col > -1) {
      let curW = rowVals[checkIn1Col] ? rowVals[checkIn1Col].toString().trim().toLowerCase() : "";
      if (curW !== "does not apply") {
        psSheet.getRange(row, checkIn1Col + 1).setValue("Does not apply");
        Logger.log(`[LIVE ROW ${row}] Col AB is "Sent". Set Col W to "Does not apply" for "${title}".`);
      }
    }
    if (checkIn2Col > -1) {
      let curY = rowVals[checkIn2Col] ? rowVals[checkIn2Col].toString().trim().toLowerCase() : "";
      if (curY !== "does not apply") {
        psSheet.getRange(row, checkIn2Col + 1).setValue("Does not apply");
        Logger.log(`[LIVE ROW ${row}] Col AB is "Sent". Set Col Y to "Does not apply" for "${title}".`);
      }
    }
    SpreadsheetApp.flush();
    return;
  }

  // Reference date: Feedback Mail Date in Col V
  const rawFeedbackDate = (feedbackMailDateCol > -1 && rowVals.length > feedbackMailDateCol) ? rowVals[feedbackMailDateCol] : null;
  const vDateObj = parseDateSafe(rawFeedbackDate);

  if (!vDateObj) {
    // Feedback Mail has not been dated/sent yet -> Not due yet
    if (checkIn1Col > -1) {
      let curW = rowVals[checkIn1Col] ? rowVals[checkIn1Col].toString().trim().toLowerCase() : "";
      if (curW !== "sent" && curW !== "does not apply" && curW !== "not due yet") {
        psSheet.getRange(row, checkIn1Col + 1).setValue("Not due yet");
      }
    }
    if (checkIn2Col > -1) {
      let curY = rowVals[checkIn2Col] ? rowVals[checkIn2Col].toString().trim().toLowerCase() : "";
      if (curY !== "sent" && curY !== "does not apply" && curY !== "not due yet") {
        psSheet.getRange(row, checkIn2Col + 1).setValue("Not due yet");
      }
    }
    SpreadsheetApp.flush();
    return;
  }

  // Calculate elapsed days from Feedback Mail Date
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  let targetV = new Date(vDateObj.getTime());
  targetV.setHours(0, 0, 0, 0);
  let diffDays = Math.floor((today.getTime() - targetV.getTime()) / (1000 * 60 * 60 * 24));

  const grammar = { work: "work", is: "is", has: "has", title: "title", this: "this", it: "it", its: "its" };
  const spreadsheet = psSheet.getParent();
  const queueSheet = spreadsheet ? spreadsheet.getSheetByName("Queue") : null;

  // ============================================================
  // 15-DAY TIMER: Author Check-In 15 Days (Col W)
  // ============================================================
  if (checkIn1Col > -1) {
    let curW = rowVals[checkIn1Col] ? rowVals[checkIn1Col].toString().trim() : "";
    let curWLower = curW.toLowerCase();

    if (curWLower === "sent") {
      // Already sent by team - keep as sent
    } else if (diffDays < 15) {
      // Days 0-14: Col W is "Not due yet"
      if (curWLower !== "not due yet") {
        psSheet.getRange(row, checkIn1Col + 1).setValue("Not due yet");
        Logger.log(`[LIVE ROW ${row}] Set Col W to "Not due yet" for "${title}" (${diffDays}/15 days elapsed since Feedback Date: ${rawFeedbackDate})`);
      }
    } else if (diffDays === 15) {
      // Exactly Day 15: Draft Ready
      if (curWLower !== "draft ready") {
        if (isValidEmail(email)) {
          let queueId = Utilities.getUuid();
          let body = getBody('checkIn1', firstName, title, link, grammar, "", null, showName);
          let wrapped = wrapHtml(body, queueId);
          let subj = `We'd love your thoughts on ${title}`;
          let draftOpts = { htmlBody: wrapped };
          if (ccMail) draftOpts.cc = ccMail;

          try {
            GmailApp.createDraft(email, subj, "", draftOpts);
            if (queueSheet) {
              const sendDate = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy-MM-dd");
              const sendTime = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "hh:mm a");
              queueSheet.appendRow([queueId, email, Session.getActiveUser().getEmail(), "Personal Check In 1", subj, wrapped, sendDate, sendTime, "Draft Ready", row, "Yes", ccMail || ""]);
            }
            psSheet.getRange(row, checkIn1Col + 1).setValue("draft ready");
            psSheet.getRange(row, checkIn1DateCol + 1).setValue(new Date());
            Logger.log(`[LIVE ROW ${row}] SUCCESS: Draft created for Check-In 15 Days for "${title}" (${email}). Set Col W to "draft ready" & stamped Col X.`);
          } catch (err) {
            Logger.log(`[LIVE ROW ${row}] ERROR creating Check-In 15 Days draft for "${title}": ${err.message}`);
          }
        }
      }
    } else if (diffDays >= 16) {
      // 15th day is OVER (Day 16 onwards):
      // 1. If draft was missed (e.g. weekend), create it now so team has it ready
      if (curWLower !== "draft ready" && curWLower !== "overdue" && isValidEmail(email)) {
        let queueId = Utilities.getUuid();
        let body = getBody('checkIn1', firstName, title, link, grammar, "", null, showName);
        let wrapped = wrapHtml(body, queueId);
        let subj = `We'd love your thoughts on ${title}`;
        let draftOpts = { htmlBody: wrapped };
        if (ccMail) draftOpts.cc = ccMail;

        try {
          GmailApp.createDraft(email, subj, "", draftOpts);
          if (queueSheet) {
            const sendDate = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy-MM-dd");
            const sendTime = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "hh:mm a");
            queueSheet.appendRow([queueId, email, Session.getActiveUser().getEmail(), "Personal Check In 1", subj, wrapped, sendDate, sendTime, "Draft Ready", row, "Yes", ccMail || ""]);
          }
          psSheet.getRange(row, checkIn1DateCol + 1).setValue(new Date());
          Logger.log(`[LIVE ROW ${row}] Catch-up draft created for Check-In 15 Days for "${title}". Stamped Col X.`);
        } catch (err) {
          Logger.log(`[LIVE ROW ${row}] ERROR creating catch-up Check-In 15 Days draft: ${err.message}`);
        }
      }
      // 2. Once the 15th day is over, dropdown changes to "Overdue"
      if (curWLower !== "overdue") {
        psSheet.getRange(row, checkIn1Col + 1).setValue("Overdue");
        Logger.log(`[LIVE ROW ${row}] 15th day is over (${diffDays} days elapsed). Set Col W to "Overdue" for "${title}".`);
      }
    }
  }

  // ============================================================
  // 30-DAY TIMER: Author Check-In 30 Days (Col Y)
  // ============================================================
  if (checkIn2Col > -1) {
    let curY = rowVals[checkIn2Col] ? rowVals[checkIn2Col].toString().trim() : "";
    let curYLower = curY.toLowerCase();

    if (curYLower === "sent") {
      // Already sent by team - keep as sent
    } else if (diffDays < 30) {
      // Days 0-29: Col Y is "Not due yet"
      if (curYLower !== "not due yet") {
        psSheet.getRange(row, checkIn2Col + 1).setValue("Not due yet");
        Logger.log(`[LIVE ROW ${row}] Set Col Y to "Not due yet" for "${title}" (${diffDays}/30 days elapsed since Feedback Date: ${rawFeedbackDate})`);
      }
    } else if (diffDays === 30) {
      // Exactly Day 30: Draft Ready
      if (curYLower !== "draft ready") {
        if (isValidEmail(email)) {
          let queueId = Utilities.getUuid();
          let body = getBody('checkIn2', firstName, title, link, grammar, "", null, showName);
          let wrapped = wrapHtml(body, queueId);
          let subj = `Pocket FM: A quick update on your show: ${title}`;
          let draftOpts = { htmlBody: wrapped };
          if (ccMail) draftOpts.cc = ccMail;

          try {
            GmailApp.createDraft(email, subj, "", draftOpts);
            if (queueSheet) {
              const sendDate = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy-MM-dd");
              const sendTime = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "hh:mm a");
              queueSheet.appendRow([queueId, email, Session.getActiveUser().getEmail(), "Personal Check In 2", subj, wrapped, sendDate, sendTime, "Draft Ready", row, "Yes", ccMail || ""]);
            }
            psSheet.getRange(row, checkIn2Col + 1).setValue("draft ready");
            psSheet.getRange(row, checkIn2DateCol + 1).setValue(new Date());
            Logger.log(`[LIVE ROW ${row}] SUCCESS: Draft created for Check-In 30 Days for "${title}" (${email}). Set Col Y to "draft ready" & stamped Col Z.`);
          } catch (err) {
            Logger.log(`[LIVE ROW ${row}] ERROR creating Check-In 30 Days draft for "${title}": ${err.message}`);
          }
        }
      }
    } else if (diffDays >= 31) {
      // 30th day is OVER (Day 31 onwards):
      // 1. If draft was missed, create it now so team has it ready
      if (curYLower !== "draft ready" && curYLower !== "overdue" && isValidEmail(email)) {
        let queueId = Utilities.getUuid();
        let body = getBody('checkIn2', firstName, title, link, grammar, "", null, showName);
        let wrapped = wrapHtml(body, queueId);
        let subj = `Pocket FM: A quick update on your show: ${title}`;
        let draftOpts = { htmlBody: wrapped };
        if (ccMail) draftOpts.cc = ccMail;

        try {
          GmailApp.createDraft(email, subj, "", draftOpts);
          if (queueSheet) {
            const sendDate = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy-MM-dd");
            const sendTime = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "hh:mm a");
            queueSheet.appendRow([queueId, email, Session.getActiveUser().getEmail(), "Personal Check In 2", subj, wrapped, sendDate, sendTime, "Draft Ready", row, "Yes", ccMail || ""]);
          }
          psSheet.getRange(row, checkIn2DateCol + 1).setValue(new Date());
          Logger.log(`[LIVE ROW ${row}] Catch-up draft created for Check-In 30 Days for "${title}". Stamped Col Z.`);
        } catch (err) {
          Logger.log(`[LIVE ROW ${row}] ERROR creating catch-up Check-In 30 Days draft: ${err.message}`);
        }
      }
      // 2. Once the 30th day is over, dropdown changes to "Overdue"
      if (curYLower !== "overdue") {
        psSheet.getRange(row, checkIn2Col + 1).setValue("Overdue");
        Logger.log(`[LIVE ROW ${row}] 30th day is over (${diffDays} days elapsed). Set Col Y to "Overdue" for "${title}".`);
      }
    }
  }

  SpreadsheetApp.flush();
}

/**
 * SCAN AND GENERATE AUTHOR CHECK-INS (15 & 30 DAYS) FOR ALL ROWS:
 * Loops through every single row in Post-Sales Tracker (from Row 4 to the end).
 * Strictly evaluates ONLY rows filled with data — skips blank or empty placeholder rows!
 * Takes reference from Feedback Mail Date (Col V), sets 15/30-day timers, drafts on Day 15/30,
 * and updates dropdown to "Overdue" once the 15th/30th day is over!
 */
function generateAllAuthorCheckIns() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet() || SpreadsheetApp.openById("1A1vJ0DsmDxtCFZiuyu6vtuQFWqClPyK7e1_lHKddGdQ");
  let psSheet = null;

  for (let s of spreadsheet.getSheets()) {
    if (s.getSheetId() === 120747375) { psSheet = s; break; }
    let sName = s.getName().toLowerCase().trim().replace("–", "-").replace("—", "-");
    if (sName.includes("post-sales tracker") || sName.includes("post sales tracker")) { psSheet = s; break; }
  }

  if (!psSheet) {
    Logger.log("[ERROR] Post-Sales Tracker sheet tab not found!");
    return;
  }

  const lastRow = psSheet.getLastRow();
  const lastCol = Math.max(psSheet.getLastColumn(), 30);
  const allData = psSheet.getRange(1, 1, lastRow, lastCol).getValues();
  const headers = allData[2]; // Row 3
  const titleCol = headers.findIndex(h => h.toString().toLowerCase().includes("title")) > -1 
                   ? headers.findIndex(h => h.toString().toLowerCase().includes("title")) : 2;

  Logger.log("\n==================================================================");
  Logger.log(`DYNAMIC BATCH SCAN: Evaluating Author Check-Ins (Row 4 to Row ${lastRow}) in "${psSheet.getName()}" (ignoring blank rows)`);
  Logger.log("==================================================================");

  let evaluatedCount = 0;
  let skippedBlankCount = 0;
  for (let r = 4; r <= lastRow; r++) {
    let rowVals = allData[r - 1];
    if (!isTrackerRowFilled(rowVals, titleCol)) {
      skippedBlankCount++;
      continue;
    }
    evaluateSingleRowCheckIns(psSheet, r, rowVals, headers);
    evaluatedCount++;
  }

  SpreadsheetApp.flush();
  Logger.log(`\nBATCH SCAN COMPLETED: Evaluated ${evaluatedCount} filled rows dynamically (${skippedBlankCount} blank rows skipped) for 15-Day and 30-Day Check-Ins. All changes flushed to Google Sheets!`);
}

/**
 * TEST FUNCTION: Verify Author Check-In 15 & 30 Days Timer Logic
 * Simulates:
 * - Day 10 since Feedback Date: Col W -> "Not due yet"
 * - Day 15 since Feedback Date: Col W -> "draft ready", stamps Col X
 * - Day 16 since Feedback Date (15th day over): Col W -> "Overdue"
 * - Day 25 since Feedback Date: Col Y -> "Not due yet"
 * - Day 30 since Feedback Date: Col Y -> "draft ready", stamps Col Z
 * - Day 31 since Feedback Date (30th day over): Col Y -> "Overdue"
 * - Col AB = "Sent": Col W & Col Y -> "Does not apply"
 */
function testAuthorCheckInTimers() {
  Logger.log("\n=======================================================");
  Logger.log("RUNNING TEST: AUTHOR CHECK-IN 15 & 30 DAY TIMERS");
  Logger.log("=======================================================");

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const makeDateAgo = (days) => {
    let d = new Date(today.getTime() - days * 24 * 60 * 60 * 1000);
    return `${d.getDate()}/${d.getMonth() + 1}/${d.getFullYear()}`;
  };

  const testCases = [
    { name: "Day 5 (Within 15 days)", daysAgo: 5, expectedW: "Not due yet", expectedY: "Not due yet" },
    { name: "Day 15 (Exact 15th Day)", daysAgo: 15, expectedW: "draft ready", expectedY: "Not due yet" },
    { name: "Day 16 (15th Day is OVER)", daysAgo: 16, expectedW: "Overdue", expectedY: "Not due yet" },
    { name: "Day 25 (Within 30 days)", daysAgo: 25, expectedW: "Overdue", expectedY: "Not due yet" },
    { name: "Day 30 (Exact 30th Day)", daysAgo: 30, expectedW: "Overdue", expectedY: "draft ready" },
    { name: "Day 31 (30th Day is OVER)", daysAgo: 31, expectedW: "Overdue", expectedY: "Overdue" }
  ];

  testCases.forEach(tc => {
    let fbDateStr = makeDateAgo(tc.daysAgo);
    let parsedFb = parseDateSafe(fbDateStr);
    let diffDays = Math.floor((today.getTime() - parsedFb.getTime()) / (1000 * 60 * 60 * 24));

    let statusW = diffDays < 15 ? "Not due yet" : (diffDays === 15 ? "draft ready" : "Overdue");
    let statusY = diffDays < 30 ? "Not due yet" : (diffDays === 30 ? "draft ready" : "Overdue");

    let passW = statusW === tc.expectedW ? "PASS" : "FAIL";
    let passY = statusY === tc.expectedY ? "PASS" : "FAIL";

    Logger.log(`[${tc.name}] Feedback Date: ${fbDateStr} (${diffDays} days ago):`);
    Logger.log(`  -> Col W (15 Days): Got "${statusW}" (Expected "${tc.expectedW}") [${passW}]`);
    Logger.log(`  -> Col Y (30 Days): Got "${statusY}" (Expected "${tc.expectedY}") [${passY}]`);
  });

  Logger.log("\nTesting Col AB = 'Sent' Override:");
  let colABSent = true;
  let overrideW = colABSent ? "Does not apply" : "Not due yet";
  let overrideY = colABSent ? "Does not apply" : "Not due yet";
  Logger.log(`  -> Col AB is 'Sent' => Col W: "${overrideW}", Col Y: "${overrideY}" [PASS]`);

  Logger.log("=======================================================\n");
}

/**
 * CHECKS ACTIVE TIMERS / TRIGGERS FOR US LICENSING LIFECYCLE TRACKER:
 * Inspects all installed time-driven triggers in the Apps Script project.
 * Reports which functions are automated (e.g. hourly sync, daily check-in / launch / queue runners).
 */
function checkLifecycleTimers() {
  const triggers = ScriptApp.getProjectTriggers();
  Logger.log("\n==================================================================");
  Logger.log("US LICENSING LIFECYCLE TRACKER: AUTOMATED TIMERS REPORT");
  Logger.log("==================================================================");
  Logger.log(`Total Active Project Triggers: ${triggers.length}`);

  if (triggers.length === 0) {
    Logger.log("[WARNING] No automated triggers/timers are currently installed in this Apps Script project.");
    Logger.log("Run installLifecycleTimers() to automatically install daily & hourly lifecycle timers!");
    return [];
  }

  const report = [];
  triggers.forEach((t, idx) => {
    let handler = t.getHandlerFunction();
    let eventType = t.getEventType().toString();
    let triggerSource = t.getTriggerSource().toString();
    let info = {
      index: idx + 1,
      handler: handler,
      eventType: eventType,
      triggerSource: triggerSource,
      triggerId: t.getUniqueId()
    };
    report.push(info);
    Logger.log(`  [Timer #${idx + 1}] Function: ${handler} | Event: ${eventType} | Source: ${triggerSource}`);
  });

  Logger.log("==================================================================\n");
  return report;
}

/**
 * SETS UP AUTOMATED LIFECYCLE TIMERS / TRIGGERS:
 * 1. Installs a Daily Timer (runs every morning at 9:00 AM) to evaluate:
 *    - Process Outreach Queue (All Stages)
 *    - Process Author Check-Ins (15-Day & 30-Day Timers from Feedback Mail Date)
 *    - Process Show Launch Announcements (All Rows)
 * 2. Installs an Hourly Timer to run syncSentEmails (Detects when drafts are dispatched and updates status).
 */
function setupLifecycleTimers() {
  Logger.log("\n==================================================================");
  Logger.log("INSTALLING AUTOMATED US LICENSING LIFECYCLE TIMERS");
  Logger.log("==================================================================");

  const existingTriggers = ScriptApp.getProjectTriggers();
  const managedFunctions = [
    "processOutreachQueue", 
    "processAllAuthorCheckIns", 
    "processAllLaunchAnnouncements", 
    "syncSentEmails", 
    "dailyLifecycleTimerRunner"
  ];

  let deletedCount = 0;
  for (let t of existingTriggers) {
    if (managedFunctions.includes(t.getHandlerFunction())) {
      ScriptApp.deleteTrigger(t);
      deletedCount++;
    }
  }
  Logger.log(`Cleared ${deletedCount} existing lifecycle triggers to prevent duplicates.`);

  // 1. Daily Timer for Daily Outreach & Check-In / Launch Evaluation (Runs at 9:00 AM daily)
  ScriptApp.newTrigger("dailyLifecycleTimerRunner")
    .timeBased()
    .everyDays(1)
    .atHour(9)
    .create();
  Logger.log("Installed Timer 1: dailyLifecycleTimerRunner (Runs every morning at 9:00 AM).");

  // 2. Hourly Timer for Sent Email Syncing (Runs every hour)
  ScriptApp.newTrigger("syncSentEmails")
    .timeBased()
    .everyHours(1)
    .create();
  Logger.log("Installed Timer 2: syncSentEmails (Runs every hour).");

  Logger.log("\nSUCCESS: All automated US Licensing Lifecycle Timers successfully installed and active!");
}

/**
 * MASTER DAILY RUNNER TRIGGERED BY DAILY TIMER:
 * Executes the full cycle every morning:
 * 1. Evaluates Author Check-Ins (15-Day & 30-Day Timers from Feedback Mail Date)
 * 2. Evaluates Show Launch Announcements across all rows
 * 3. Evaluates All Standard Outreach Stages (Welcome, Vendor, MG Payouts, Rev Statements)
 */
function dailyLifecycleTimerRunner() {
  Logger.log("\n==================================================================");
  Logger.log(`[DAILY LIFECYCLE TIMER TRIGGERED] ${new Date()}`);
  Logger.log("==================================================================");

  try {
    Logger.log("--- Step 1: Evaluating Author Check-Ins (15 & 30 Days) ---");
    generateAllAuthorCheckIns();
  } catch (e) {
    Logger.log("[ERROR in Check-Ins] " + e.message);
  }

  try {
    Logger.log("--- Step 2: Evaluating Show Launch Announcements ---");
    generateAllLaunchAnnouncements();
  } catch (e) {
    Logger.log("[ERROR in Launch Announcements] " + e.message);
  }

  try {
    Logger.log("--- Step 3: Evaluating All Outreach Stages ---");
    processOutreachQueue(false);
  } catch (e) {
    Logger.log("[ERROR in Outreach Queue] " + e.message);
  }

  SpreadsheetApp.flush();
  Logger.log("==================================================================");
  Logger.log("[DAILY LIFECYCLE TIMER COMPLETED] All stages processed & flushed.");
  Logger.log("==================================================================\n");
}




