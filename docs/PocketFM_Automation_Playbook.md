# PocketFM Post-Sales CRM Automation Playbook

This document outlines the complete, end-to-end automation workflow for identifying milestones in the `Lifecycle Tracker - Master` and `Post-Sales Tracker` and automatically generating fully formatted HTML email drafts for authors.

## Overview of the Engine
The automation consists of real-time event listeners, background orchestrators, and two-way sync engines:
1. **The Drafter (`processOutreachQueue`):** Scans the trackers for milestone dates and dynamically drafts perfectly formatted HTML emails across all 11 stages (Welcome, Vendor, MG Payouts, Check-In 1, Check-In 2, Show Launch, Newsletter, and Quarterly Statements).
2. **Instant UI Sync (`onEdit`):** Automatically detects when a team member flips Column W, Column Y, or Column AB to `"Sent"` in Google Sheets and instantly stamps Column X, Column Z, or Column AC with today's date.
3. **The Sync Engine (`syncSentEmails`):** Scans your Gmail "Sent" folder every hour looking for invisible tracking codes. When it finds that you actually clicked "Send" on a draft, it reaches back into the tracker, flips the dropdown from `"Draft Ready"` to `"Sent"`, and logs the sent timestamp.

---

## The 11 Stage Trigger Conditions Table

| Stage | Email Type | Active Column in Post-Sales Tracker | Reference Anchor | Conditions & Timing Rules |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **Welcome Email** | **Col R (18)**: `Welcome Email` | Col Q / Col D (`Contract Date`) | `Contract Date == TODAY` & Status != Dropped/Bad. Authors with 2+ titles signed on the same date receive 1 consolidated draft. |
| **2** | **Vendor Onboarding** | **Col S (19)**: `Vendor Onboarding Email` | Col Q / Col D (`Contract Date`) | `Contract Date == TODAY` (Sent same day as Welcome Email so author can complete Netsuite). |
| **3** | **MG Payment Initiated** | **Col T (20)**: `MG Payout Initiated` | Master Col U (`Vendor Exited`) | `Vendor Exited Date == TODAY` & Vendor Status == `'Done'`. |
| **4** | **MG Payment Processed** | **Col U (21)**: `MG Payout Confirmation` | Master Col X (`MG Exited`) | `MG Exited Date == TODAY` & MG Status == `'Done'`. Stamped into **Col V (`Feedback Mail Date`)**. |
| **5** | **Author Check-In 1** | **Col W (23)**: `Author Check-In (15 Days)` | **Col V (22)** (`Feedback Mail Date`) | • Contract Date >= Sept 1, 2026 (if before $\rightarrow$ `Does not apply`)<br>• Col AB Launch Sent != Sent (if sent $\rightarrow$ `Does not apply`)<br>• Diff == 15 days $\rightarrow$ `draft ready`<br>• Diff < 15 days $\rightarrow$ `Not due yet`<br>• Diff >= 16 days $\rightarrow$ `Overdue` (No draft created).<br>• Auto-stamped in **Col X** when marked Sent. |
| **6** | **Author Check-In 2** | **Col Y (25)**: `Author Check-In (30 Days)` | **Col X (24)** (`Author Check-In 1 DATE`) | • Contract Date >= Sept 1, 2026 (if before $\rightarrow$ `Does not apply`)<br>• Col AB Launch Sent != Sent (if sent $\rightarrow$ `Does not apply`)<br>• If Col X missing $\rightarrow$ `Not due yet`<br>• Diff == 15 days from Col X $\rightarrow$ `draft ready`<br>• Diff < 15 days $\rightarrow$ `Not due yet`<br>• Diff >= 16 days $\rightarrow$ `Overdue` (No draft created).<br>• Auto-stamped in **Col Z** when marked Sent. |
| **7** | **Show Launch Announcement** | **Col AB (28)**: `Show Launch Sent?` | Master Col Y & Col AG | Strict 4-point guard: Valid Show ID + Live Show Link URL + Col AA/AB != Not launched/Unavailable/Discontinued + Status != Dropped/Bad. Auto-stamped in **Col AC** when Sent. |
| **8** | **Newsletter (Author Edit)** | **Col AD (30)**: `Newsletter Edit` | **Col AC (29)** (`Launch Email Sent Date`) | **Strictly Col AC Date >= 15 Days Ago** & Col AC not blank. Ignores Col J Launch Date. Active live Show Link required. |
| **9A**| **Rev Statement: Content Update** | **Col AM (39)**: `Rev Statement Sent?` | Col AL Drive Link + Argus Tab | Launch Status in `Testing/Launched`. Strictly requires valid URL in Col AL. Injects Argus metrics into draft. |
| **9B**| **Rev Statement: Payment Ready** | **Col AM (39)**: `Rev Statement Sent?` | Col AL Drive Link | Launch Status in `Testing/Launched`. Strictly requires valid URL in Col AL. |
| **9C**| **Rev Statement: Sunset / Dropped** | **Col AM (39)**: `Rev Statement Sent?` | Col AL Drive Link | Launch Status in `Dropped/Bad/Discontinued`. Strictly requires valid URL in Col AL. Mutually exclusive from 9A/9B. |

