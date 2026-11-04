# Pocket FM CRM Automation
## Email Automation Trigger Conditions, Column Mappings & Function Reference Guide

Complete specification for all 11 outreach stages, decoupled author check-in logic, real-time `onEdit` triggers, and standalone runner functions.

---

### Architecture Summary

* **Dual-Track Execution**: Automatic hourly background scans via `processOutreachQueue()` + instant manual dropdown date stamping via `onEdit(e)`.
* **Strict Decoupled Timers**: Check-In 1 evaluates Col V + 15d; Check-In 2 evaluates Col X + 15d. Both respect the Sept 1, 2026 contract signing cutoff.
* **Two-Way Gmail Sync**: `syncSentEmails()` scans Sent Mail for tracking codes, sets status to `'Sent'`, and records live sent timestamps.
* **Isolation & Testing**: Every stage has a dedicated menu button and direct Apps Script runner function, plus automated unit test suites.

---

### 1. Core Shared Column Requirements

For any email draft to be generated, the row must satisfy these core shared columns across both tabs:
* **Recipient Email**: Post-Sales Tracker Col F (`Receiver Email ID`), with fallback to Lifecycle Master Col AD & Col AB.
* **Show Title**: Lifecycle Master Col F / Post-Sales Tracker Col C (`Title / IP`).
* **Show Link**: Lifecycle Master Col AG (`Show Link`), with fallback to Post-Sales Tracker Col L.
* **Blank Row Guard**: Row must pass `isTrackerRowFilled()` (contains valid non-blank Title/IP, not empty/unpopulated).

---

### 2. The 11 Stage Trigger Conditions & Timing Matrix

