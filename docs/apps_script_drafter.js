/**
 * POCKETFM AUTOMATED EMAIL BUNDLER
 * 
 * Instructions:
 * 1. Open your Google Sheet ("Lifecycle Tracker - Master")
 * 2. Click on "Extensions" in the top menu, then click "Apps Script"
 * 3. Delete any code there, and paste this entire file.
 * 4. Click the "Save" icon (the floppy disk).
 * 5. Click the "Run" button at the top!
 */

function processOutreachQueue() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Lifecycle Tracker - Master");
  
  // If sheet isn't found, stop
  if (!sheet) {
    Logger.log("Error: Could not find sheet 'Lifecycle Tracker - Master'");
    return;
  }
  
  const data = sheet.getDataRange().getValues();
  
  // Assuming Row 1 is the Header (Index 0 in 0-indexed arrays)
  const headerRowIndex = 0; 
  const headers = data[headerRowIndex];
  
  // Find column indexes
  const authorCol = headers.indexOf("Author Name");
  const titleCol = headers.indexOf("Title / IP");
  const licensorCol = headers.indexOf("Licensor (Legal name)");
  const statusCol = headers.indexOf("Status");
  
  if (authorCol === -1 || titleCol === -1 || licensorCol === -1 || statusCol === -1) {
    Logger.log("Error: Missing required columns (Author Name, Title / IP, Licensor (Legal name), Status)");
    return;
  }
  
  // Check if AI_Context_Bundle column exists, if not, create it
  let contextCol = headers.indexOf("AI_Context_Bundle");
  if (contextCol === -1) {
    contextCol = headers.length;
    sheet.getRange(headerRowIndex + 1, contextCol + 1).setValue("AI_Context_Bundle");
  }

  // Step 1: Collect all rows that are "Ready for Outreach"
  let outreachQueue = [];
  
  for (let i = headerRowIndex + 1; i < data.length; i++) {
    const status = data[i][statusCol];
    // Trigger for ANY status that is filled out (In Progress, Done, Ready for Outreach, etc)
    if (status && status.toString().trim() !== "") {
      outreachQueue.push({
        rowIndex: i,
        author: data[i][authorCol],
        title: data[i][titleCol],
        licensor: data[i][licensorCol]
      });
    }
  }
  
  if (outreachQueue.length === 0) {
    Logger.log("No rows found with Status 'Ready for Outreach'");
    return;
  }
  
  // Step 2: Group by Licensor (Agency)
  let groupedByLicensor = {};
  
  outreachQueue.forEach(item => {
    if (!groupedByLicensor[item.licensor]) {
      groupedByLicensor[item.licensor] = [];
    }
    groupedByLicensor[item.licensor].push(item);
  });
  
  // Step 3: Process Groups and Determine Scenarios
  for (let licensor in groupedByLicensor) {
    let group = groupedByLicensor[licensor];
    
    let authors = group.map(g => g.author);
    let books = group.map(g => g.title);
    
    let uniqueAuthors = [...new Set(authors)];
    let isDirect = (uniqueAuthors.length === 1 && uniqueAuthors[0] === licensor);
    
    let scenario = 2; // Default
    let context = "";
    
    if (isDirect && books.length === 1) {
      scenario = 1;
      context = `Direct Author Outreach. Recipient: ${authors[0]}. Book to license: ${books[0]}.`;
    } 
    else if (!isDirect && books.length === 1) {
      scenario = 2;
      context = `Agency Outreach. Recipient: ${licensor}. Author they represent: ${authors[0]}. Book to license: ${books[0]}.`;
    }
    else if (!isDirect && books.length > 1) {
      scenario = 3;
      context = `Agency Outreach (Multiple Authors/Books). Recipient: ${licensor}. Books to license: `;
      for (let i = 0; i < books.length; i++) {
        context += `'${books[i]}' by ${authors[i]}, `;
      }
    }
    else if (isDirect && books.length > 1) {
      scenario = 4;
      context = `Direct Author Outreach (Multiple Books). Recipient: ${authors[0]}. Books to license: `;
      for (let i = 0; i < books.length; i++) {
        context += `'${books[i]}', `;
      }
    }
    
    // Clean up trailing commas
    context = context.replace(/, $/, ".");
    
    // Step 4: Write Context to the FIRST row of that group.
    // For the other books in that group, mark them as "Bundled" so we don't send duplicate emails.
    let primaryRow = group[0].rowIndex;
    sheet.getRange(primaryRow + 1, contextCol + 1).setValue(context);
    
    for (let i = 1; i < group.length; i++) {
      let secondaryRow = group[i].rowIndex;
      sheet.getRange(secondaryRow + 1, contextCol + 1).setValue("Bundled with row " + (primaryRow + 1));
    }
    
    Logger.log(`Processed ${licensor} - Scenario ${scenario}`);
  }
  
  Logger.log("Finished generating all AI Context Bundles!");
}

