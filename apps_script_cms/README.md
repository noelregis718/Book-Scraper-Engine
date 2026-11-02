# Pocket FM CMS Scraper & Data Manager (Apps Script Suite)

A complete, fully functional Google Apps Script suite built to connect, fetch, and manage live **Pocket FM CMS Show Metrics** directly within Google Sheets.

---

## 📁 Architecture Overview

| File (`.gs` / `.js`) | Module | Core Functionality |
| :--- | :--- | :--- |
| **`CmsConfig.gs`** | **Module 1: Config** | Standard column maps (`Show ID`, `Plays`, `Duration`, `Ratings`, etc.), sheet finders, metric cleaners, and secure `ScriptProperties` management. |
| **`CmsService.gs`** | **Module 2: CMS Service** | Direct HTTP connection via `UrlFetchApp` with session token/cookie headers, HTML/JSON metric extraction, and native `doPost` Webhook receiver. |
| **`CmsSyncEngine.gs`** | **Module 3: Sync Engine** | Central sheet writer, show matcher, full sheet batch sync runner, single show row updater, and Master Tracker show importer/auditor. |
| **`CmsMenu.gs`** | **Module 4: UI & Menus** | Adds the **`Pocket FM CMS Scraper`** menu to Google Sheets with interactive dialogs for 1-click sync, token setup, and audits. |

---

## 🚀 How to Install in Google Sheets (or Standalone Project)

### Option A: In a Standalone Project (New Link)
1. Open a browser and navigate to **[script.new](https://script.new)**.
2. Rename the project at top-left to **`Pocket FM CMS Scraper`**.
3. Create 4 script files:
   - `CmsConfig` (paste content from `CmsConfig.gs`)
   - `CmsService` (paste content from `CmsService.gs`)
   - `CmsSyncEngine` (paste content from `CmsSyncEngine.gs`)
   - `CmsMenu` (paste content from `CmsMenu.gs`)
4. Click **Save** (disk icon).

### Option B: Inside Your Google Spreadsheet Directly
1. Open your Google Spreadsheet (e.g. **Pocket FM Post-Sales Tracker**).
2. Go to **Extensions > Apps Script**.
3. Add the 4 files above and save. Reload the spreadsheet to see the menu.

---

## 🧭 Menu Features (`Pocket FM CMS Scraper`)

Once loaded, a new top menu **`Pocket FM CMS Scraper`** appears in Google Sheets:

* **`▶️ Sync All Shows from CMS`**: Loops across every Show ID in the `CMS Show Data` tab, pulls live metrics from Pocket FM CMS, and updates the rows in real-time.
* **`🎯 Sync Currently Selected Show`**: Instantly updates metrics for whichever row is currently clicked/highlighted.
* **`📥 Import Missing Shows from Tracker`**: Scans the Master Lifecycle Tracker / Post-Sales Tracker, detects any newly created Show IDs, and adds them into `CMS Show Data`.
* **`📊 Audit Shows Missing from CMS`**: Compares Master Tracker shows with CMS sheet and lists shows that don't have metrics yet.
* **`🔑 Set / Update CMS Session Token`**: Opens a secure prompt to paste your active Pocket FM session cookie or authorization token.
* **`👁️ Check CMS Auth Token Status`**: Verifies whether an active token is stored in Script Properties.
* **`🌐 View Webhook URL & Secret Key`**: Displays configuration details if you want external scrapers (e.g. Python Playwright) to push metrics directly to the sheet.
* **`🧹 Clean & Format CMS Sheet`**: Automatically applies Pocket FM crimson header formatting, aligns columns, and freezes the top row.

---

## 🔑 How to Set Up the CMS Session Token

Because Pocket FM CMS requires JumpCloud Single Sign-On (SSO):

1. Open **[cms.pocketfm.com](https://cms.pocketfm.com/)** in Google Chrome and log in via JumpCloud SSO.
2. Press **F12** (or Right Click $\rightarrow$ Inspect) to open Chrome DevTools.
3. Go to the **Application** tab $\rightarrow$ **Cookies** $\rightarrow$ `https://cms.pocketfm.com`.
4. Copy the session cookie (or from the **Network** tab, inspect any request and copy the `Authorization` or `Cookie` header).
5. In your Google Sheet, click **`Pocket FM CMS Scraper > 🔑 Set / Update CMS Session Token`**.
6. Paste the token and click **OK**. It is now securely saved in Google's cloud Script Properties.
7. Click **`▶️ Sync All Shows from CMS`** to update all show data directly!