| Stage # & Name | Exact Sheet Conditions & Date Anchors | Post-Sales Dropdown & Date Stamped | Draft Subject Created | Automation Behavior & Guards |
| :--- | :--- | :--- | :--- | :--- |
| **Stage 1: Welcome Email** | • Col Q (Contract Date) == TODAY<br>• Col AA (Launch Status) != Dropped / Bad<br>• Receiver Email (Col F) is valid | Col R $\rightarrow$ `Draft Ready` | *Welcome to Pocket FM - here's what happens next* | Introduces author to Pocket FM. Authors with 2+ titles signed on the same date receive 1 consolidated draft. |
| **Stage 2: Vendor Onboarding** | • Col Q (Contract Date) == TODAY (Same day as Welcome Email)<br>• Col AA (Launch Status) != Dropped / Bad | Col S $\rightarrow$ `Draft Ready` | *Vendor Onboarding for [Title]* | Dispatches onboarding packet & Netsuite setup instructions. Runs simultaneously with Welcome Email. |
| **Stage 3: MG Payment Initiated** | • Col U (Vendor Exit Date) == TODAY<br>• Col S (Vendor Status) == `'Done'`<br>• Col AA (Launch Status) != Dropped / Bad | Col T $\rightarrow$ `Draft Ready` | *Payment Initiated: Minimum Guarantee for [Title]* | Notifies author that NetSuite bill has been approved and payment processing has commenced. |
| **Stage 4: MG Payment Processed** | • Col X (MG Exit Date) == TODAY<br>• Col V (MG Status) == `'Done'`<br>• Col AA (Launch Status) != Dropped / Bad | Col U $\rightarrow$ `Draft ready`<br>Col V $\rightarrow$ Today's Date (`Feedback Mail Date`) | *Pocket FM: Your Minimum Guarantee Payment Has Been Processed* | Confirms payment remittance. Automatically captures live timestamp in Col V (Feedback Mail Date) as anchor for Check-In 1. |
| **Stage 5: Author Check-In 1 (15 Days)** | • Col D (Contract Date) $\ge$ 2026-09-01 (If before $\rightarrow$ `'Does not apply'`)<br>• Col AB (Launch Sent) != `'Sent'` (If sent $\rightarrow$ `'Does not apply'`)<br>• Col V (Feedback Date) present:<br>&nbsp;&nbsp;- Diff < 15d $\rightarrow$ `'Not due yet'`<br>&nbsp;&nbsp;- Diff == 15d $\rightarrow$ `'draft ready'`<br>&nbsp;&nbsp;- Diff $\ge$ 16d $\rightarrow$ `'Overdue'`<br>• If Col V missing & Launch not sent $\rightarrow$ `'Not due yet'` | Col W $\rightarrow$ `draft ready`<br>Col X $\rightarrow$ Stamped with Date when Sent (UI or sync) | *We'd love your thoughts on [Title]* | 15-Day check-in. Draft generated ONLY on the 15th day. If $\ge 16$ days, Col W turns `'Overdue'` without catch-up draft. Stamped in Col X. |
| **Stage 6: Author Check-In 2 (30 Days / 15d from Check-In 1)** | • Col D (Contract Date) $\ge$ 2026-09-01 (If before $\rightarrow$ `'Does not apply'`)<br>• Col AB (Launch Sent) != `'Sent'` (If sent $\rightarrow$ `'Does not apply'`)<br>• Col X (Check-In 1 Date) present:<br>&nbsp;&nbsp;- Diff < 15d $\rightarrow$ `'Not due yet'`<br>&nbsp;&nbsp;- Diff == 15d $\rightarrow$ `'draft ready'`<br>&nbsp;&nbsp;- Diff $\ge$ 16d $\rightarrow$ `'Overdue'`<br>• If Col X missing $\rightarrow$ `'Not due yet'` | Col Y $\rightarrow$ `draft ready`<br>Col Z $\rightarrow$ Stamped with Date when Sent (UI or sync) | *Pocket FM: A quick update on your show: [Title]* | Strictly anchored to Col X Date + 15 days! Cannot trigger if Check-In 1 was never sent. Overdue if $\ge 16$ days. Stamped in Col Z. |
| **Stage 7: Show Launch Announcement** | • Col I / Col Y (Show ID) present & valid<br>• Col L / Col AG (Show Link) is LIVE URL<br>• Col AA / Col AB != `'Not launched / Unavailable / Discontinued'`<br>• Col K / Col AA Status in [Testing, Testing_PGC, Launched (ROW)] | Col AB $\rightarrow$ `Draft Ready`<br>Col AA $\rightarrow$ `Draft Ready`<br>Col AC $\rightarrow$ Stamped with Date when Sent | *Your Pocket FM Show Is Now Live: [Show Name]!* | Strict 4-point guard: If Show ID is missing, link is not live, or status is unlaunched/dropped $\rightarrow$ STRICTLY NO DRAFT. Stamped in Col AC. |
| **Stage 8: Newsletter Edit (The Author Edit)** | • Col AC (Launch Sent Date) MUST BE PRESENT<br>• Today - Col AC Date $\ge 15$ days<br>• Col L (Show Link) is LIVE URL<br>• STRICT RULE: Never considers Col J (Launch Date)! | Col AD $\rightarrow$ `Draft Ready` | *What’s new at Pocket FM + a few things worth knowing* | Creator newsletter. If Col AC is blank, missing, or $< 15$ days elapsed $\rightarrow$ STRICTLY NO DRAFT. Ignored if already Sent/Draft Ready. |
| **Stage 9A: Rev Statement: Content Update** | • Launch Status in [Testing, Testing_PGC, Testing_PGC_Completed, Launched (ROW)]<br>• Col AL (Drive Link) MUST BE VALID URL<br>• Show ID found in Argus Show Data tab | Col AM (Progress) $\rightarrow$ `Draft Ready`<br>Col AL $\rightarrow$ Drive Link | *Content Update for [Title]* | Worked Well branch: Injects live performance metrics (Duration, LDAU, Comments, Ratings) from Argus tab into draft. Suppressed if Col AL blank. |
| **Stage 9B: Rev Statement: Payment Ready** | • Launch Status in [Testing, Testing_PGC, Testing_PGC_Completed, Launched (ROW)]<br>• Col AL (Drive Link) MUST BE VALID URL | Col AM (Progress) $\rightarrow$ `Draft Ready`<br>Col AL $\rightarrow$ Drive Link | *Pocket FM: Your earnings are waiting for you!* | Worked Well branch: Dispatches quarterly earnings notification with finance approved Drive link from Col AL. Suppressed if Col AL blank. |
| **Stage 9C: Rev Statement: Sunset / Dropped** | • Launch Status in [Dropped, Bad, Show Discontinued]<br>• Col AL (Drive Link) MUST BE VALID URL | Col AM (Progress) $\rightarrow$ `Draft Ready`<br>Col AL $\rightarrow$ Drive Link | *Pocket FM: An Update on [Title]* | Didn't Work Well branch: Dispatches sunset review and engagement conclusion with Col AL Drive link. Mutually exclusive from 9A/9B. |

