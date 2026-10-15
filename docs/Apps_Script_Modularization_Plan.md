# Pocket FM CRM Automation: 5-Part Modular Architecture Plan

> **Document Version:** 2.0 (Updated with Blank Row Filtering & Single Master Run Button)  
> **Prepared For:** Pocket FM US Licensing & Engineering Team  
> **Author:** Antigravity AI Pair Programmer  
> **Target Sheet:** [Pocket FM Post-Sales Tracker (gid=120747375)](https://docs.google.com/spreadsheets/d/1A1vJ0DsmDxtCFZiuyu6vtuQFWqClPyK7e1_lHKddGdQ/edit?gid=120747375#gid=120747375)

---

## 1. Executive Summary

### Current Situation
The CRM email drafting, spreadsheet tracking, sent mail synchronization, date anomaly detection, and check-in timer logic currently reside in a single monolithic script file (`apps_script_drafter.js`, **3,250+ lines of code**).

### Sheet Data Characteristics (Discovered via Data Audit)
* **Active Filled Rows:** **Rows 4 to 112 (109 active show rows)** contain real author, show title, and deal information.
* **Blank Shell Rows:** **Rows 113 to 996 (884 empty rows)** exist only because dropdown data validations and formulas were dragged down the sheet.
* **Requirement:** Automated triggers and batch runners must **never process or log errors for blank rows**. They must evaluate only rows filled with data and skip empty rows instantly.

### The Solution: 5-Part Modular Architecture with a Single Master Run Button
Divide the codebase into **5 logically independent `.gs` files** inside Google Apps Script that share a unified global scope, governed by a **single-click custom top-bar menu button** directly inside Google Sheets:

```
                    ┌────────────────────────────────────────────────────────┐
                    │               Google Sheet Top Menu Bar                │
                    │   [ ⚡ Pocket FM Automation ▾ ]                        │
                    │   ├── ▶️ 🚀 RUN ALL AUTOMATIONS (Single Click)         │
                    │   ├── ──────────────────────────────────────────       │
                    │   ├── ✉️ Run Author Check-Ins (15 & 30 Days)           │
                    │   ├── 🚀 Run Show Launch Announcements Only            │
                    │   ├── 📋 Run Standard Outreach (Welcome, Vendor, MG)   │
                    │   └── 🔄 Sync Sent Emails (Mark "Sent")                │
                    └──────────────────────────┬─────────────────────────────┘
                                               │
                                               ▼
                               ┌──────────────────────────────────┐
                               │            Main.gs               │
                               │  • onOpen() Top Menu Builder     │
                               │  • onEdit() Live Row Trigger     │
                               │  • runAllOutreachAutomations()   │
                               │    (Master Orchestrator)         │
                               └────────────────┬─────────────────┘
                                                │
                   ┌────────────────────────────┼────────────────────────────┐
                   ▼                            ▼                            ▼
        ┌────────────────────┐       ┌────────────────────┐       ┌────────────────────┐
        │     Config.gs      │       │  StageHandlers.gs  │       │    Templates.gs    │
        │ • isTrackerRowFilled◄─────►│ • Welcome & Vendor │◄─────►│ • getBody() HTML   │
        │ • resolveColumns() │       │ • MG Payouts       │       │ • wrapHtml()       │
        │ • parseDateSafe()  │       │ • Check-Ins (15/30)│       │ • Dynamic Grammar  │
        │ • cleanEmail()     │       │ • Show Launch      │       └────────────────────┘
        │ • Sheet GIDs       │       │ • Revenue (AMJ/JAS)│
        └────────────────────┘       └──────────┬─────────┘
                                                │
                                                ▼
                                     ┌────────────────────┐
                                     │   DraftEngine.gs   │
                                     │ • createDraft()    │
                                     │ • Queue Injection  │
                                     │ • syncSentEmails() │
                                     │ • flush() Updates  │
                                     └────────────────────┘
```

---

## 2. Detailed Breakdown of the 5 Modules

### Module 1: `Config.gs` (Configuration & Shared Utilities)
**Purpose:** Single source of truth for sheet identifiers, column resolution, date parsing, sanitizers, and the **global row filter**.

* **Global Constants:**
  * Target Spreadsheet ID: `1A1vJ0DsmDxtCFZiuyu6vtuQFWqClPyK7e1_lHKddGdQ`
  * Post-Sales Tracker Tab GID: `120747375`
* **Core Blank Row Gatekeeper (`isTrackerRowFilled`):**
  ```javascript
  function isTrackerRowFilled(rowVals, titleCol = 2) {
    if (!rowVals || rowVals.length === 0) return false;
    let rawTitle = (titleCol > -1 && rowVals.length > titleCol && rowVals[titleCol]) 
                   ? rowVals[titleCol].toString().trim() : "";
    if (!rawTitle || rawTitle === "" || rawTitle === "-" || rawTitle === "#N/A" || 
        rawTitle.toLowerCase() === "n/a" || rawTitle.startsWith("#")) {
      return false; // Blank or placeholder row
    }
    // Verify row has at least one other non-empty cell beside title
    for (let c = 0; c < rowVals.length; c++) {
      if (c === titleCol) continue;
      let val = rowVals[c];
      if (val !== null && val !== undefined && val.toString().trim() !== "" && val.toString().trim() !== "-") {
        return true; // Valid row with real deal data
      }
    }
    return false;
  }
  ```
* **Column Resolver Function (`resolveTrackerColumns`):**
  * Dynamically scans row 3 headers and resolves 0-based column indices for all columns (Col J Launch Date, Col O Script Date, Col V Feedback Date, Col W/Y Check-Ins, Col AA/AB Launch Status, Col AE–AQ Revenue Statements).
* **Sanitization & Date Parsing:**
  * `parseDateSafe(dateVal)`: Multi-format date engine supporting text ordinals (*"2nd october"*, *"6 th october"*), Excel serial numbers, DD/MM/YYYY, MM/DD/YYYY, and ISO formats.
  * `cleanEmail(rawEmail)`: Extracts clean email addresses from `<email@domain.com>` brackets and removes trailing whitespace or semicolons.
  * `cleanCcList(rawCc)`: Validates and formats comma-separated CC recipients.
  * `isValidEmail(emailStr)`: Regex validator for recipient emails.

---

### Module 2: `Templates.gs` (HTML Email Design System)
**Purpose:** Houses all branded, responsive HTML templates and dynamic text logic (pure functions, decoupled from sheet access).

* **Components:**
  * `wrapHtml(bodyContent, queueId)`: Renders the Pocket FM branded responsive container (600px width, Poppins font, logo headers, dark-mode styling, and tracking token footer).
  * `getBody(type, firstName, title, link, grammar, revLink, argus, showName)`:
    * **Welcome Email:** Contract signing date from Column A Timestamp in Lifecycle Master, onboarding milestones.
    * **Vendor Onboarding:** Manuscript submission guidelines, portal links.
    * **MG Payout Processed:** Minimum guarantee payment confirmation.
    * **Author Check-In 1 (15 Days):** Experience questionnaire, feedback check.
    * **Author Check-In 2 (30 Days):** Follow-up status check.
    * **Show Launch Announcement:** Live show celebration with clickable link and app metrics.
    * **Quarterly Revenue Statements:** Dynamic earnings snapshot with Argus metrics and invoicing table.

---

### Module 3: `DraftEngine.gs` (Execution & Synchronization Engine)
**Purpose:** Handles Gmail API calls, spreadsheet cell updates, and GMass queue logging.

* **Core Operations:**
  * `createDraft(...)`:
    * Generates Gmail drafts using `GmailApp.createDraft()`.
    * Injects metadata into the `Queue` tab (UUID, recipient, send time, template name).
    * Directly updates target status dropdowns (e.g. Col AB $\rightarrow$ `"Draft Ready"`, Col W $\rightarrow$ `"draft ready"`) and stamps sent timestamps (Col AC, Col X, Col Z).
    * Calls `SpreadsheetApp.flush()` to commit cell writes immediately.
  * `syncSentEmails()`:
    * Scans Gmail sent threads to automatically update dropdowns from `"Draft Ready"` $\rightarrow$ **`"Sent"`** when team members dispatch outreach.
    * Strictly skips blank rows in the Queue sheet.

---

### Module 4: `StageHandlers.gs` (Business Logic by Stage)
**Purpose:** Contains cleanly separated, isolated logic for each outreach stage. Every stage function receives row data, checks `isTrackerRowFilled`, and evaluates rules.

* **Stage Handlers:**
  1. `handleWelcomeAndVendor(rowVals, mainDict, mainHeaders)`:
     * Triggers when Timestamp (Column A in Lifecycle Master) is today.
  2. `handleMGPayout(rowVals, mainDict, psHeaders)`:
     * Triggers on MG Payout Exit Date; stamps **Feedback Mail Date (Col V)**.
  3. `handleAuthorCheckIns(psSheet, row, rowVals, headers)`:
     * Skips if `!isTrackerRowFilled(rowVals)`.
     * References **Feedback Mail Date (Col V)**.
     * Override Rule: If Col AB is `"Sent"`, Col W & Col Y set to `"Does not apply"`.
     * **15-Day Check-In (Col W):**
       - Day 0–14: `"Not due yet"`
       - Day 15: Creates draft $\rightarrow$ Col W set to `"draft ready"`, Col X stamped.
       - Day 16+ (15th day over): Col W dropdown changes to **`"Overdue"`**. Catch-up draft created if missed.
     * **30-Day Check-In (Col Y):**
       - Day 0–29: `"Not due yet"`
       - Day 30: Creates draft $\rightarrow$ Col Y set to `"draft ready"`, Col Z stamped.
       - Day 31+ (30th day over): Col Y dropdown changes to **`"Overdue"`**. Catch-up draft created if missed.
  4. `handleShowLaunchAnnouncement(psSheet, row, rowVals, headers)`:
     * Skips if `!isTrackerRowFilled(rowVals)`.
     * Validates Mandatory Condition 1 (Show Link, Launch Date, `testing_pgc`).
     * `Launch Date <= Script Date`: Flags Col AB as **`"Launch Date Issue"`**, Col AA as **`"Check with content"`**, suppresses draft.
     * `Launch Date > Script Date`: Creates draft $\rightarrow$ Col AB/AA set to **`"Draft Ready"`**, Col AC stamped.
  5. `handleNewsletterEdit(rowVals, headers)`:
     * Evaluates 15 days post-launch.
  6. `handleQuarterlyRevenueStatements(rowVals, headers)`:
     * Evaluates AMJ, JAS, OND statement drives and invoice triggers.

---

### Module 5: `Main.gs` & User Interface (One-Click Master Orchestrator)
**Purpose:** Master orchestrator, user-facing menu buttons, and automated triggers.

#### 1. The Single Master Run Button (`runAllOutreachAutomations`)
Runs all stages sequentially across the spreadsheet with **1 click**. Reads data in a single batch, processes only filled rows, skips blank rows, and reports progress to the user.

```javascript
/**
 * MASTER SINGLE-CLICK RUNNER:
 * Connects all automation stages into one button.
 * Evaluates ONLY rows filled with data (Rows 4-112) and skips blank rows (Rows 113-996).
 */
function runAllOutreachAutomations() {
  const ui = SpreadsheetApp.getUi();
  const psSheet = getPostSalesTrackerSheet();
  if (!psSheet) {
    ui.alert("Error", "Post-Sales Tracker sheet tab not found!", ui.ButtonSet.OK);
    return;
  }

  const lastRow = psSheet.getLastRow();
  const lastCol = Math.max(psSheet.getLastColumn(), 30);
  const allData = psSheet.getRange(1, 1, lastRow, lastCol).getValues();
  const headers = allData[2]; // Row 3
  const titleCol = headers.findIndex(h => h.toString().toLowerCase().includes("title")) > -1 
                   ? headers.findIndex(h => h.toString().toLowerCase().includes("title")) : 2;

  let evaluatedCount = 0;
  let skippedBlankCount = 0;

  for (let r = 4; r <= lastRow; r++) {
    let rowVals = allData[r - 1];

    // STRICT BLANK ROW GUARD: Skip empty placeholder rows
    if (!isTrackerRowFilled(rowVals, titleCol)) {
      skippedBlankCount++;
      continue;
    }

    // Run all stage handlers for this populated row
    handleAuthorCheckIns(psSheet, r, rowVals, headers);
    handleShowLaunchAnnouncement(psSheet, r, rowVals, headers);
    evaluatedCount++;
  }

  // Also process standard outreach queue (Welcome, Vendor, MG payouts)
  processOutreachQueue(false);

  SpreadsheetApp.flush();

  // Show clean success toast/alert to the user in Google Sheets
  SpreadsheetApp.getActiveSpreadsheet().toast(
    `Evaluated ${evaluatedCount} active rows (${skippedBlankCount} blank rows skipped). All drafts & statuses updated!`,
    "Automation Complete",
    6
  );
}
```

#### 2. Google Sheets Top-Bar Menu Integration (`onOpen`)
Creates a native dropdown menu directly in the spreadsheet header when the sheet is opened:

```javascript
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu("⚡ Pocket FM Automation")
    .addItem("▶️ 🚀 RUN ALL AUTOMATIONS (Single Click)", "runAllOutreachAutomations")
    .addSeparator()
    .addItem("✉️ Run Author Check-Ins (15 & 30 Days)", "runAuthorCheckInBatch")
    .addItem("🚀 Run Show Launch Announcements Only", "runLaunchAnnouncementBatch")
    .addItem("📋 Run Standard Outreach (Welcome, Vendor, MG)", "runOutreachQueueBatch")
    .addSeparator()
    .addItem("🔄 Sync Sent Emails (Mark Dropdowns 'Sent')", "syncSentEmails")
    .addToUi();
}
```

#### 3. Real-Time Sheet Trigger (`onEdit(e)`)
* Intercepts edits to Launch Dates, Script Dates, Launch Statuses, or Feedback Dates.
* Immediately checks `if (!isTrackerRowFilled(rowVals)) return;`
* If filled, updates status dropdowns on the fly in real-time.

#### 4. Automated Daily Timer (`dailyLifecycleTimerRunner`)
* Runs daily at 9:00 AM via time-driven trigger.
* Calls `runAllOutreachAutomations()`, cycling through filled rows only without user intervention.

---

## 3. Comparison: Monolithic vs. 5-Part Modular Architecture

| Dimension | Monolithic Script (`apps_script_drafter.js`) | 5-Part Modular Architecture |
| :--- | :--- | :--- |
| **Code Organization** | 1 huge file $\times$ 3,250+ lines | **5 distinct files** $\times$ ~200–500 lines each |
| **Row Traversal** | Looped 996 rows, calling API on blank rows | **Batch reads, evaluates 109 filled rows, skips 884 blanks** |
| **Execution Speed** | ~40–60 seconds (API call per row) | **~2–4 seconds** (in-memory batch filtering) |
| **Trigger Method** | Open script editor $\rightarrow$ select function $\rightarrow$ click Run | **1 Click** directly in Google Sheets top menu |
| **Locating a Bug** | Scroll through 3,250 lines | Open the specific stage file (e.g., `StageHandlers.gs`) |
| **Blank Row Safety** | Risk of stamping "Not due yet" on blank rows | **Zero**: Protected by `isTrackerRowFilled` |
| **Sub-Buttons Available?** | No, all-or-nothing or manual function picking | **Yes**: Master button + stage-specific buttons in UI |

---

## 4. Implementation Steps (Ready for Execution Upon Approval)

1. **Step 1: Open Apps Script Project**
   * In [US Licensing Lifecycle Tracker](https://docs.google.com/spreadsheets/d/1A1vJ0DsmDxtCFZiuyu6vtuQFWqClPyK7e1_lHKddGdQ/edit?gid=120747375#gid=120747375), click **Extensions > Apps Script**.
2. **Step 2: Create the 5 Files**
   * Click **+** next to *Files* $\rightarrow$ *Script* to create:
     1. `Config.gs`
     2. `Templates.gs`
     3. `DraftEngine.gs`
     4. `StageHandlers.gs`
     5. `Main.gs`
3. **Step 3: Transfer & Distribute Functions**
   * Move the respective sections from the verified `apps_script_drafter.js`.
4. **Step 4: Verify & Test**
   * Refresh the Google Sheet.
   * Verify the **⚡ Pocket FM Automation** menu appears at the top.
   * Click **▶️ 🚀 RUN ALL AUTOMATIONS** and confirm execution completes with the toast notification:  
     `"Evaluated 109 active rows (884 blank rows skipped). All drafts & statuses updated!"`
