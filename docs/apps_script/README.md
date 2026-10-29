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

## How to Use the Pocket FM Automation Menu

1. Reload the Google Spreadsheet tab.
2. In the top menu bar, you will see the menu: **`Pocket FM Automation`**.
3. You can run all stages at once or each stage individually in complete isolation:
   - **`▶️ Run All Automations at Once`**: Runs all 10 stages sequentially.
   - **`1️⃣ Run Welcome Emails Only`**: Contract signed today.
   - **`2️⃣ Run Vendor Onboarding Only`**: Onboarding docs dispatch.
   - **`3️⃣ Run MG Payout Initiated Only`**: Vendor exited today.
   - **`4️⃣ Run MG Payout Confirmation Only`**: MG payout processed.
   - **`5️⃣ Run Author Check-In 1 (15 Days) Only`**: 15 days from feedback mail.
   - **`6️⃣ Run Author Check-In 2 (30 Days) Only`**: 30 days from feedback mail.
   - **`7️⃣ Run Show Launch Announcements Only`**: Live show launch.
   - **`8️⃣ Run Newsletter (The Author Edit) Only`**: 15 days from launch.
   - **`9️⃣ Run Quarterly Revenue Statements (Worked Well) Only`**: Testing / Testing_PGC / Testing_PGC_Completed / Launched (ROW) shows (Content Update & Payment Ready drafts). *Strictly requires a valid Revenue Statement Link in Col AL (suppressed if blank).*
   - **`🔟 Run Content Didn't Work Well Statements Only`**: Condition is Dropped / Bad / Sunset (Didn't work well - Content + Payment Related Update draft). *Strictly requires a valid Revenue Statement Link in Col AL (suppressed if blank).*
   - **`🧪 Test Content Didn't Work Well Draft`**: Generates a test "Didn't work well - Content + Payment Related Update" draft directly to your Gmail.
   - **`🧪 Test Newsletter Draft`**: Generates a test newsletter directly to your Gmail.
   - **`⚡ Enable Auto-Sync Sent Emails` / `🔄 Sync Sent Emails Now`**: Syncs sent drafts back to sheet status dropdowns.

