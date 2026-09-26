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
