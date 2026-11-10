/**
 * ============================================================================
 * POCKET FM - AUTOMATED REVENUE STATEMENT GENERATOR
 * File: RevenueStatementGenerator.gs
 * ============================================================================
 * 
 * Automatically generates branded, confidential revenue statements for contracted
 * authors directly from Google Sheets data, hosts the document on Google Drive,
 * and pastes the shareable link directly back into Column AL (Revenue Statement Link).
 * 
 * Fully integrated with Stage 9 of the Pocket FM Outreach CRM Engine.
 */

// Global Configuration
const STATEMENT_CONFIG = {
  DRIVE_FOLDER_NAME: "Pocket FM Revenue Statements",
  DEFAULT_REV_SHARE_PCT: 15, // 15% standard gross revenue share
  TEMPLATE_FILE_NAME: "StatementTemplate.html"
};

/**
 * Adds the "📊 Pocket FM Statements" custom menu to Google Sheets on open
 */
function onOpen() {
  try {
    const ui = SpreadsheetApp.getUi();
    ui.createMenu('📊 Pocket FM Statements')
      .addItem('▶ Generate Statement for Active Row', 'generateStatementForSelectedRow')
      .addItem('⚡ Generate All Missing Statements (Batch)', 'generateAllMissingStatements')
      .addSeparator()
      .addItem('🔍 Preview Statement in Dialog (Active Row)', 'previewSelectedStatement')
      .addToUi();
  } catch (e) {
    Logger.log("Menu creation skipped (headless/trigger context): " + e.message);
  }
}

/**
 * Resolves or creates the Google Drive storage folder for statements
 */
function getOrCreateStatementsFolder() {
  const folderName = STATEMENT_CONFIG.DRIVE_FOLDER_NAME;
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
  
  // Title / Show Name
  let titleCol = hLower.findIndex(h => h.includes("title") || h.includes("series") || h.includes("show") || h === "ip");
  if (titleCol === -1) titleCol = 2; // Default Col C

  // Author Name
  let authorCol = hLower.findIndex(h => h.includes("author") && !h.includes("email"));
  if (authorCol === -1) authorCol = 1; // Default Col B

  // Email
  let emailCol = hLower.findIndex(h => h.includes("author email") || h.includes("email"));

  // Revenue Statement Link Column (Approved Col AL in Columns AI-AM)
  let revLinkCol = hLower.findIndex(h => 
    (h.includes("jas") || h.includes("rev") || h.includes("statement")) && 
    (h.includes("link") || h.includes("drive") || h.includes("url"))
  );
  if (revLinkCol === -1) revLinkCol = 37; // Standard Col AL (0-indexed 37 = Col 38)

  // Status Column
  let statusCol = hLower.findIndex(h => 
    (h.includes("jas") || h.includes("rev")) && h.includes("status")
  );
  if (statusCol === -1) statusCol = 35; // Col AJ

  // Sent/Draft Column
  let sentCol = hLower.findIndex(h => 
    (h.includes("jas") || h.includes("rev")) && (h.includes("sent") || h.includes("draft"))
  );
  if (sentCol === -1) sentCol = 38; // Col AM

  // Financial & Metric Columns (with fallback fuzzy detection)
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
    statusCol,
    sentCol,
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

  // Reporting period
  let period = (cols.periodCol > -1 && row[cols.periodCol]) ? row[cols.periodCol].toString().trim() : "";
  if (!period) {
    period = "July 1, 2026 – September 30, 2026 (3-Month Statement / Q3)";
  }

  // Determine 6-Month vs 3-Month Intro
  const isSixMonth = period.toLowerCase().includes("6-month") || period.toLowerCase().includes("combined");
  const introLabel = isSixMonth 
    ? "Here's your 6-month combined revenue statement for" 
    : "Here's your 3-month quarterly revenue statement for";

  // Numerical values with safe parsing
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
  const revSharePct = STATEMENT_CONFIG.DEFAULT_REV_SHARE_PCT;
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
  
  template = template
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

  return template;
}