---

### 3. Complete Apps Script Functions & Automation Methods

| Function Name & Scope | Trigger / Invocation | Parameters | Operational Behavior & Output |
| :--- | :--- | :--- | :--- |
| **`onEdit(e)`**<br>`[Main.gs]` | Automatic Simple Trigger (Google Sheets UI Edit Event) | `e`: Event Object (sheet, range, value, row, col) | Real-time UI listener. When a user manually selects `'Sent'` in the dropdown:<br>• Col W (23) $\rightarrow$ Sets Col X (24) to today's date.<br>• Col Y (25) $\rightarrow$ Sets Col Z (26) to today's date.<br>• Col AB (28) $\rightarrow$ Sets Col AC (29) to today's date.<br>Calls `SpreadsheetApp.flush()` immediately for instant screen update. |
| **`processOutreachQueue()`**<br>`[StageHandlers.gs]` | Time-driven Trigger (Every 4 hrs) or Manual Menu Run | `isDelayedRun: boolean = false`<br>`targetStage: string = null` | The master multi-stage pipeline engine. Iterates through all rows in Post-Sales Tracker, evaluates milestone dates, consolidates multi-title authors, and generates Gmail drafts. When `targetStage` is passed (e.g. `'checkIn1'`), runs only that stage in complete isolation. |
| **`evaluateSingleRowCheckIns()`**<br>`[StageHandlers.gs]` | Called by `onEdit(e)` or Stage Handlers | `psSheet, row, preloadedRowVals = null, preloadedHeaders = null` | Evaluates Check-In 1 (15 Days) and Check-In 2 (30 Days) for a single specific row. Checks Col D Sept 1 cutoff, Col AB Launch status, and Col V/Col X date differences. Performs immediate cell updates and Gmail draft creation. |
| **`evaluateSingleRowLaunch()`**<br>`[StageHandlers.gs]` | Called by `onEdit(e)` or Stage Handlers | `psSheet, row, preloadedRowVals = null, preloadedHeaders = null` | Evaluates Show Launch Announcement for a single specific row. Applies the strict 4-point guard (valid Show ID, live Show Link, not unlaunched/dropped). Sets Col AB/AA to `'Draft Ready'` and generates launch draft. |
| **`syncSentEmails()` /<br>`syncSentEmailsNow()`**<br>`[DraftEngine.gs]` | Time-driven Trigger (Every 1 hr) or Menu `'Sync Sent Emails Now'` | None | Two-way Gmail sync engine. Scans Gmail Sent folder for hidden HTML tracking tokens. When an outreach draft is sent by a team member, reaches back into Google Sheet, flips dropdown from `'Draft Ready'` to `'Sent'`, and stamps sent date. |
| **`testAuthorCheckInTimers()`**<br>`[StageHandlers.gs]` | Apps Script Editor / Developer Test Suite | None | Automated 16-point unit test matrix covering all combinations of Check-In 1 and Check-In 2 (Sept 1 cutoff, Launch override, missing dates, diff < 15d, diff == 15d, diff >= 16d, already sent). Logs `[PASS]` for each test with 100% success. |
| **`testShowLaunchAnnouncement()`**<br>`[StageHandlers.gs]` | Apps Script Editor / Developer Test Suite | None | Runs TestCase A (Launch Date Anomaly, verifies draft suppressed) and TestCase B (Valid Launch, verifies draft generated) to validate Stage 7 integrity. |
| **`runAllOutreachAutomations()`**<br>`[Main.gs]` | Menu: Pocket FM Automation > `'▶️ Run All Automations at Once'` | None | Single-click master runner that executes all stages sequentially across all qualifying rows. |
| **`runWelcomeEmails()`**<br>`[Main.gs]` | Menu: Pocket FM Automation > `'1️⃣ Run Welcome Emails Only'` | None | Calls `processOutreachQueue(false, 'welcome')`. Evaluates only Stage 1 in isolation. |
| **`runVendorOnboarding()`**<br>`[Main.gs]` | Menu: Pocket FM Automation > `'2️⃣ Run Vendor Onboarding Only'` | None | Calls `processOutreachQueue(false, 'vendor')`. Evaluates only Stage 2 in isolation. |
| **`runMgPayoutInitiated()`**<br>`[Main.gs]` | Menu: Pocket FM Automation > `'3️⃣ Run MG Payout Initiated Only'` | None | Calls `processOutreachQueue(false, 'mgInitiated')`. Evaluates only Stage 3 in isolation. |
| **`runMgPayoutConfirmation()`**<br>`[Main.gs]` | Menu: Pocket FM Automation > `'4️⃣ Run MG Payout Confirmation Only'` | None | Calls `processOutreachQueue(false, 'mgConfirmed')`. Evaluates only Stage 4 in isolation. |
| **`runAuthorCheckIn1()`**<br>`[Main.gs]` | Menu: Pocket FM Automation > `'5️⃣ Run Author Check-In 1 (15 Days) Only'` | None | Calls `processOutreachQueue(false, 'checkIn1')`. Evaluates only Stage 5 in isolation. |
| **`runAuthorCheckIn2()`**<br>`[Main.gs]` | Menu: Pocket FM Automation > `'6️⃣ Run Author Check-In 2 (30 Days) Only'` | None | Calls `processOutreachQueue(false, 'checkIn2')`. Evaluates only Stage 6 in isolation. |
| **`runShowLaunch()`**<br>`[Main.gs]` | Menu: Pocket FM Automation > `'7️⃣ Run Show Launch Announcements Only'` | None | Calls `processOutreachQueue(false, 'launch')`. Evaluates only Stage 7 in isolation. |
| **`runNewsletter()`**<br>`[Main.gs]` | Menu: Pocket FM Automation > `'8️⃣ Run Newsletter Only'` | None | Calls `processOutreachQueue(false, 'newsletter')`. Evaluates only Stage 8 in isolation. |
| **`runRevenueStatements()`**<br>`[Main.gs]` | Menu: Pocket FM Automation > `'9️⃣ Run Quarterly Rev Statements (Worked Well)'` | None | Calls `processOutreachQueue(false, 'revStatement_workedWell')`. Evaluates Stages 9A & 9B. |
| **`runContentBadStatements()`**<br>`[Main.gs]` | Menu: Pocket FM Automation > `'🔟 Run Content Didn't Work Well Statements'` | None | Calls `processOutreachQueue(false, 'contentBad')`. Evaluates Stage 9C Sunset in isolation. |
| **`isDealSignedBeforeSept1()`**<br>`[Config.gs]` | Helper Utility Function | `dateVal: any` | Strict cutoff evaluator. Returns true if contract signing date is strictly before Sept 1, 2026 midnight local time (`cmp.getTime() < cutoff.getTime()`). |
| **`parseDateSafe()`**<br>`[Config.gs]` | Helper Utility Function | `val: any` | Universal date parser. Handles native Date objects, ISO strings, Excel timestamps, and timestamps with time components. Returns valid Date object or null. |
| **`isDaysAgoOrMore()`**<br>`[Config.gs]` | Helper Utility Function | `dateVal: any, nDays: number` | Calculates calendar days elapsed comparing target date at midnight to today at midnight. |
| **`isValidWebUrl()`**<br>`[Config.gs]` | Helper Utility Function | `url: string` | Validates that string begins with `http://` or `https://` and contains valid domain syntax. Rejects text placeholders like `'Show Untested'`. |
| **`isTrackerRowFilled()`**<br>`[Config.gs]` | Row Blank Guard | `rowVals: Array, titleCol: number = 2` | Strict row validator. Returns false if row is empty or Title / IP column is blank, preventing phantom drafts on unpopulated rows. |

---

### 4. How to Run & Verify Triggers in Google Sheets

1. **Top-Bar Custom Menu**:
   * Open the Google Sheet, navigate to the custom menu **`Pocket FM Automation`**.
   * Run any stage trigger directly in complete isolation (e.g. `5. Run Author Check-In 1`, `8. Run Newsletter`, `9. Run Revenue Statements`).
2. **Instant UI Dropdown Test**:
   * In **Post-Sales Tracker**, manually select `'Sent'` in **Column W**, **Column Y**, or **Column AB**.
   * Observe **Column X**, **Column Z**, or **Column AC** instantly auto-populate with today's date via `onEdit(e)` without page refresh.
3. **Automated Unit Testing**:
   * In **Extensions > Apps Script**, select `testAuthorCheckInTimers` or `testShowLaunchAnnouncement` from the function dropdown.
   * Click **Run** and view the Execution Log to verify all 16 test cases passing with 100% success.
4. **Gmail Verification**:
   * Navigate to **Gmail > Drafts** to inspect and dispatch the generated branded HTML drafts.
