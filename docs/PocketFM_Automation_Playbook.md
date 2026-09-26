# PocketFM Audio Rights Outreach Automation Playbook

This document outlines the complete, end-to-end automation workflow for identifying, drafting, and sending personalized audio rights licensing emails to authors and agencies in bulk.

## Overview of the Engine
The automation consists of three phases that work together to prevent duplicate emails, personalize content, and safely blast emails in bulk:
1. **The Grouper (Google Apps Script):** Scans the `Lifecycle Tracker - Master` sheet, identifies books marked for outreach, and groups multiple books belonging to the same Agency into a single context string to prevent spamming.
2. **The Writer (GPT for Sheets):** Reads the context string and dynamically writes a perfectly customized, HTML-formatted email that distinguishes between direct authors and agencies.
3. **The Sender (GMass):** Pulls the final drafted text from the spreadsheet and sends them out individually.

---

## Phase 1: The Grouping Engine (Apps Script)

### How to Install:
1. Open your `Lifecycle Tracker - Master` Google Sheet.
2. Click **Extensions > Apps Script** in the top menu.
3. Delete any existing code and paste the script below.
4. Click the **Save** (floppy disk) icon.

### How to Automate it (Set it and forget it):
To make this run in the background without you having to click "Run":
1. In Apps Script, click the **Alarm Clock icon** (Triggers) on the left sidebar.
2. Click **+ Add Trigger**.
3. Settings:
   - Function to run: `processOutreachQueue`
   - Event source: `Time-driven`
   - Type of time-based trigger: `Hour timer`
   - Hour interval: `Every hour`
4. Click **Save**.

### The Apps Script Code:
```javascript
/**
 * POCKETFM AUTOMATED EMAIL BUNDLER
 */

function processOutreachQueue() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Lifecycle Tracker - Master");
  if (!sheet) return;
  
  const data = sheet.getDataRange().getValues();
  
  // Depending on your sheet, this is either 0 (Row 1) or 2 (Row 3)
  const headerRowIndex = 2; 
  const headers = data[headerRowIndex];
  
  const authorCol = headers.indexOf("Author Name");
  const titleCol = headers.indexOf("Title / IP");
  const licensorCol = headers.indexOf("Licensor (Legal name)");
  const statusCol = headers.indexOf("Status");
  
  if (authorCol === -1 || titleCol === -1 || licensorCol === -1 || statusCol === -1) return;
  
  let contextCol = headers.indexOf("AI_Context_Bundle");
  if (contextCol === -1) {
    contextCol = headers.length;
    sheet.getRange(headerRowIndex + 1, contextCol + 1).setValue("AI_Context_Bundle");
  }

  let outreachQueue = [];
  
  for (let i = headerRowIndex + 1; i < data.length; i++) {
    const status = data[i][statusCol];
    if (status && status.toString().trim() !== "") {
      outreachQueue.push({
        rowIndex: i,
        author: data[i][authorCol],
        title: data[i][titleCol],
        licensor: data[i][licensorCol]
      });
    }
  }
  
  if (outreachQueue.length === 0) return;
  
  let groupedByLicensor = {};
  outreachQueue.forEach(item => {
    if (!groupedByLicensor[item.licensor]) groupedByLicensor[item.licensor] = [];
    groupedByLicensor[item.licensor].push(item);
  });
  
  for (let licensor in groupedByLicensor) {
    let group = groupedByLicensor[licensor];
    let authors = group.map(g => g.author);
    let books = group.map(g => g.title);
    
    let uniqueAuthors = [...new Set(authors)];
    let isDirect = (uniqueAuthors.length === 1 && uniqueAuthors[0] === licensor);
    
    let context = "";
    
    if (isDirect && books.length === 1) {
      context = `Direct Author Outreach. Recipient: ${authors[0]}. Book to license: ${books[0]}.`;
    } 
    else if (!isDirect && books.length === 1) {
      context = `Agency Outreach. Recipient: ${licensor}. Author they represent: ${authors[0]}. Book to license: ${books[0]}.`;
    }
    else if (!isDirect && books.length > 1) {
      context = `Agency Outreach (Multiple Authors/Books). Recipient: ${licensor}. Books to license: `;
      for (let i = 0; i < books.length; i++) context += `'${books[i]}' by ${authors[i]}, `;
    }
    else if (isDirect && books.length > 1) {
      context = `Direct Author Outreach (Multiple Books). Recipient: ${authors[0]}. Books to license: `;
      for (let i = 0; i < books.length; i++) context += `'${books[i]}', `;
    }
    
    context = context.replace(/, $/, ".");
    
    let primaryRow = group[0].rowIndex;
    sheet.getRange(primaryRow + 1, contextCol + 1).setValue(context);
    
    for (let i = 1; i < group.length; i++) {
      let secondaryRow = group[i].rowIndex;
      sheet.getRange(secondaryRow + 1, contextCol + 1).setValue("Bundled with row " + (primaryRow + 1));
    }
  }
}
```

---

## Phase 2: The AI Email Generator (GPT for Sheets)

Once the `AI_Context_Bundle` is generated, we use the GPT for Sheets plugin to write the emails. 

**Setup:**
Create two new columns in your spreadsheet: `Final Draft Subject` and `Final Draft Email`.

### The Subject Line Prompt
Paste this formula into the first empty cell of the `Final Draft Subject` column (assuming your Context Bundle is in column **CA**) and drag it down:

```text
=IF(OR(CA4="", LEFT(CA4, 7)="Bundled"), "", GPT("Context: " & CA4 & " Task: Write a short, professional email subject line for this context. Do not use quotes."))
```

### The Email Body Prompt
Paste this formula into the first empty cell of the `Final Draft Email` column and drag it down. *(Make sure to replace John Doe with your manager's actual details!)*

```text
=IF(OR(CA4="", LEFT(CA4, 7)="Bundled"), "", GPT("Context: " & CA4 & " Task: Write a highly personalized audio rights licensing email. Rule 1: Read the context. If it is an agency, start with 'Dear [Agency Name]'. If it is a direct author, start with 'Dear [Author Name]'. Rule 2: You MUST mention the specific Book title(s) listed in the context. Rule 3: NEVER use placeholders or brackets—use the actual names from the context. Rule 4: You MUST use HTML <br><br> tags to separate your paragraphs instead of normal line breaks. Rule 5: Sign off as John Doe, Head of Licensing, PocketFM."))
```

---

## Phase 3: The Bulk Sender (GMass)

The final step is to blast the perfectly drafted emails to the recipients without triggering spam filters.

### Steps to Send:
1. Open your PocketFM Gmail account.
2. Click the red **GMass Spreadsheet button** near the top search bar.
3. Select your `Lifecycle Tracker - Master` sheet from the dropdown menu and click **Connect**.
4. In the GMass compose window:
   - Click into the **Subject** line and type EXACTLY: `{Final Draft Subject}`
   - Click into the **Main Body** (the large white box) and type EXACTLY: `{Final Draft Email}`
5. Click the red **GMass Send Button** at the bottom left.

**Why it works:** GMass will automatically skip the rows that were left blank by the `=IF()` statement (the bundled books), ensuring that Agencies receive only ONE beautifully formatted email containing the grouped list of books you want to license!