---

## Complete Catalog of Functions

### 1. Real-Time UI Trigger Functions
* **`onEdit(e)`**: Simple trigger in `Main.gs`. Listens for edits in `Post-Sales Tracker`. When Col W, Col Y, or Col AB is changed to `"Sent"`, immediately writes `new Date()` into Col X, Col Z, or Col AC, and calls `SpreadsheetApp.flush()`.
* **`evaluateSingleRowCheckIns(psSheet, row)`**: Evaluates Check-In 1 & Check-In 2 for a single edited row.
* **`evaluateSingleRowLaunch(psSheet, row)`**: Evaluates Show Launch Announcement for a single edited row.

### 2. Workflow Orchestrator Functions
* **`processOutreachQueue(isDelayedRun, targetStage)`**: Core multi-stage batch runner in `StageHandlers.gs`. Evaluates milestone dates, groups multi-title authors, and creates Gmail drafts. Pass `targetStage` (e.g. `'welcome'`, `'checkIn1'`, `'launch'`) to execute that stage in isolation.
* **`syncSentEmails()` / `syncSentEmailsNow()`**: Two-way sync engine in `DraftEngine.gs`. Detects sent drafts in Gmail and marks corresponding sheet dropdowns as `"Sent"`.
* **`runAllOutreachAutomations()`**: Master runner in `Main.gs` executed from the custom Google Sheets menu.

### 3. Dedicated Stage Runners (Google Sheets Menu & Apps Script)
* `runWelcomeEmails()` $\rightarrow$ Stage 1 Welcome Emails Only
* `runVendorOnboarding()` $\rightarrow$ Stage 2 Vendor Onboarding Only
* `runMgPayoutInitiated()` $\rightarrow$ Stage 3 MG Payout Initiated Only
* `runMgPayoutConfirmation()` $\rightarrow$ Stage 4 MG Payout Confirmation Only
* `runAuthorCheckIn1()` $\rightarrow$ Stage 5 Author Check-In 1 (15 Days) Only
* `runAuthorCheckIn2()` $\rightarrow$ Stage 6 Author Check-In 2 (30 Days) Only
* `runShowLaunch()` $\rightarrow$ Stage 7 Show Launch Announcements Only
* `runNewsletter()` $\rightarrow$ Stage 8 Newsletter (The Author Edit) Only
* `runRevenueStatements()` $\rightarrow$ Stage 9 Worked Well Statements Only
* `runContentBadStatements()` $\rightarrow$ Stage 10 / 9C Sunset Statements Only

### 4. Automated Testing & Verification Functions
* **`testAuthorCheckInTimers()`**: Runs the 16-point unit test matrix validating all 15-day and 30-day conditions (Sept 1 cutoff, Launch sent override, missing dates, exact 15-day draft ready, and overdue status).
* **`testShowLaunchAnnouncement()`**: Tests launch date anomaly suppression vs valid live launch draft generation.
* **`testDidnWorkWellDraft()`**: Dispatches a sample test sunset draft directly to Gmail.
* **`testNewsletterDraft()`**: Dispatches a sample test newsletter draft directly to Gmail.

### 5. Utility & Helper Functions
* `isDealSignedBeforeSept1(dateVal)`: Strict cutoff check (`< 2026-09-01`).
* `parseDateSafe(val)`: Bulletproof date parser handling Date objects, ISO strings, Excel timestamps, and timestamps with time components.
* `isDaysAgoOrMore(dateVal, nDays)`: Calculates elapsed calendar days comparing midnight-to-midnight.
* `isValidWebUrl(url)`: Validates that a string is a real web URL (`http://` or `https://`).
* `isTrackerRowFilled(rowVals, titleCol)`: Strict row blank guard to prevent empty rows from triggering false drafts.

---

## Trigger Configuration in Google Apps Script

To make the engine run completely autonomously in the background:
1. In the Apps Script editor, click the **Alarm Clock icon** (Triggers) on the left sidebar.
2. Add **Trigger 1**:
   * Function: `processOutreachQueue`
   * Event source: `Time-driven`
   * Type: `Hour timer`
   * Interval: `Every 4 hours`
3. Add **Trigger 2**:
   * Function: `syncSentEmails`
   * Event source: `Time-driven`
   * Type: `Hour timer`
   * Interval: `Every hour`
