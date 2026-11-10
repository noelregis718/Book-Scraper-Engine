# Pocket FM Automated Revenue Statement Generator

Automate quarterly and 6-month revenue statement generation directly inside **Google Sheets**. Colleagues never need to edit HTML, touch a terminal, or manually upload files.

---

## 🚀 How It Works for Colleagues

1. **Enter / Verify Data in Google Sheets**:
   * Colleagues work inside the **Post-Sales Tracker** tab as usual.
   * Ensure Title (Col C), Author (Col B), and reporting numbers are filled.
2. **Click the Custom Menu Button**:
   * At the top of Google Sheets, click:
     **`📊 Pocket FM Statements` ➔ `▶ Generate Statement for Active Row`**
     *(Or click `⚡ Generate All Missing Statements (Batch)` to generate for all authors at once)*
3. **Automated Magic (Runs in 2 seconds)**:
   * Reads the show's title, author, period, plays, listeners, and financial data.
   * Injects the data into the branded Pocket FM statement template.
   * Saves the statement directly into a Google Drive folder (`Pocket FM Revenue Statements`).
   * Sets permission to *"Anyone with the link can view"*.
   * **Automatically pastes the shareable link directly into Column AL (Revenue Statement Link).**
4. **Outreach Email Integration (Stage 9)**:
   * `StageHandlers.gs` automatically detects the new link in Column AL and prepares the author email draft immediately!

---

## 📦 What's Inside This Folder

* **[`RevenueStatementGenerator.gs`](RevenueStatementGenerator.gs)**: The complete Google Apps Script code to paste into your Google Apps Script editor.
* **[`StatementTemplate.html`](StatementTemplate.html)**: The official Pocket FM statement HTML template (matching the high-fidelity branding, Pocket FM logo, financial table, and PDF download button).

---

## 🛠️ 1-Minute Setup Guide for Colleagues

1. Open your Google Spreadsheet:
   [Pocket FM Deal Tracker](https://docs.google.com/spreadsheets/d/1JFT4_f9Du6UZWi6aM0FjYvyR-mcAsbARq7JyxJwLPZc/edit)
2. In the top menu, go to **Extensions ➔ Apps Script**.
3. In the left panel under **Files**, click the **`+`** icon and select **Script**.
4. Name the new file: **`RevenueStatementGenerator`**.
5. Copy all the code from [`RevenueStatementGenerator.gs`](RevenueStatementGenerator.gs) and paste it into the editor.
6. Press **Ctrl + S** (or Cmd + S) to save.
7. Refresh your Google Spreadsheet tab!
8. You will now see the new menu: **`📊 Pocket FM Statements`** at the top of your sheet.

---

## 📋 Features & Safeguards

* **Single-Row & Bulk Processing**: Generate a statement for one specific row, or batch-generate for all rows missing a link.
* **Interactive Preview**: Use `🔍 Preview Statement in Dialog` to review how the statement looks before saving it.
* **Automatic Financial Calculations**:
  * Revenue Share = `Gross Revenue × 15%`
  * Recouped MG = `Max(0, MG Paid - Revenue Share)`
  * Final Payout = `Max(0, Revenue Share - MG Paid)`
* **Intelligent Period Detection**: Automatically determines whether a show is 6-Month Combined or 3-Month Quarterly and formats the header accordingly.
* **Direct Column AL Integration**: Directly populates the approved Column AL (`revLinkCol`), fully enabling Stage 9 (`revStatement_workedWell` / `revStatement_didntWorkWell`) to generate email drafts without any errors.