/**
 * ============================================================================
 * POST-SALES CRM EMAIL SCHEDULER (100% COMPLETE)
 * Trigger: Set this function to run Time-driven -> Day timer -> 7:00 PM to 8:00 PM
 * ============================================================================
 */

function processPostSalesTriggers() {
  // Connects directly to the Internal Copy of US_Licensing_Lifecycle_Tracker
  const sheet = SpreadsheetApp.openByUrl("https://docs.google.com/spreadsheets/d/1qQegfsBODu8GAfe1lMCxNtYV75MWCEtQOopiwH4JcWY/edit?gid=1165007468#gid=1165007468").getSheetByName("Lifecycle Tracker - Master");
  if (!sheet) return;
  
  const data = sheet.getDataRange().getValues();
  
  // Row 3 (Index 2) contains your headers
  const headerRowIndex = 2; 
  const headers = data[headerRowIndex];
  
  // Map all base data columns
  const emailCol = headers.indexOf("Email ID");
  const authorCol = headers.indexOf("Author Name");
  const titleCol = headers.indexOf("Title / IP");
  const showLinkCol = headers.indexOf("Show Link"); // AZ
  
  // -------------------------------------------------------------
  // TRIGGER DATE COLUMNS
  // -------------------------------------------------------------
  const contractSignedCol = headers.indexOf("Contract Signing date"); // N
  // Column AP is exactly 2 columns to the right of the Vendor Lifecycle Status column
  const vendorLifecycleExitedCol = headers.indexOf("Vendor lifecycle Status") + 2; 
  // Column AT is exactly 6 columns to the right of the Vendor Lifecycle Status column
  const mgPayoutExitedCol = headers.indexOf("Vendor lifecycle Status") + 6; 
  const mgConfirmedCol = headers.indexOf("MG Payout Confirmation + Feedback Mail"); // BI
  const revStatementDueCol = headers.indexOf("Rev Statement Due Date"); // BR
  
  // -------------------------------------------------------------
  // STATUS COLUMNS TO UPDATE (Where "Scheduled" is written)
  // -------------------------------------------------------------
  const welcomeCol = headers.indexOf("Welcome Email"); // BF
  const vendorCol = headers.indexOf("Vendor Onboarding Email \n(Same day as Welcome Email)"); // BG
  const mgPayoutInitiatedCol = headers.indexOf("MG Payout Initiated\n(Netsuite Stage: Bill approved)"); // BH
  const mgPayoutConfirmationCol = headers.indexOf("MG Payout Confirmation + Feedback Mail"); // BI
  const checkIn1Col = headers.indexOf("Author Check-In 1:\n(MG Payout Confirmation + 15 days)"); // BM
  const checkIn2Col = headers.indexOf("Author Check-In 2:\n(MG Payout Confirmation + 30 days)\n[Optional]"); // BN
  const launchCol = headers.indexOf("Show Launch Announcement Status"); // BO
  const revStatementEmailCol = headers.indexOf("Revenue Statement + Insights Email Status"); // BS
  
  // -------------------------------------------------------------
  // HTML TEMPLATES - UPDATE THESE WITH THE GOOGLE DOC CODES
  // -------------------------------------------------------------
  const htmlTemplates = {
    welcome: `<h1>Welcome to PocketFM, {Author}!</h1><p>We are thrilled to license {Title}.</p>`,
    vendor: `<h1>Vendor Setup</h1><p>Please complete your onboarding, {Author}.</p>`,
    mgInitiated: `<h1>MG Payout Initiated</h1><p>Hi {Author}, your payout for {Title} has been approved!</p>`,
    mgConfirmed: `<h1>MG Payout Confirmed</h1><p>Hi {Author}, the MG payout for {Title} has been sent.</p>`,
    checkIn1: `<h1>Checking In</h1><p>Hi {Author}, it's been 15 days since your payout for {Title}.</p>`,
    checkIn2: `<h1>Checking In</h1><p>Hi {Author}, it's been 30 days since your payout for {Title}.</p>`,
    launch: `<h1>Your Show is Live!</h1><p>Listen to {Title} here: {ShowLink}</p>`,
    revStatement: `<h1>Revenue Statement</h1><p>Hi {Author}, here is the revenue statement for {Title}.</p>`
  };
  
  // Helper functions
  const today = new Date();
  today.setHours(0,0,0,0);
  
  const isToday = (dateVal) => {
    if (!dateVal || !(dateVal instanceof Date)) return false;
    let d = new Date(dateVal);
    d.setHours(0,0,0,0);
    return d.getTime() === today.getTime();
  };
  
  const addDays = (dateVal, days) => {
    if (!dateVal || !(dateVal instanceof Date)) return null;
    let d = new Date(dateVal);
    d.setDate(d.getDate() + days);
    return d;
  };

  // Draft Creator (Approval System)
  const createDraft = (email, subject, htmlBody, rowIndex, colIndex) => {
    if (!email || email.trim() === "") return;
    GmailApp.createDraft(email, subject, "", { htmlBody: htmlBody });
    sheet.getRange(rowIndex + 1, colIndex + 1).setValue("Scheduled");
  };

  // Loop through all rows
  for (let i = headerRowIndex + 1; i < data.length; i++) {
    let row = data[i];
    let email = row[emailCol];
    if (!email) continue;
    
    let author = row[authorCol];
    let title = row[titleCol];
    let showLink = row[showLinkCol];
    
    // Replace Variables in Templates
    let welcomeHtml = htmlTemplates.welcome.replace(/{Author}/g, author).replace(/{Title}/g, title);
    let vendorHtml = htmlTemplates.vendor.replace(/{Author}/g, author).replace(/{Title}/g, title);
    let mgInitiatedHtml = htmlTemplates.mgInitiated.replace(/{Author}/g, author).replace(/{Title}/g, title);
    let mgConfirmedHtml = htmlTemplates.mgConfirmed.replace(/{Author}/g, author).replace(/{Title}/g, title);
    let checkIn1Html = htmlTemplates.checkIn1.replace(/{Author}/g, author).replace(/{Title}/g, title);
    let checkIn2Html = htmlTemplates.checkIn2.replace(/{Author}/g, author).replace(/{Title}/g, title);
    let launchHtml = htmlTemplates.launch.replace(/{Author}/g, author).replace(/{Title}/g, title).replace(/{ShowLink}/g, showLink);
    let revHtml = htmlTemplates.revStatement.replace(/{Author}/g, author).replace(/{Title}/g, title);
    
    // -------------------------------------------------------------
    // RULE 1: Contract Signed = Welcome Email & Vendor Email
    // -------------------------------------------------------------
    if (isToday(row[contractSignedCol])) {
      if (row[welcomeCol] !== "Scheduled" && row[welcomeCol] !== "Sent") {
        createDraft(email, `Welcome to PocketFM - ${title}`, welcomeHtml, i, welcomeCol);
      }
      if (row[vendorCol] !== "Scheduled" && row[vendorCol] !== "Sent") {
        createDraft(email, `Vendor Onboarding - ${title}`, vendorHtml, i, vendorCol);
      }
    }

    // -------------------------------------------------------------
    // RULE 2: Column AP (Vendor Lifecycle Exit) -> MG Payout Initiated
    // -------------------------------------------------------------
    if (isToday(row[vendorLifecycleExitedCol])) {
      if (row[mgPayoutInitiatedCol] !== "Scheduled" && row[mgPayoutInitiatedCol] !== "Sent") {
        createDraft(email, `MG Payout Initiated - ${title}`, mgInitiatedHtml, i, mgPayoutInitiatedCol);
      }
    }

    // -------------------------------------------------------------
    // RULE 3: Column AT (MG Payout Exit) -> MG Payout Confirmation
    // -------------------------------------------------------------
    if (isToday(row[mgPayoutExitedCol])) {
      if (row[mgPayoutConfirmationCol] !== "Scheduled" && row[mgPayoutConfirmationCol] !== "Sent") {
        createDraft(email, `MG Payout Confirmation - ${title}`, mgConfirmedHtml, i, mgPayoutConfirmationCol);
      }
    }
    
    // -------------------------------------------------------------
    // RULE 4: Author Check-Ins (MG Payout Confirmation + 15 / 30 Days)
    // -------------------------------------------------------------
    let mgDate = row[mgConfirmedCol];
    // This checks if Column BI actually contains a valid Date before doing the +15 math
    if (mgDate && mgDate instanceof Date) {
      if (isToday(addDays(mgDate, 15)) && row[checkIn1Col] !== "Scheduled" && row[checkIn1Col] !== "Sent") {
        createDraft(email, `Checking in on ${title}`, checkIn1Html, i, checkIn1Col);
      }
      if (isToday(addDays(mgDate, 30)) && row[checkIn2Col] !== "Scheduled" && row[checkIn2Col] !== "Sent") {
        createDraft(email, `Following up on ${title}`, checkIn2Html, i, checkIn2Col);
      }
    }
    
    // -------------------------------------------------------------
    // RULE 5: Show Launch Announcement
    // -------------------------------------------------------------
    if (showLink && showLink.toString().includes("http")) {
      if (row[launchCol] !== "Scheduled" && row[launchCol] !== "Sent") {
        createDraft(email, `Your Show is Live! - ${title}`, launchHtml, i, launchCol);
      }
    }

    // -------------------------------------------------------------
    // RULE 6: Rev Statement Due Date
    // -------------------------------------------------------------
    if (isToday(row[revStatementDueCol])) {
      if (row[revStatementEmailCol] !== "Scheduled" && row[revStatementEmailCol] !== "Sent") {
        createDraft(email, `Revenue Statement for ${title}`, revHtml, i, revStatementEmailCol);
      }
    }
  }
}
