# PocketFM Post-Sales CRM Automation Playbook

This document outlines the complete, end-to-end automation workflow for identifying milestones in the `Lifecycle Tracker - Master` and `Post-Sales Tracker` and automatically generating fully formatted HTML email drafts for authors.

## Overview of the Engine
The automation consists of two main functions that work together to track dates, draft emails, and log when emails are actually sent:
1. **The Drafter (`processOutreachQueue`):** Scans the trackers for milestone dates and dynamically drafts perfectly formatted HTML emails (Welcome, Vendor, Check-Ins, Launch, Newsletter, Quarterly Statements).
2. **The Sync Engine (`syncSentEmails`):** Scans your Gmail "Sent" folder looking for tracking codes. When you send a draft from Gmail, it syncs back to the tracker and marks the status as "Sent" and stamps the sent date.

---

## Installation & Setup

### 1. The Apps Script Code
1. Open your Google Sheet (`Lifecycle Tracker - Master` / `Post-Sales Tracker`).
2. Click **Extensions > Apps Script**.
3. Create 5 script files in the Apps Script editor:
   - `Config.gs`
   - `Templates.gs`
   - `DraftEngine.gs`
   - `StageHandlers.gs`
   - `Main.gs`
   *(Source code available in `apps_script/` or single-file fallback `docs/apps_script_drafter.js`).*
4. Click the **Save** (floppy disk) icon.

*(Note: The script is configured for the production Sheet ID: `1JFT4_f9Du6UZWi6aM0FjYvyR-mcAsbARq7JyxJwLPZc`)*

---

## Trigger Configuration (Set it and forget it)

To make the engine run autonomously in the background:

1. **Via Spreadsheet Menu:** Use **`Pocket FM Automation`** in the top menu bar to run any stage in isolation, or click:
   - **`⏰ Enable Daily Outreach Automation (Every Morning 9 AM)`**
   - **`⚡ Enable Auto-Sync Sent Emails (Every 1 Min)`**
2. **Via Apps Script Triggers Sidebar:**
   - **Trigger 1 (The Drafter):** Function `processOutreachQueue` | Event: `Time-driven` | `Day timer` (or `Hour timer`).
   - **Trigger 2 (The Sync Engine):** Function `syncSentEmails` | Event: `Time-driven` | `Minute timer (Every 1-5 mins)`.

---

## How the Triggers Work (The Rules)

The script relies on specific columns and exact date/status combinations to determine whether an email should be drafted or marked Overdue.

### 1. Welcome Email
- **Conditions:**
  - `Contract Signing date` is **Today** & not sent -> Drafts Welcome email (`Col R -> draft ready`).
  - `Contract Signing date` is **in the past (< TODAY)** & not sent -> Sets `Col R -> Overdue`.
  - `Status` != Dropped / Bad.
- **Action:** Introduces author to Pocket FM workflow.

### 2. Vendor Onboarding Email
- **Conditions:**
  - `Contract Signing date` is **Today** & not sent -> Drafts Vendor Onboarding email (`Col S -> draft ready`).
  - `Contract Signing date` is **in the past (< TODAY)** & not sent -> Sets `Col S -> Overdue`.
  - `Status` != Dropped / Bad.
- **Action:** Dispatches onboarding packet and invoice requirements.

### 3. MG Payout Initiated
- **Automatic Prerequisite:** When Welcome Email (Col R) and Vendor Onboarding Email (Col S) are both `Sent`, Col T is automatically set to `Not due yet` until milestone dates are reached.
- **Conditions:**
  - `Vendor Lifecycle Exited` date is **Today** & `Vendor Status` == `Done` -> Drafts MG Initiated email (`Col T -> draft ready`).
  - `Vendor Lifecycle Exited` date is **in the past (< TODAY)** & `Vendor Status` == `Done` & not sent -> Sets `Col T -> Overdue`.
  - `Status` != Dropped / Bad.
- **Action:** Notifies author that NetSuite bill has been approved.

### 4. MG Payout Confirmation
- **Automatic Prerequisite:** When Welcome Email (Col R) and Vendor Onboarding Email (Col S) are both `Sent`, Col U is automatically set to `Not due yet` until milestone dates are reached.
- **Conditions:**
  - `MG Payout Exited` date is **Today** & `MG Status` == `Done` -> Drafts MG Confirmed email (`Col U -> draft ready`), stamps `Col V` with Today's Date (*Feedback Mail Date*).
  - `MG Payout Exited` date is **in the past (< TODAY)** & `MG Status` == `Done` & not sent -> Sets `Col U -> Overdue`.
  - `Status` != Dropped / Bad.
