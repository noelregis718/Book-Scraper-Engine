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
      .addItem("🚀 Launch CMS Scraper Popup", "openCmsScraperDialog")
      .addItem("▶️ Run Background Sync All Shows", "syncAllCmsShows")
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
 * Opens the interactive CMS Scraper Modal Popup inside Google Sheets
 */
function openCmsScraperDialog() {
  try {
    const htmlOutput = HtmlService.createHtmlOutput(buildCmsScraperDialogHtml())
      .setWidth(780)
      .setHeight(680);
    SpreadsheetApp.getUi().showModalDialog(htmlOutput, "Pocket FM CMS Live Scraper");
  } catch (e) {
    Logger.log("Modal dialog is available when run inside Google Sheets UI: " + e);
  }
}

/**
 * Generates the complete HTML for the interactive CMS Scraper Modal & Web App
 * @returns {string} HTML string
 */
function buildCmsScraperDialogHtml() {
  return `<!DOCTYPE html>
<html>
<head>
  <base target="_blank">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: #f7f9fa;
      color: #202124;
      padding: 20px;
    }
    .header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 2px solid #7a0000;
      padding-bottom: 12px;
      margin-bottom: 16px;
    }
    .header h2 {
      font-size: 19px;
      color: #7a0000;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .badge {
      font-size: 12px;
      padding: 4px 10px;
      border-radius: 12px;
      font-weight: 600;
    }
    .badge-success { background: #e6f4ea; color: #137333; }
    .badge-warning { background: #fef7e0; color: #b06000; }
    .badge-error { background: #fce8e6; color: #c5221f; }
    
    .card {
      background: #ffffff;
      border: 1px solid #dadce0;
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 16px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .card h3 {
      font-size: 14px;
      color: #3c4043;
      margin-bottom: 10px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    
    .btn {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: #7a0000;
      color: #ffffff;
      border: none;
      border-radius: 6px;
      padding: 9px 16px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.2s;
      text-decoration: none;
    }
    .btn:hover { background: #5c0000; }
    .btn:disabled { background: #bdc1c6; cursor: not-allowed; }
    .btn-secondary {
      background: #f1f3f4;
      color: #3c4043;
      border: 1px solid #dadce0;
    }
    .btn-secondary:hover { background: #e8eaed; }
    
    .token-input {
      width: 100%;
      padding: 8px 12px;
      border: 1px solid #dadce0;
      border-radius: 6px;
      font-size: 12px;
      font-family: monospace;
      margin: 8px 0;
    }
    
    .progress-container {
      background: #e8eaed;
      border-radius: 6px;
      height: 12px;
      overflow: hidden;
      margin: 12px 0 6px 0;
    }
    .progress-bar {
      background: #7a0000;
      height: 100%;
      width: 0%;
      transition: width 0.3s ease;
    }
    .progress-stats {
      display: flex;
      justify-content: space-between;
      font-size: 12px;
      color: #5f6368;
    }
    
    .live-card {
      background: #fafafa;
      border-left: 4px solid #7a0000;
      padding: 10px 14px;
      border-radius: 4px;
      margin-top: 10px;
      font-size: 13px;
    }
    .metric-pill {
      display: inline-block;
      background: #eef3fc;
      color: #1a73e8;
      padding: 2px 8px;
      border-radius: 4px;
      font-weight: 600;
      margin: 2px 4px 2px 0;
      font-size: 12px;
    }
    
    .log-box {
      background: #1e1e1e;
      color: #d4d4d4;
      border-radius: 6px;
      padding: 12px;
      height: 140px;
      overflow-y: auto;
      font-family: Consolas, Monaco, monospace;
      font-size: 11px;
      line-height: 1.5;
    }
    .log-success { color: #81c995; }
    .log-warn { color: #fdd663; }
    .log-error { color: #f28b82; }
  </style>
</head>
<body>

  <div class="header">
    <h2>📻 Pocket FM CMS Live Scraper</h2>
    <span id="authBadge" class="badge badge-warning">Checking Session...</span>
  </div>

  <!-- STEP 1: AUTHENTICATION -->
  <div class="card">
    <h3>Step 1: Open CMS & Log In Manually</h3>
    <p style="font-size: 13px; color: #5f6368; margin-bottom: 12px; line-height: 1.5;">
      Pocket FM CMS uses JumpCloud SSO with 2FA. Click below to open CMS in your browser, enter your credentials, and complete your login.
    </p>
    <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
      <button class="btn btn-secondary" onclick="openCmsWindow()">
        🌐 1. Open Pocket FM CMS in New Window
      </button>
      <button class="btn btn-secondary" onclick="toggleTokenBox()" style="font-size: 12px;">
        🔑 Optional: Paste Session Token
      </button>
    </div>
    
    <div id="tokenBox" style="display: none; margin-top: 10px; background: #fdf2f2; border: 1px solid #fad2cf; border-radius: 6px; padding: 12px;">
      <div style="font-weight: 600; font-size: 12px; color: #b31412; margin-bottom: 4px;">
        Optional: Paste Session Cookie or Bearer Token:
      </div>
      <input type="text" id="tokenInput" class="token-input" placeholder="Paste session cookie or Bearer token here..." style="margin: 6px 0 8px 0;">
      <div style="display: flex; gap: 8px;">
        <button class="btn" style="padding: 6px 14px; font-size: 12px;" onclick="saveToken()">💾 Save Token</button>
        <button class="btn btn-secondary" style="padding: 6px 14px; font-size: 12px;" onclick="toggleTokenBox()">Cancel</button>
      </div>
    </div>
  </div>

  <!-- STEP 2: SCRAPER CONTROL -->
  <div class="card">
    <div style="display: flex; justify-content: space-between; align-items: center;">
      <h3>Step 2: Send Confirmation & Start Live Scraping</h3>
      <span id="showCountBadge" style="font-size: 12px; color: #5f6368; font-weight: 600;">Loading shows...</span>
    </div>

    <div style="font-size: 12px; color: #70757a; margin-top: 4px;">
      Target Tab: <b style="color: #7a0000;" id="sheetTargetName">Argus Show Data</b>
    </div>

    <p style="font-size: 13px; color: #5f6368; margin: 10px 0 8px 0;">
      Once you are signed into Pocket FM CMS in your browser, click below to confirm and scrape:
    </p>

    <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
      <button id="startBtn" class="btn" style="padding: 10px 20px; font-size: 14px;" onclick="startScraping()">
        🚀 Start Live Scraping All Shows
      </button>
      <a id="bookmarkletLink" class="btn btn-secondary" href="javascript:void(0)" style="font-size: 12px; cursor: move;" title="Drag this button to your browser Bookmarks Bar">
        ⭐ Drag to Bookmarks: Sync CMS Shows
      </a>
    </div>

    <div style="margin-top: 10px; background: #eef3fc; border-left: 3px solid #1a73e8; padding: 8px 12px; border-radius: 4px; font-size: 12px; color: #174ea6;">
      💡 <b>Alternative (Zero Setup):</b> Double-click <code>run_cms_scraper.bat</code> in your project folder. It launches Chrome with your credentials, prompts for 2FA, and starts scraping as soon as you press Enter!
    </div>

    <div class="progress-container">
      <div id="pBar" class="progress-bar"></div>
    </div>
    <div class="progress-stats">
      <span id="progressLabel">Waiting to start...</span>
      <span id="progressPct">0%</span>
    </div>

    <div id="liveCard" class="live-card" style="display: none;">
      <div style="font-weight: 700; color: #202124;" id="liveTitle">-</div>
      <div style="margin-top: 4px;">
        <span class="metric-pill" id="pillPlays">Plays: -</span>
        <span class="metric-pill" id="pillDur">Dur: -</span>
        <span class="metric-pill" id="pillRatings">Ratings: -</span>
        <span class="metric-pill" id="pillReviews">Reviews: -</span>
        <span class="metric-pill" id="pillComments">Comments: -</span>
      </div>
    </div>
  </div>

  <!-- STEP 3: LIVE LOGS -->
  <div class="card" style="margin-bottom: 0;">
    <h3>Live Execution Feed</h3>
    <div id="logBox" class="log-box">
      <div>[INIT] Initializing Pocket FM CMS Scraper...</div>
    </div>
  </div>

  <script>
    let showList = [];
    let currentIndex = 0;
    let isRunning = false;
    let successCount = 0;
    let failCount = 0;
    let hasAuthToken = false;

    window.onload = function() {
      addLog("[INIT] Connecting to Google Sheet...");
      google.script.run
        .withSuccessHandler(onInitSuccess)
        .withFailureHandler(onInitError)
        .getCmsInitData();
    };

    function onInitSuccess(data) {
      showList = data.shows || [];
      document.getElementById("showCountBadge").innerText = showList.length + " shows found in sheet";
      if (data.sheetName) {
        document.getElementById("sheetTargetName").innerText = data.sheetName;
      }
      
      hasAuthToken = !!data.hasToken;
      const badge = document.getElementById("authBadge");
      if (hasAuthToken) {
        badge.innerText = "Session Token Configured";
        badge.className = "badge badge-success";
        addLog("[AUTH] CMS session token is active and ready.");
      } else {
        badge.innerText = "Token Missing / Expired";
        badge.className = "badge badge-warning";
        addLog("[NOTICE] No session token configured. You can log into CMS in browser and run the scraper.", "warn");
      }
      updateBookmarklet();
      addLog("[READY] Ready to scrape " + showList.length + " shows.");
    }

    function updateBookmarklet() {
      const showIds = (showList || []).map(function(s) { return s.showId; });
      const webhookEndpoint = "https://script.google.com/a/macros/pocketfm.com/s/AKfycbzZqhEd3T03yt6u_G-M51QcjYzndd9tkfJNPS8r9eXr8vFA6owv5qt_UzymosThbdkb/exec";
      const code = "javascript:(async function(){" +
        "if(!location.hostname.includes('pocketfm.com')){alert('Please click this bookmark while on cms.pocketfm.com!');return;}" +
        "const shows=" + JSON.stringify(showIds) + ";" +
        "const box=document.createElement('div');" +
        "box.style='position:fixed;top:15px;right:15px;background:#7a0000;color:#fff;padding:16px 20px;border-radius:8px;z-index:9999999;font-family:sans-serif;box-shadow:0 4px 16px rgba(0,0,0,0.4);min-width:320px;max-width:400px;';" +
        "box.innerHTML='<div style=\"font-weight:bold;font-size:14px;\">📻 Pocket FM CMS Live Scraper</div><div id=\"syncMsg\" style=\"margin-top:6px;font-size:12px;\">Starting live scrape...</div>';" +
        "document.body.appendChild(box);" +
        "const msg=document.getElementById('syncMsg');" +
        "const results=[];" +
        "for(let i=0;i<shows.length;i++){" +
        "const sid=shows[i];" +
        "msg.innerText='Scraping show '+(i+1)+'/'+shows.length+' ('+sid.substring(0,8)+')...';" +
        "try{" +
        "const resp=await fetch('https://api.cms.pocketfm.com/content_api/book.published_shows?show_id='+sid);" +
        "const d=await resp.json();" +
        "const b=(d.result&&d.result.books?d.result.books[0]:(d.result||d.data))||{};" +
        "const sName=b.title||b.name||b.show_name||('Show '+sid.substring(0,8));" +
        "const pl=b.plays||b.play_count||0;" +
        "const dur=b.duration||b.hours||0;" +
        "msg.innerHTML='<b>'+sName+'</b><br>Plays: '+pl+' | Dur: '+dur+' hrs ('+(i+1)+'/'+shows.length+')';" +
        "results.push({showId:sid,showName:sName,plays:pl,duration:dur,ratings:b.ratings||b.rating||0,reviews:b.reviews||b.review_count||0,comments:b.comments||b.comment_count||0});" +
        "}catch(e){results.push({showId:sid,showName:'',plays:0,duration:0,ratings:0,reviews:0,comments:0});}" +
        "await new Promise(function(r){setTimeout(r,400);});" +
        "}" +
        "msg.innerText='Syncing results to Argus Show Data tab...';" +
        "try{" +
        "await fetch('" + webhookEndpoint + "',{method:'POST',mode:'no-cors',headers:{'Content-Type':'application/json'},body:JSON.stringify({secret:'pocketfm_cms_sync_2026',shows:results})});" +
        "msg.innerText='✅ Done! Successfully scraped and synced '+results.length+' shows to Google Sheets!';" +
        "}catch(err){" +
        "msg.innerText='Scraped '+results.length+' shows! Webhook status: '+err;" +
        "}" +
        "setTimeout(function(){if(box.parentNode)box.parentNode.removeChild(box);},6000);" +
        "})();";
      const btn = document.getElementById("bookmarkletLink");
      if(btn) btn.setAttribute("href", code);
    }

    function onInitError(err) {
      addLog("[ERROR] Failed to load sheet data: " + err, "error");
    }

    function openCmsWindow() {
      window.open("https://cms.pocketfm.com/shows/audiobooks?tab=published", "_blank");
      addLog("[BROWSER] Opened Pocket FM CMS in popup window. Log in via JumpCloud SSO.");
    }

    function toggleTokenBox() {
      const box = document.getElementById("tokenBox");
      box.style.display = box.style.display === "none" ? "block" : "none";
      if (box.style.display === "block") {
        document.getElementById("tokenInput").focus();
      }
    }

    function saveToken() {
      const val = document.getElementById("tokenInput").value.trim();
      if (!val) {
        alert("Please paste your session cookie or token before saving.");
        return;
      }
      google.script.run
        .withSuccessHandler(function() {
          hasAuthToken = true;
          const badge = document.getElementById("authBadge");
          badge.innerText = "Session Token Configured";
          badge.className = "badge badge-success";
          toggleTokenBox();
          addLog("[AUTH] Session token updated successfully! Ready to scrape.", "success");
        })
        .saveCmsTokenAjax(val);
    }

    function startScraping() {
      if (isRunning || showList.length === 0) return;

      if (!hasAuthToken) {
        addLog("[NOTICE] No cloud session token saved. Attempting direct sync or use bookmarklet/runner.", "warn");
      }

      isRunning = true;
      currentIndex = 0;
      successCount = 0;
      failCount = 0;

      document.getElementById("startBtn").disabled = true;
      document.getElementById("liveCard").style.display = "block";
      addLog("[START] Starting live scraping for " + showList.length + " shows into " + document.getElementById("sheetTargetName").innerText + "...");

      scrapeNextShow();
    }

    function scrapeNextShow() {
      if (currentIndex >= showList.length) {
        finishScraping();
        return;
      }

      const item = showList[currentIndex];
      const shortId = item.showId.substring(0, 10);
      updateProgress(currentIndex, showList.length, "Scraping show " + (currentIndex + 1) + " of " + showList.length + " (" + shortId + "...)");

      google.script.run
        .withSuccessHandler(function(metrics) {
          if (metrics.success) {
            successCount++;
            document.getElementById("liveTitle").innerText = metrics.showName || ("Show " + shortId);
            document.getElementById("pillPlays").innerText = "Plays: " + (metrics.plays || 0);
            document.getElementById("pillDur").innerText = "Dur: " + (metrics.duration || 0) + " hrs";
            document.getElementById("pillRatings").innerText = "Ratings: " + (metrics.ratings || 0);
            document.getElementById("pillReviews").innerText = "Reviews: " + (metrics.reviews || 0);
            document.getElementById("pillComments").innerText = "Comments: " + (metrics.comments || 0);

            addLog("[" + (currentIndex + 1) + "/" + showList.length + "] ✅ " + (metrics.showName || shortId) + " | Plays: " + metrics.plays + " | Dur: " + metrics.duration, "success");
          } else {
            failCount++;
            addLog("[" + (currentIndex + 1) + "/" + showList.length + "] ⚠️ " + shortId + ": " + (metrics.error || "Failed to parse"), "error");
          }
          currentIndex++;
          scrapeNextShow();
        })
        .withFailureHandler(function(err) {
          failCount++;
          addLog("[" + (currentIndex + 1) + "/" + showList.length + "] ❌ Error: " + err, "error");
          currentIndex++;
          scrapeNextShow();
        })
        .scrapeSingleShowAjax(item.showId);
    }

    function updateProgress(curr, total, label) {
      const pct = Math.round((curr / total) * 100);
      document.getElementById("pBar").style.width = pct + "%";
      document.getElementById("progressPct").innerText = pct + "%";
      document.getElementById("progressLabel").innerText = label;
    }

    function finishScraping() {
      isRunning = false;
      document.getElementById("startBtn").disabled = false;
      updateProgress(showList.length, showList.length, "All shows scraped!");
      addLog("=============================================");
      addLog("🎉 SCRAPING COMPLETE! Updated: " + successCount + " | Failed: " + failCount, "success");
      addLog("All data has been saved live into your Google Sheet tab!", "success");
    }

    function addLog(msg, type) {
      const box = document.getElementById("logBox");
      const div = document.createElement("div");
      if (type === "success") div.className = "log-success";
      if (type === "warn") div.className = "log-warn";
      if (type === "error") div.className = "log-error";
      div.innerText = msg;
      box.appendChild(div);
      box.scrollTop = box.scrollHeight;
    }
  </script>
</body>
</html>`;
}

/**
 * UI Prompt allowing users to securely enter or update their CMS session cookie / token
 */
function promptSetCmsAuthToken() {
  let ui = null;
  try {
    ui = SpreadsheetApp.getUi();
  } catch (e) {
    Logger.log("UI prompt is only available when executed from a Google Spreadsheet container. In standalone mode, use setCmsAuthToken('YOUR_TOKEN') in CmsConfig.gs.");
    return;
  }

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
  const token = getCmsAuthToken();

  if (token) {
    safeAlert(
      "CMS Token Status: Active",
      `A session token is currently saved in Script Properties.\n\n• Token Preview: ${token.substring(0, 20)}...\n• Length: ${token.length} characters\n\nIf sync returns 401/redirect errors, your session may have expired—simply click 'Set / Update CMS Session Token' to update.`
    );
  } else {
    safeAlert(
      "CMS Token Status: Not Configured",
      "No CMS session token is currently stored.\n\nPlease click 'Set / Update CMS Session Token' to enter your session cookie before syncing directly from Google Sheets."
    );
  }
}

/**
 * Displays Webhook integration details for external scrapers (e.g. Python Playwright)
 */
function showWebhookDetailsDialog() {
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

  safeAlert("Pocket FM CMS Webhook Endpoint", msg);
}

