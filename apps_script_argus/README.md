# Pocket FM Argus CMS Scraper & Data Manager (Apps Script Suite)

A complete, fully functional Google Apps Script suite built to connect, fetch, and manage live **Pocket FM CMS Show Metrics** directly within Google Sheets.

---

## 📁 Architecture Overview

| File (`.gs` / `.js`) | Module | Core Functionality |
| :--- | :--- | :--- |
| **`ArgusConfig.gs`** | **Module 1: Config** | Standard column maps (`Show ID`, `Plays`, `Duration`, `Ratings`, etc.), sheet finders, metric cleaners, and secure `ScriptProperties` management. |
| **`ArgusService.gs`** | **Module 2: CMS Service** | Direct HTTP connection via `UrlFetchApp` with session token/cookie headers, HTML/JSON metric extraction, and native `doPost` Webhook receiver. |
| **`ArgusSyncEngine.gs`** | **Module 3: Sync Engine** | Central sheet writer, show matcher, full sheet batch sync runner, single show row updater, and Master Tracker show importer/auditor. |
| **`ArgusMenu.gs`** | **Module 4: UI & Menus** | Adds the **`Pocket FM Argus Scraper`** menu to Google Sheets with interactive dialogs for 1-click sync, token setup, and audits. |

---

## 🚀 How to Install in Google Sheets

1. Open your Google Spreadsheet (e.g. **Pocket FM Post-Sales Tracker** or **US Licensing Lifecycle Tracker**).
2. Go to **Extensions > Apps Script**.
3. Create 4 script files in Apps Script editor:
   - `ArgusConfig` (paste content from `ArgusConfig.gs`)
   - `ArgusService` (paste content from `ArgusService.gs`)
   - `ArgusSyncEngine` (paste content from `ArgusSyncEngine.gs`)
   - `ArgusMenu` (paste content from `ArgusMenu.gs`)
4. Click **Save** (disk icon).
5. Reload your Google Spreadsheet.

---

## 🧭 Menu Features (`Pocket FM Argus Scraper`)

Once loaded, a new top menu **`Pocket FM Argus Scraper`** appears in Google Sheets:

* **`▶️ Sync All Shows from CMS`**: Loops across every Show ID in the `Argus Show Data` tab, pulls live metrics from Pocket FM CMS, and updates the rows in real-time.
* **`🎯 Sync Currently Selected Show`**: Instantly updates metrics for whichever row is currently clicked/highlighted.
* **`📥 Import Missing Shows from Tracker`**: Scans the Master Lifecycle Tracker / Post-Sales Tracker, detects any newly created Show IDs, and adds them into `Argus Show Data`.
* **`📊 Audit Shows Missing from Argus`**: Compares Master Tracker shows with Argus and lists shows that don't have metrics yet.
* **`🔑 Set / Update CMS Session Token`**: Opens a secure prompt to paste your active Pocket FM session cookie or authorization token.
* **`👁️ Check CMS Auth Token Status`**: Verifies whether an active token is stored in Script Properties.
* **`🌐 View Webhook URL & Secret Key`**: Displays configuration details if you want external scrapers (e.g. Python Playwright) to push metrics directly to the sheet.
* **`🧹 Clean & Format Argus Sheet`**: Automatically applies Pocket FM crimson header formatting, aligns columns, and freezes the top row.

---

## 🔑 How to Set Up the CMS Session Token

Because Pocket FM CMS requires JumpCloud Single Sign-On (SSO):

1. Open **[cms.pocketfm.com](https://cms.pocketfm.com/)** in Google Chrome and log in via JumpCloud SSO.
2. Press **F12** (or Right Click $\rightarrow$ Inspect) to open Chrome DevTools.
3. Go to the **Application** tab $\rightarrow$ **Cookies** $\rightarrow$ `https://cms.pocketfm.com`.
4. Copy the session cookie (or from the **Network** tab, inspect any request and copy the `Authorization` or `Cookie` header).
5. In your Google Sheet, click **`Pocket FM Argus Scraper > 🔑 Set / Update CMS Session Token`**.
6. Paste the token and click **OK**. It is now securely saved in Google's cloud Script Properties.
7. Click **`▶️ Sync All Shows from CMS`** to update all show data directly!

---

## 🔗 Connection with Stage 9 / Outreach Automation

The `Argus Show Data` tab updated by this script directly powers:
- **Stage 9A**: Content Review / Worked Well updates (injects `Plays`, `Duration Produced`, `Ratings`, `Reviews`, `Comments`).
- **Stage 9B**: Worked Well Payment drafts.
- **Stage 9C**: Didn't Work Well (Dropped / Bad / Sunset) drafts.
- **Stage 7**: Show Launch Announcements.