- **Action:** Confirms remittance and stamps `Col V` Feedback Mail Date.

### 5. Author Check-In 1 (15 Days)
- **Base Reference Date:** `Col V` (*Author Feedback Call Sent Date*).
- **Conditions:**
  - If contract was signed before **1st September** -> `Col W -> Does not apply`.
  - If `Show Launch Announcement` is `Sent` (Col AA/AB) -> `Col W -> Does not apply`.
  - If `Col V` is blank OR `diffDays < 15` -> `Col W -> Not due yet`.
  - If exact 15th day (`diffDays === 15` from Col V) -> Drafts check-in email (`Col W -> draft ready`). Subject: *"We'd love your thoughts on [Title]"*.
  - If 16+ days passed (`diffDays >= 16`) & not sent -> `Col W -> Overdue` (no catch-up draft).
- **Action:** Gathers initial creative feedback. When email is sent from Gmail, stamped with date in **Col X**.

### 6. Author Check-In 2 (30 Days)
- **Base Reference Date:** `Col X` (*Author Check-In 1 Sent Date*).
- **Conditions:**
  - If contract was signed before **1st September** -> `Col Y -> Does not apply`.
  - If `Show Launch Announcement` is `Sent` (Col AA/AB) -> `Col Y -> Does not apply`.
  - If `Col X` is blank OR `diffDays < 30` -> `Col Y -> Not due yet`.
  - If exact 30th day (`diffDays === 30` from Col X) -> Drafts check-in email (`Col Y -> draft ready`). Subject: *"Pocket FM: A quick update on your show: [Title]"*.
  - If 31+ days passed (`diffDays >= 31`) & not sent -> `Col Y -> Overdue` (no catch-up draft).
- **Action:** Follow-up production check-in. When email is sent from Gmail, stamped with date in **Col Z**.

### 7. Show Launch Announcement
- **Conditions:**
  - Both `Show ID` and `Show Link` must be present and valid (active URL starting with `http` or `pocketfm`).
  - `Col AA / AB` is NOT "Not launched", "Not live", or "Unavailable".
  - `Status` != Dropped / Bad.
- **Action:** Drafts official Launch Announcement (*"Your Pocket FM Show Is Now Live"*). Sets `Col AB -> Draft Ready`. Stamped with date in `Col AC` when sent.

### 8. Newsletter (The Author Edit)
- **Conditions:**
  - Base Date: `Col AC` (*Show Launch Announcement Sent Date*) is **15 Days Ago (`diffDays >= 15`)**. *(Strictly ignores Col J).*
  - `Show Link` is an active live URL.
  - `Col AD` is not already `Sent` or `Draft Ready`.
- **Action:** Drafts creator community newsletter (*"What's new at Pocket FM + a few things worth knowing"*). Sets `Col AD -> Draft Ready`.

### 9. Quarterly Revenue Statements
- **Revenue Statement Engine & Portal:** Generates confidential branded statements hosted live on Vercel (`https://pocketfm-statements.vercel.app`), accessible via the [Internal Statement Hub](https://pocketfm-statements.vercel.app/internal_hub).
- **9A (Worked Well - Content Review):**
  - `Launch Status` is `Testing_PGC` / `Launched (ROW)`.
  - Automatically drafted during standard outreach runs.
  - Requires a valid Revenue Statement Link in `Col AL` (suppressed if blank).
  - Drafts Content Review email with Argus performance snapshot. Updates `Col AM -> Draft Ready`.
- **9B (Worked Well - Payment Ready):**
  - `Launch Status` is `Testing_PGC` / `Launched (ROW)`.
  - **Decoupled from standard runs:** Triggered only when royalties are payable post-MG recoupment (or when explicitly selected from the menu), preventing premature invoice requests to authors.
  - Drafts Payment Ready email. Updates `Col AM -> Draft Ready`.
- **9C (Content Didn't Work Well):**
  - `Launch Status` is `Dropped` / `Bad` / `Sunset`.
  - Requires a valid Revenue Statement Link in `Col AL` (suppressed if blank).
  - Drafts Sunset Update email. Updates `Col AM -> Draft Ready`.

---

## Data Integration Notes
* The script maps data from **`Lifecycle Tracker - Master`**, **`Post-Sales Tracker`**, and **`Argus Show Data`**.
* **Argus Matching:** If you see `[Insert...]` in your drafts, the `Show ID` is missing from the tracker or does not exist in the Argus tab.
