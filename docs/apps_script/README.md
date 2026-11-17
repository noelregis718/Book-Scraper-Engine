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

1. Open your Google Sheet: [Pocket FM Post-Sales Tracker](https://docs.google.com/spreadsheets/d/1JFT4_f9Du6UZWi6aM0FjYvyR-mcAsbARq7JyxJwLPZc/edit?gid=120747375#gid=120747375).
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
   - **8️⃣ Run Newsletter (The Author Edit) Only**: 15 days from Show Launch Announcement Sent Date (Col AC). Strictly requires Col AC date and live link (ignores Col J).
   - **`9️⃣ Run Quarterly Revenue Statements (Worked Well) Only`**: Testing / Testing_PGC / Testing_PGC_Completed / Launched (ROW) shows (Content Update & Payment Ready drafts). *Strictly requires a valid Revenue Statement Link in Col AL (suppressed if blank).*
   - **`🔟 Run Content Didn't Work Well Statements Only`**: Condition is Dropped / Bad / Sunset (Didn't work well - Content + Payment Related Update draft). *Strictly requires a valid Revenue Statement Link in Col AL (suppressed if blank).*
   - **`⚡ Enable Auto-Sync Sent Emails` / `🔄 Sync Sent Emails Now`**: Syncs sent drafts back to sheet status dropdowns.

---

## Quarterly Revenue Statement Logic (Columns AE to AQ)

### 1. Cycle & Column Mapping

The Post-Sales Tracker divides quarterly revenue reporting into 3 distinct cycles:

| Cycle | Quarter & Months | Statement Date / Due Date | Email Status Col | Drive / Vercel Link Col | Sent Status Col |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **AMJ** | Q2 (April – June) | **Col AE** (31) | **Col AF** (32) | **Col AG** (33) | **Col AH** (34) |
| **JAS** | Q3 (July – September) | **Col AI** (35) / **Col AK** (37)* | **Col AJ** (36) | **Col AL** (38) | **Col AM** (39) |
| **OND** | Q4 (October – December) | **Col AN** (40) | **Col AO** (41) | **Col AP** (42) | **Col AQ** (43) |

*\*Note: For the JAS cycle, Col AK (`Revenue Statement Due Date`) is used by the sync engine to record the exact date the statement email was sent.*

---

### 2. Automation Triggers & Guardrails (Columns AJ, AK, AL, AM)

* **Column AJ (`JAS Revenue Statement + Insights Email Status`):**
  * **Draft Suppression:** If Col AJ contains `"no statement to be shared"`, `"check with content"`, or `"not due yet"`, email drafting is **strictly suppressed** (no draft is generated).
  * **Draft Permitted:** Values such as `"ready"`, `"eligible to send, statement attached"`, or blank allow drafting to proceed (subject to Col AL link validation).

* **Column AL (`JAS Revenue Statement Drive Links`):**
  * **Strict URL Validation (`isValidWebUrl`):** Col AL must contain an active web URL (starting with `http://` or `https://`, pointing to either the Vercel statement portal `pocketfm-statements.vercel.app` or Google Drive).
  * **Missing Link Guard:** If Col AL is empty or has non-URL placeholder text (e.g. `"Show Untested / Never Made Live"`), the engine **strictly suppresses draft generation**.

* **Column AK (`Revenue Statement Sent Date`):**
  * **Automatic Timestamping:** When the revenue statement email is sent from Gmail, the background sync job (`syncSentEmails`) detects the sent message and records the exact dispatch date (`YYYY-MM-DD`) into **Col AK**.

* **Column AM (`Revenue Statement + Insights Email Sent?`):**
  * **Draft Creation:** Updated to **`Draft Ready`** when `processOutreachQueue` successfully creates a draft.
  * **Sent Confirmation:** Updated to **`Sent`** when `syncSentEmails` detects the dispatched email in Gmail.
  * **Safety Guard:** Col AM will **never** be marked as `Sent` if Col AL lacks a valid URL, preventing false-positive matches with unrelated emails (such as Welcome or Launch emails).

