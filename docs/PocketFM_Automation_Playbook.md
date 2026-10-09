# PocketFM Post-Sales CRM Automation Playbook

This document outlines the complete, end-to-end automation workflow for identifying milestones in the `Lifecycle Tracker - Master` and `Post Sale Comms Tracker` and automatically generating fully formatted HTML email drafts for authors.

## Overview of the Engine
The automation consists of two main functions that work together to track dates, draft emails, and log when emails are actually sent:
1. **The Drafter (`processOutreachQueue`):** Scans the trackers for milestone dates (e.g., 15 Days after MG Payout, Today is Rev Statement Due Date) and dynamically drafts perfectly formatted HTML emails (Welcome, Vendor, Launch, Quarterly Statements).
2. **The Sync Engine (`syncSentEmails`):** Scans your Gmail "Sent" folder every hour looking for our invisible tracking codes. When it finds that you actually clicked "Send" on a draft, it reaches back into the tracker and changes the status from "Sent" (meaning drafted) to "Yes" or marks it fully completed.

---

## Installation & Setup

### 1. The Apps Script Code
1. Open your Google Sheet (`Lifecycle Tracker - Master`).
2. Click **Extensions > Apps Script**.
3. Delete the existing code and paste the completely updated `apps_script_drafter.js` code.
4. Click the **Save** (floppy disk) icon.

*(Note: The script is hardcoded to connect to the main production Sheet ID: `1A1vJ0DsmDxtCFZiuyu6vtuQFWqClPyK7e1_lHKddGdQ`)*

---

## Trigger Configuration (Set it and forget it)

To make the engine run completely autonomously in the background without you having to click "Run":

1. In the Apps Script editor, click the **Alarm Clock icon** (Triggers) on the left sidebar.
2. You will need to add **TWO** triggers.

### Trigger 1: The Drafter
1. Click **+ Add Trigger**.
2. **Function to run:** `processOutreachQueue`
3. **Event source:** `Time-driven`
4. **Type of time-based trigger:** `Hour timer`
5. **Hour interval:** `Every 4 hours` *(Or Every hour based on your preference)*
6. Click **Save**.

### Trigger 2: The Sync Engine
1. Click **+ Add Trigger**.
2. **Function to run:** `syncSentEmails`
3. **Event source:** `Time-driven`
4. **Type of time-based trigger:** `Hour timer`
5. **Hour interval:** `Every hour`
6. Click **Save**.

---

## How the Triggers Work (The Rules)

The script relies on specific columns and exact date/status combinations to determine whether an email should be drafted.

### 1. Welcome Email
- **Condition:** The `Contract Signing date` in the Master sheet is **Today**.
- **Action:** Drafts the Welcome email. Updates the Post-Sales tracker status to `Sent`.

### 2. Vendor Onboarding Email
- **Condition:** The `Contract Signing date` is **2 Days Ago**.
- **Action:** Drafts the Vendor email instructing the author to complete onboarding.

### 3. MG Payout Initiated
- **Condition:** The `Vendor Lifecycle Exited` date in the Master sheet is **Today**.
- **Action:** Drafts the MG Initiated email.

### 4. MG Payout Confirmation
- **Condition:** The `MG Payout Exited` date in the Master sheet is **Today**.
- **Action:** Drafts the payment confirmation email.

### 5. Author Check-In (15 Days)
- **Condition:** The `MG Payout Exited` date is exactly **15 Days Ago**.
- **Requirement:** The `Show ID` column must still be **blank**.
- **Action:** Drafts a check-in email asking the author for world-building insights.

### 6. Show Launch Announcement
- **Condition:** The `Show Launch Announcement Status` is marked as `Ready` (or blank).
- **Requirement:** The `Show ID (after show creation)` column has a valid link.
- **Action:** Drafts the official Launch Announcement. Also automatically sets the `Show Launch Announcement Email Sent?` dropdown to `Yes`.

### 7. Quarterly Revenue Statements
- **Condition:** The `Rev Statement Due Date` is **Today**.
- **Requirement:** The `Launch Status` in the Master Sheet or Post-Sales Sheet must be either `testing_pgc` or `launched`.
- **Requirement:** The `Revenue Statement + Insights Email Status` must contain the word `Eligible`.
- **Data Integration:** Pulls live metrics (Duration, LDAU, Comments, Ratings, Reviews) dynamically from the `Argus Show Data` tab using the Show ID. If the Show ID doesn't match, it safely falls back to `[Insert...]` placeholders.
- **Action:** Drafts the "Content Update" email containing the Quarterly Statement Drive link.

---

## Data Integration Notes
* The script perfectly maps data from the **Lifecycle Tracker - Master**, **Post Sale Comms Tracker**, and **Argus Show Data**.
* **Argus Matching:** If you ever see `[Insert...]` in your drafts instead of real numbers, it means the `Show ID` is missing from the Master tracker, or the exact Show ID doesn't exist in the Argus tab.
