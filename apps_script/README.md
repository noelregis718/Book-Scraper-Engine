# Pocket FM CRM Automation - 5-Part Modular Scripts

This folder contains the complete, verified 5-part modular division of the Pocket FM CRM Apps Script automation.

## File Structure

| File (.gs / .js) | Purpose | Role |
| :--- | :--- | :--- |
| **`Config.gs`** / **`Config.js`** | Single source of truth for IDs, column resolvers, date parser (`parseDateSafe`), sanitizers, and **`isTrackerRowFilled()`**. | Shared utilities & row filter |
| **`Templates.gs`** / **`Templates.js`** | All branded HTML templates (`wrapHtml`, `getBody`) for all 12 stages. | Responsive HTML design system |
| **`DraftEngine.gs`** / **`DraftEngine.js`** | Low-level Gmail draft creation (`GmailApp.createDraft`), Queue logging, and `syncSentEmails()`. | Execution & sync engine |
| **`StageHandlers.gs`** / **`StageHandlers.js`** | Business rules: Author Check-Ins (15/30 Days), Show Launch (anomaly vs valid), and Outreach Queue (Welcome, Vendor, MG, Rev Statements). | Core business logic |
| **`Main.gs`** / **`Main.js`** | Google Sheets Top Menu (`onOpen`), **Single Master Run Button (`runAllOutreachAutomations`)**, sub-runners, live trigger (`onEdit`), and daily timers. | Master orchestrator & UI |

---

## How to Install in Google Apps Script

1. Open your Google Sheet: [Pocket FM Post-Sales Tracker](https://docs.google.com/spreadsheets/d/1A1vJ0DsmDxtCFZiuyu6vtuQFWqClPyK7e1_lHKddGdQ/edit?gid=120747375#gid=120747375).
2. Go to **Extensions > Apps Script**.
3. Create 5 script files by clicking the **+** icon next to **Files** $\rightarrow$ **Script**:
   - `Config`
   - `Templates`
   - `DraftEngine`
   - `StageHandlers`
   - `Main`
4. Copy and paste the corresponding code from each file in this folder into the Apps Script editor.
5. Click **Save** (disk icon).

---

## How to Use the Single Master Run Button

1. Reload the Google Spreadsheet tab.
2. In the top menu bar, you will see a new menu: **`Pocket FM Automation`**.
3. Click **`▶️ 🚀 RUN ALL AUTOMATIONS (Single Click)`**.
4. The script will:
   - Make 1 batch read of the entire sheet.
   - Filter and evaluate **only the 109 active rows (Rows 4 to 112)**.
   - Skip all **884 blank formula rows (Rows 113 to 996)**.
   - Display a toast notification:  
     `"Evaluated 109 active rows (884 blank rows skipped). All drafts & statuses updated!"`