/**
 * Generates statement file on Google Drive and writes link into Google Sheet
 */
function generateAndSaveStatement(sheet, rowVals, cols, rowNum) {
  const data = extractRowStatementData(rowVals, cols, rowNum);
  const htmlContent = buildStatementHtml(data);
  const folder = getOrCreateStatementsFolder();

  // Create clean filename
  const cleanTitle = data.title.replace(/[^a-zA-Z0-9_\- ]/g, "").trim().replace(/\s+/g, "_");
  const filename = `Revenue_Statement_${cleanTitle}.html`;

  // Search if file already exists in folder to update it or create new
  const existingFiles = folder.getFilesByName(filename);
  let file;
  if (existingFiles.hasNext()) {
    file = existingFiles.next();
    file.setContent(htmlContent);
  } else {
    file = folder.createFile(filename, htmlContent, MimeType.HTML);
  }

  // Set sharing to Anyone with link can view
  file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
  const driveUrl = file.getUrl();

  // Write directly to Column AL (1-based column index = cols.revLinkCol + 1)
  const targetCol = cols.revLinkCol + 1;
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
 * Action 1: Generates statement for the row currently selected by the user
 */
function generateStatementForSelectedRow() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const range = sheet.getActiveRange();
  if (!range) {
    SpreadsheetApp.getUi().alert("Please select a row first!");
    return;
  }
  
  const rowNum = range.getRow();
  if (rowNum === 1) {
    SpreadsheetApp.getUi().alert("Row 1 is the header row. Please select an author row.");
    return;
  }

  const numCols = sheet.getLastColumn();
  const headers = sheet.getRange(1, 1, 1, numCols).getValues()[0];
  const rowVals = sheet.getRange(rowNum, 1, 1, numCols).getValues()[0];
  const cols = resolveStatementColumns(headers);

  if (!rowVals[cols.titleCol]) {
    SpreadsheetApp.getUi().alert(`Row ${rowNum} does not contain a show title!`);
    return;
  }

  try {
    const res = generateAndSaveStatement(sheet, rowVals, cols, rowNum);
    SpreadsheetApp.getUi().alert(
      `✅ Revenue Statement Generated!\n\n` +
      `Show: ${res.title}\n` +
      `Author: ${res.author}\n` +
      `Link: ${res.url}\n\n` +
      `The link has been written directly to Column AL.`
    );
  } catch (err) {
    SpreadsheetApp.getUi().alert("Error generating statement: " + err.message);
  }
}

/**
 * Action 2: Generates statements in batch for all active rows missing a link in Col AL
 */
function generateAllMissingStatements() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const lastRow = sheet.getLastRow();
  const numCols = sheet.getLastColumn();
  
  if (lastRow < 2) {
    SpreadsheetApp.getUi().alert("No data found in current sheet.");
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
    
    // Skip empty rows
    const rawTitle = (cols.titleCol > -1 && rowVals[cols.titleCol]) ? rowVals[cols.titleCol].toString().trim() : "";
    if (!rawTitle || rawTitle === "-" || rawTitle.startsWith("#")) {
      continue;
    }

    // Check if Column AL already has a link
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

  SpreadsheetApp.getUi().alert(
    `⚡ Batch Statement Generation Complete!\n\n` +
    `• Generated & Linked: ${generatedCount}\n` +
    `• Already Had Links (Skipped): ${skippedCount}`
  );
}

/**
 * Action 3: Shows an interactive preview of the statement for the selected row
 */
function previewSelectedStatement() {
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

  const htmlOutput = HtmlService.createHtmlOutput(htmlContent)
    .setWidth(900)
    .setHeight(650);
  SpreadsheetApp.getUi().showModalDialog(htmlOutput, `Statement Preview: ${data.title}`);
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
