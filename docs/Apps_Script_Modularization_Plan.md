# Pocket FM CRM Automation: 5-Part Modular Architecture Plan

> **Document Version:** 1.0  
> **Prepared For:** Pocket FM US Licensing & Engineering Team  
> **Author:** Antigravity AI Pair Programmer  
> **Target Sheet:** [Pocket FM Post-Sales Tracker (gid=120747375)](https://docs.google.com/spreadsheets/d/1A1vJ0DsmDxtCFZiuyu6vtuQFWqClPyK7e1_lHKddGdQ/edit?gid=120747375#gid=120747375)

---

## 1. Executive Summary

### Current Situation
The entire CRM email drafting, spreadsheet tracking, sent mail synchronization, and error handling logic currently resides in a single monolithic script file (`apps_script_drafter.js`, **2,500+ lines of code**).

### Pain Points
* **Maintenance Bottleneck:** A small change in one stage (e.g., launch date anomaly validation) requires searching through 2,500 lines of code.
* **Variable Scope Leakage:** Helper functions declared in inner closures can cause runtime errors (e.g., `ReferenceError: cleanEmail is not defined`).
* **Deployment Friction:** Team members must open the Apps Script code editor, select a specific function from a dropdown, and hit "Run".

### The Solution: 5-Part Modular Architecture
Divide the monolithic codebase into **5 logically independent files** inside Google Apps Script that share a unified global namespace (no `import` or `require` needed), paired with a **single-click custom menu button** in the Google Sheets interface.

```
                    ┌────────────────────────────────────────────────────────┐
                    │               Google Sheet Top Menu                    │
                    │      [ Pocket FM Automation ▾ ] -> "▶️ Run All Drafts"   │
                    └──────────────────────────┬─────────────────────────────┘
                                               │
                                               ▼
                              ┌──────────────────────────────────┐
                              │            Main.gs               │
                              │  • onOpen() Menu Builder         │
                              │  • onEdit() Live Trigger         │
                              │  • runAllOutreachStages()        │
                              └────────────────┬─────────────────┘
                                               │
                  ┌────────────────────────────┼────────────────────────────┐
                  ▼                            ▼                            ▼
       ┌────────────────────┐       ┌────────────────────┐       ┌────────────────────┐
       │     Config.gs      │       │  StageHandlers.gs  │       │    Templates.gs    │
       │ • Column Resolvers │◄─────►│ • Welcome & Vendor │◄─────►│ • getBody() HTML   │
       │ • parseDateSafe()  │       │ • MG Payouts       │       │ • wrapHtml()       │
       │ • cleanEmail()     │       │ • Check-Ins (15/30)│       │ • Dynamic Grammar  │
       │ • Sheet GIDs       │       │ • Show Launch      │       └────────────────────┘
       └────────────────────┘       │ • Revenue (AMJ/JAS)│
                                    └──────────┬─────────┘
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
**Purpose:** Single source of truth for sheet identifiers, column headers, date parsing, and sanitizers.
* **Global Constants:**
  * Master Sheet GID and Post-Sales Tracker GID (`120747375`).
* **Column Resolver Function (`resolveTrackerColumns`):**
  * Automatically resolves 0-based column indices for all dynamic columns (Col J Launch Date, Col O Script Date, Col W/Y Check-Ins, Col AA/AB Launch Status & Dropdowns, Col AE–AQ Revenue Statements).
* **Sanitization & Parsing Helpers:**
  * `parseDateSafe(dateVal)`: Multi-format date engine supporting text ordinals (*"2nd october"*), serial numbers, and ISO strings.
  * `cleanEmail(rawEmail)`: Extracts pure email addresses from `<email@domain.com>` brackets and removes trailing spaces/semicolons.
  * `cleanCcList(rawCc)`: Validates and formats comma-separated CC recipients.
  * `isValidEmail(emailStr)`: Regex validator for recipient emails.

---

### Module 2: `Templates.gs` (HTML Email Design System)
**Purpose:** Houses all branded, responsive HTML templates and dynamic text logic.
* **Components:**
  * `wrapHtml(bodyContent, queueId)`: Renders the Pocket FM branded responsive container (600px, Poppins font, logo headers, dark-mode styling, and GMass tracking token footer).
  * `getBody(type, firstName, title, link, grammar, revLink, argus, showName)`:
    * **Welcome Email:** Onboarding milestones and next steps.
    * **Vendor Onboarding:** Manuscript submission guidelines and invoice portal links.
    * **MG Payout Processed:** Minimum guarantee payment confirmation.
    * **Author Check-In 1 (15 Days):** Check-in questionnaire on production experience.
    * **Author Check-In 2 (30 Days):** Follow-up status check.
    * **Show Launch Announcement:** Live show celebration with clickable link and app metrics.
    * **Quarterly Revenue Statements:** Dynamic earnings snapshot with Argus metrics and invoicing table.

---

### Module 3: `DraftEngine.gs` (Execution & Synchronization Engine)
**Purpose:** Handles low-level Gmail API calls, spreadsheet writing, and GMass queue logging.
* **Core Operations:**
  * `createDraft(...)`:
    * Generates Gmail drafts using `GmailApp.createDraft()`.
    * Injects metadata into the spreadsheet `Queue` tab (UUID, recipient, send time, template name, GMass tracking).
    * Directly updates target status dropdowns (e.g. Col AB $\rightarrow$ `"Draft Ready"`) and stamps sent timestamps (Col AC, Col X, Col Z).
    * Calls `SpreadsheetApp.flush()` to instantly commit cell writes to the live sheet.
  * `syncSentEmails()`:
    * Scans Gmail sent threads to automatically update dropdowns from `"Draft Ready"` $\rightarrow$ **`"Sent"`** when team members dispatch outreach.

---

### Module 4: `StageHandlers.gs` (Business Logic by Stage)
**Purpose:** Contains cleanly separated, isolated logic for every outreach stage.
* **Stage Handlers:**
  1. `handleWelcomeAndVendor(row, rowData)`: Triggers when Timestamp (Column A in Lifecycle Master) is today.
  2. `handleMGPayoutInitiated(row, rowData)`: Triggers on Vendor Lifecycle Exit Date.
  3. `handleMGPayoutConfirmed(row, rowData)`: Triggers on MG Payout Exit Date; automatically stamps **Feedback Mail Date (Col V)**.
  4. `handleAuthorCheckIns(row, rowData)`:
     * Evaluates elapsed days referencing **Feedback Mail Date (Col V)**.
     * Overrides Col W & Y to `"Does not apply"` if Col AB is marked `"Sent"`.
     * **15-Day Check-In (Col W):**
       - Day 0–14: Col W is `"Not due yet"`.
       - Day 15: Creates Check-In 1 draft $\rightarrow$ Col W turns to `"draft ready"`, Col X stamped with date.
       - Day 16+ (once 15th day is over): Col W dropdown changes to **`"Overdue"`**. Catch-up draft generated if previously uncreated.
     * **30-Day Check-In (Col Y):**
       - Day 0–29: Col Y is `"Not due yet"`.
       - Day 30: Creates Check-In 2 draft $\rightarrow$ Col Y turns to `"draft ready"`, Col Z stamped with date.
       - Day 31+ (once 30th day is over): Col Y dropdown changes to **`"Overdue"`**. Catch-up draft generated if previously uncreated.
  5. `handleShowLaunchAnnouncement(row, rowData)`:
     * Validates Mandatory Condition 1 (Show Link, Launch Date, `testing_pgc` status).
     * Compares Launch Date vs. Script Date (Col O):
       * `Launch Date <= Script Date`: Flags Col AB as **`"Launch Date Issue"`**, Col AA as **`"Check with content"`**, suppresses draft.
       * `Launch Date > Script Date`: Creates draft $\rightarrow$ Col AB/AA set to **`"Draft Ready"`**, Col AC stamped.
  6. `handleNewsletterEdit(row, rowData)`: Triggers 15 days post-launch.
  7. `handleQuarterlyRevenueStatements(row, rowData)`: AMJ, JAS, OND statement drives and invoice triggers.

---

### Module 5: `Main.gs` & User Interface (One-Click Runners)
**Purpose:** Master orchestrator and user-facing entry points.
* **Top-Level Orchestrators:**
  * `runAllOutreachStages()`: Executes stages 1 through 9 across all spreadsheet rows.
  * `runLaunchAnnouncementBatch()`: Dedicated one-click scan specifically for Show Launch rows.
  * `runAuthorCheckInBatch()`: Dedicated one-click scan specifically for 15-day / 30-day check-ins.
* **Custom Google Sheets Top Menu (`onOpen`):**
  Adds a native dropdown menu directly in the spreadsheet header:
  ```
  Pocket FM Outreach
  ├── ▶️ Run All Outreach Drafts
  ├── 🚀 Run Show Launch Announcements Only
  ├── ✉️ Run Author Check-Ins (15 & 30 Days)
  └── 🔄 Sync Sent Emails (Mark Dropdowns "Sent")
  ```
* **Real-Time Trigger (`onEdit(e)`):**
  * Listens for edits to Launch Dates, Script Dates, Launch Statuses, or Feedback Dates.
  * Instantly re-evaluates the edited row and updates status dropdowns on the fly.

---

## 3. Team Benefits Comparison

| Dimension | Monolithic Script (Current) | 5-Part Modular Architecture (New) |
| :--- | :--- | :--- |
| **File Length** | 1 file $\times$ 2,592 lines | 5 files $\times$ ~200–500 lines each |
| **Change Execution Time** | 10–25 minutes (risk of side-effects) | **Seconds** (localized to 1 file) |
| **Trigger Mechanism** | Must open script editor, pick function, click Run | **1 Click** directly in Google Sheets menu |
| **Risk of Scope Errors** | High (nested functions in large loops) | **Zero** (global shared namespace) |
| **Testing** | Difficult to test individual stages | Each stage can be tested independently |

---

## 4. Implementation & Rollout Steps

1. **Step 1: Create Files in Apps Script Editor**
   * Open the target Google Sheet $\rightarrow$ **Extensions > Apps Script**.
   * Click the **+** icon next to *Files* $\rightarrow$ select *Script*.
   * Create: `Config.gs`, `Templates.gs`, `DraftEngine.gs`, `StageHandlers.gs`, and `Main.gs`.
2. **Step 2: Distribute Code**
   * Move helper functions into `Config.gs`.
   * Move email templates into `Templates.gs`.
   * Move draft creation and queue operations into `DraftEngine.gs`.
   * Move stage logic into `StageHandlers.gs`.
   * Place `onOpen()`, `onEdit()`, and master runners in `Main.gs`.
3. **Step 3: Verification & Test Run**
   * Run `testShowLaunchAnnouncement()` to verify date anomaly (`Launch Date Issue`) and valid launch drafting.
   * Reload the Google Sheet and verify the custom menu button appears in the top menu bar.
4. **Step 4: Go-Live**
   * Instruct operations team members to use the custom **Pocket FM Outreach** menu directly inside the sheet.
