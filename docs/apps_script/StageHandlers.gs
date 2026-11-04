/**
 * =============================================================
 * POCKET FM LIFECYCLE CRM AUTOMATION - MODULE 4: STAGE HANDLERS
 * File: StageHandlers.gs (or StageHandlers.js)
 * =============================================================
 * Contains isolated, robust stage evaluation logic for:
 * 1. Author Check-Ins (15 & 30 Days from Feedback Mail Date)
 * 2. Show Launch Announcements (Launch Date vs Script Date Anomaly Checks)
 * 3. Master Outreach Queue (Welcome, Vendor, MG Payouts, Rev Statements)
 * 4. Dedicated Stage Unit Tests
 *
 * STRICT BLANK ROW GUARD: Evaluates only filled rows (Rows 4-112),
 * skipping blank formula placeholder rows (Rows 113-996).
 */

function processOutreachQueue(isDelayedRun = false, targetStage = null) {
  // Use active spreadsheet when run from container-bound menu, with fallback to document ID
  let spreadsheet;
  try {
    spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  } catch (e) {}
  if (!spreadsheet) {
    try {
      spreadsheet = SpreadsheetApp.openById("1JFT4_f9Du6UZWi6aM0FjYvyR-mcAsbARq7JyxJwLPZc");
    } catch (e2) {}
  }
  const allSheets = spreadsheet.getSheets();
  let mainSheet = (typeof getMainTrackerSheet === 'function') ? getMainTrackerSheet(spreadsheet) : null;
  let psSheet = (typeof getPostSalesTrackerSheet === 'function') ? getPostSalesTrackerSheet(spreadsheet) : null;
  let queueSheet = (typeof getQueueSheet === 'function') ? getQueueSheet(spreadsheet) : null;
  
  if (!mainSheet || !psSheet || !queueSheet) {
    for (let s of allSheets) {
      let sName = s.getName().toLowerCase().trim().replace("–", "-").replace("—", "-");
      if (!mainSheet && (sName === "lifecycle tracker - master" || sName.includes("lifecycle tracker - master"))) {
        mainSheet = s;
      }
      if (!psSheet && (sName === "post-sales tracker" || sName === "post sales tracker")) {
        psSheet = s;
      }
      if (!queueSheet && sName === "queue") {
        queueSheet = s;
      }
    }
  }
  
  Logger.log('[SHEET DETECTED] Main Sheet: ' + (mainSheet ? mainSheet.getName() : 'None'));
  Logger.log('[SHEET DETECTED] Post-Sales Tracker Sheet: ' + (psSheet ? psSheet.getName() + ' (GID: ' + psSheet.getSheetId() + ')' : 'None'));
  
  
  if (queueSheet) {
    try {
      queueSheet.getRange(1, 12).setValue("CC");
      let headerRange = queueSheet.getRange(1, 1, 1, 12);
      headerRange.setBackground("#1155cc"); 
      headerRange.setFontColor("#ffffff");
      headerRange.setFontWeight("bold");
      headerRange.setHorizontalAlignment("center");
      headerRange.setVerticalAlignment("middle");
      queueSheet.setRowHeight(1, 40); 
      queueSheet.hideColumns(1);
      queueSheet.hideColumns(6);
      queueSheet.setColumnWidth(2, 200);
      queueSheet.setColumnWidth(4, 220);
      queueSheet.setColumnWidth(5, 350);
      queueSheet.getRange("B:E").setWrap(true);
      queueSheet.getRange("G:I").setHorizontalAlignment("center");
    } catch (eQ) {
      Logger.log("[QUEUE SHEET FORMAT] Non-critical queue format notice: " + eQ.message);
    }
  }
  
  if (!mainSheet || !psSheet) {
    Logger.log("Could not find required tracking tabs. Main Sheet found: " + (mainSheet !== null) + ", Post-Sales Tracker found: " + (psSheet !== null));
    let names = [];
    allSheets.forEach(s => names.push(s.getName()));
    Logger.log("Available sheets: " + names.join(", "));
    return;
  }
  
  const mainData = mainSheet.getDataRange().getValues();
  const psData = psSheet.getDataRange().getValues();
  
  // Headers for main sheet (Row 3, index 2)
  const mainHeaders = mainData[2];
  const mainFindCol = (name) => mainHeaders.findIndex(h => h.toString().toLowerCase().includes(name.toLowerCase()));
  
  // --- ARGUS DATA PARSING ---
  const argusSheet = allSheets.find(s => s.getName().toString().toLowerCase().includes("argus"));
  let argusData = {};
  if (argusSheet) {
    const aData = argusSheet.getDataRange().getValues();
    if (aData.length > 0) {
      const aHeaders = aData[0];
      const aFindCol = (name) => aHeaders.findIndex(h => h.toString().toLowerCase().includes(name.toLowerCase()));
      const aShowIdCol = aFindCol("Show ID");
      const aTitleCol = aFindCol("Title");
      const aShowNameCol = aFindCol("Show Name");
      const aDurCol = aFindCol("Duration");
      const aLdauCol = aFindCol("Plays") > -1 ? aFindCol("Plays") : aFindCol("LDAU");
      const aCommentsCol = aFindCol("Comment");
      const aRatingsCol = aFindCol("Rating");
      const aReviewsCol = aFindCol("Review");
      const aHoursCol = aFindCol("Listening Hour");
      
      for (let j = 1; j < aData.length; j++) {
        let sid = aShowIdCol > -1 ? aData[j][aShowIdCol] : "";
        let aTitle = aTitleCol > -1 ? aData[j][aTitleCol] : "";
        let aShowName = aShowNameCol > -1 ? aData[j][aShowNameCol] : "";

        let dur = aDurCol > -1 ? aData[j][aDurCol] : "";
        let ldau = aLdauCol > -1 ? aData[j][aLdauCol] : "";
        let comments = aCommentsCol > -1 ? aData[j][aCommentsCol] : "";
        let ratings = aRatingsCol > -1 ? aData[j][aRatingsCol] : "";
        let reviews = aReviewsCol > -1 ? aData[j][aReviewsCol] : "";
        let hours = aHoursCol > -1 ? aData[j][aHoursCol] : "";

        let formattedDur = (dur !== "" && dur !== null && dur !== undefined) ? dur + " hours" : "N/A";
        let formattedPlays = (ldau !== "" && ldau !== null && ldau !== undefined) 
                            ? (ldau.toString().toLowerCase().includes("play") ? ldau.toString() : ldau.toString().replace(/\s*listeners\s*/i, "").trim() + " plays") 
                            : "N/A";
        let formattedComments = (comments !== "" && comments !== null && comments.toString() !== "0" && comments.toString() !== "0.0") 
                                ? (!isNaN(comments) ? Math.round(Number(comments)).toString() : comments.toString()) 
                                : "No comments";
        let formattedRatings = (ratings !== "" && ratings !== null && ratings.toString() !== "0" && ratings.toString() !== "0.0") 
                               ? ratings.toString() 
                               : "No ratings";
        let formattedReviews = (reviews !== "" && reviews !== null && reviews.toString() !== "0" && reviews.toString() !== "0.0") 
                               ? (!isNaN(reviews) ? Math.round(Number(reviews)).toString() : reviews.toString()) 
                               : "No reviews";
        let formattedHours = (hours !== "" && hours !== null && hours !== undefined) ? hours.toString() : "N/A";

        let metrics = {
          duration: formattedDur,
          ldau: formattedPlays,
          plays: formattedPlays,
          comments: formattedComments,
          ratings: formattedRatings,
          reviews: formattedReviews,
          hours: formattedHours
        };

        if (sid) {
          argusData[sid.toString().trim()] = metrics;
          argusData[sid.toString().toLowerCase().trim()] = metrics;
        }
        if (aTitle) {
          argusData[aTitle.toString().toLowerCase().trim()] = metrics;
        }
        if (aShowName) {
          argusData[aShowName.toString().toLowerCase().trim()] = metrics;
        }
      }
    }
  }
  // --------------------------
  
  const mainShowIdCol = mainFindCol("Show ID (after show creation)") !== -1 
                        ? mainFindCol("Show ID (after show creation)") 
                        : (mainFindCol("Show ID") !== -1 ? mainFindCol("Show ID") : 24); // Col Y (index 24)
  const emailCol = mainFindCol("Receiver Email ID") !== -1 
                   ? mainFindCol("Receiver Email ID") 
                   : (mainFindCol("Email") !== -1 ? mainFindCol("Email") : 29); // Col AD (index 29)
  const authorCol = mainFindCol("Author Name") !== -1 ? mainFindCol("Author Name") : 2; // Col C (index 2)
  const firstNameCol = mainFindCol("Receiver First Name") !== -1 ? mainFindCol("Receiver First Name") : 31; // Col AF (index 31)
  const mainTitleCol = mainFindCol("Title / IP") !== -1 ? mainFindCol("Title / IP") : 5; // Col F (index 5)
  const ccCol = mainFindCol("CC Mail ID") !== -1 ? mainFindCol("CC Mail ID") : 30; // Col AE (index 30)
  const mainShowNameCol = mainFindCol("Show Name") !== -1 ? mainFindCol("Show Name") : 33; // Col AH (index 33)
  
  // Master Sheet Columns Mapping (Col F, Q, S, U, V, X, Y, Z, AA, AD, AG)
  const showLinkCol = (mainHeaders.length > 32 && mainHeaders[32] && mainHeaders[32].toString().toLowerCase().includes("link")) 
                      ? 32 
                      : (mainFindCol("Show Link") !== -1 && mainFindCol("Show Link") >= 29 
                          ? mainFindCol("Show Link") 
                          : 32); // Column AG (index 32, 33rd column in Lifecycle Master)
  const contractSignedCol = mainFindCol("Contract Signing date") !== -1 
                            ? mainFindCol("Contract Signing date") 
                            : (mainFindCol("Contract") !== -1 ? mainFindCol("Contract") : 16); // Column Q (Contract Date)
  // Dynamic Master Sheet Section Detection (Row 1 section banners: 'Vendor lifecycle' vs 'MG payout')
  const mainRow1 = (mainData && mainData.length > 0) ? mainData[0] : [];
  let detectedVendorStatusCol = -1;
  let detectedVendorExitCol = -1;
  let detectedMgStatusCol = -1;
  let detectedMgExitCol = -1;

  for (let c = 0; c < mainHeaders.length; c++) {
    let sec = (mainRow1.length > c && mainRow1[c]) ? mainRow1[c].toString().toLowerCase().trim() : "";
    let hdr = mainHeaders[c] ? mainHeaders[c].toString().toLowerCase().trim() : "";
    if (sec.includes("vendor") || (c >= 17 && c <= 20)) {
      if (hdr.includes("status") && detectedVendorStatusCol === -1) detectedVendorStatusCol = c;
      if (hdr.includes("exit") && detectedVendorExitCol === -1) detectedVendorExitCol = c;
    }
    if (sec.includes("mg payout") || sec.includes("mg") || (c >= 21 && c <= 24)) {
      if (hdr.includes("status") && detectedMgStatusCol === -1) detectedMgStatusCol = c;
      if (hdr.includes("exit") && detectedMgExitCol === -1) detectedMgExitCol = c;
    }
  }

  const vendorStatusCol = detectedVendorStatusCol > -1 ? detectedVendorStatusCol : 18; // Column S (Vendor Status == Done)
  const vendorLifecycleExitedCol = detectedVendorExitCol > -1 ? detectedVendorExitCol : 20; // Column U (Vendor Exit Date)
  const mgStatusCol = detectedMgStatusCol > -1 ? detectedMgStatusCol : 21; // Column V (MG Status == Done)
  const mgPayoutExitedCol = detectedMgExitCol > -1 ? detectedMgExitCol : 23; // Column X (MG Exit Date)
  const mainLaunchDateCol = mainFindCol("Launch Date") !== -1 ? mainFindCol("Launch Date") : 25; // Column Z (Launch Date)
  const launchStatusCol = (mainHeaders.length > 26 && mainHeaders[26] && mainHeaders[26].toString().toLowerCase().includes("status"))
                          ? 26
                          : (mainFindCol("Launch Status") !== -1 ? mainFindCol("Launch Status") : 26); // Column AA (Status)

  // Build a lookup dictionary for main sheet data based on Title / IP (Col F)
  let mainDict = {};
  for(let i = 3; i < mainData.length; i++) {
     let row = mainData[i];
     if (!isTrackerRowFilled(row, mainTitleCol)) continue; // Skip blank rows
     let t = row[mainTitleCol];
     if (t) {
         let safeTitle = t.toString().toLowerCase().trim();
         let rawContract = (contractSignedCol > -1 && row.length > contractSignedCol && row[contractSignedCol]) 
                            ? row[contractSignedCol] 
                            : "";

         // Email resolution for Master row: Check Col AD (index 29) first, then Col AB (index 27 fallback)
         let masterEmail = "";
         if (emailCol > -1 && row.length > emailCol && row[emailCol] && row[emailCol].toString().trim() !== "") {
           masterEmail = row[emailCol].toString().trim();
         } else if (row.length > 29 && row[29] && row[29].toString().trim() !== "") {
           masterEmail = row[29].toString().trim(); // Col AD (index 29)
         } else if (row.length > 27 && row[27] && row[27].toString().trim() !== "") {
           masterEmail = row[27].toString().trim(); // Col AB (index 27 fallback)
         }

         // Show Link resolution for Master row: Check Col AG (index 32)
         let masterShowLink = "";
         if (row.length > 32 && row[32] && row[32].toString().trim() !== "") {
           masterShowLink = row[32].toString().trim(); // Col AG (index 32)
         } else if (showLinkCol > -1 && row.length > showLinkCol && row[showLinkCol] && row[showLinkCol].toString().trim() !== "") {
           masterShowLink = row[showLinkCol].toString().trim();
         }

         // CC Mail resolution for Master row: Check Col AE (index 30)
         let masterCc = (ccCol > -1 && row.length > ccCol && row[ccCol]) 
                        ? row[ccCol].toString().trim() 
                        : (row.length > 30 && row[30] ? row[30].toString().trim() : "");

         // First Name resolution for Master row: Check Col AF (index 31)
         let masterFirstName = (firstNameCol > -1 && row.length > firstNameCol && row[firstNameCol]) 
                               ? row[firstNameCol].toString().trim() 
                               : (row.length > 31 && row[31] ? row[31].toString().trim() : "");

         // Show Name resolution for Master row: Check Col AH (index 33)
         let masterShowName = (mainShowNameCol > -1 && row.length > mainShowNameCol && row[mainShowNameCol]) 
                              ? row[mainShowNameCol].toString().trim() 
                              : (row.length > 33 && row[33] ? row[33].toString().trim() : "");

         mainDict[safeTitle] = {
             masterRow: i + 1,
             email: masterEmail,
             author: (authorCol > -1 && row.length > authorCol) ? row[authorCol] : "",
             firstName: masterFirstName,
             showLink: masterShowLink,
             ccMail: masterCc,
             showId: (mainShowIdCol > -1 && row.length > mainShowIdCol) ? row[mainShowIdCol] : "",
             contractSigned: rawContract, // Col Q: Contract == TODAY
             vendorStatus: (vendorStatusCol > -1 && row.length > vendorStatusCol && row[vendorStatusCol]) ? row[vendorStatusCol].toString().trim() : "",
             vendorLifecycleExited: (vendorLifecycleExitedCol > -1 && row.length > vendorLifecycleExitedCol) ? row[vendorLifecycleExitedCol] : "",
             mgStatus: (mgStatusCol > -1 && row.length > mgStatusCol && row[mgStatusCol]) ? row[mgStatusCol].toString().trim() : "",
             mgPayoutExited: (mgPayoutExitedCol > -1 && row.length > mgPayoutExitedCol) ? row[mgPayoutExitedCol] : "",
             launchStatus: (launchStatusCol > -1 && row.length > launchStatusCol && row[launchStatusCol]) ? row[launchStatusCol].toString().trim() : "",
             launchDate: (mainLaunchDateCol > -1 && row.length > mainLaunchDateCol) ? row[mainLaunchDateCol] : "",
             stage: (row.length > 15 && row[15]) ? row[15].toString().trim() : "",
             showName: masterShowName
         };
     }
  }

  // Headers for Post-Sales Tracker (Row 3, index 2)
  const psHeaders = psData[2];
  const psFindCol = (name) => psHeaders.findIndex(h => h.toString().toLowerCase().includes(name.toLowerCase()));
  
  const psTitleCol = psFindCol("Title / IP") !== -1 ? psFindCol("Title / IP") : (psFindCol("Title") !== -1 ? psFindCol("Title") : 2);
  const psContractDateCol = psFindCol("Contract Signing date") !== -1 
                            ? psFindCol("Contract Signing date") 
                            : (psFindCol("Contract") !== -1 ? psFindCol("Contract") : 3); // Column D
  const psShowNameCol = psFindCol("Show Name") !== -1 ? psFindCol("Show Name") : 12;
  const psShowLinkCol = psFindCol("Show Link") !== -1 ? psFindCol("Show Link") : 11;
  const welcomeCol = psFindCol("Welcome Email") !== -1 ? psFindCol("Welcome Email") : 17; 
  const vendorCol = psFindCol("Vendor Onboarding Email") !== -1 ? psFindCol("Vendor Onboarding Email") : 18; 
  const mgPayoutInitiatedCol = psFindCol("MG Payout Initiated") !== -1 ? psFindCol("MG Payout Initiated") : 19; 
  const mgPayoutConfirmationCol = psFindCol("MG Payout Confirmation") !== -1 ? psFindCol("MG Payout Confirmation") : 20; 
  const feedbackMailDateCol = psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("feedback") && s.includes("date");
  }) !== -1 ? psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("feedback") && s.includes("date");
  }) : 21; // Column V

  const checkIn1Col = psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("15 days") && !s.includes("newsletter") && !s.includes("date");
  }) !== -1 ? psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("15 days") && !s.includes("newsletter") && !s.includes("date");
  }) : 22; // Column W

  const checkIn1DateCol = psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("15 days") && !s.includes("newsletter") && s.includes("date");
  }) !== -1 ? psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("15 days") && !s.includes("newsletter") && s.includes("date");
  }) : 23; // Column X

  const checkIn2Col = psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("30 days") && !s.includes("date");
  }) !== -1 ? psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("30 days") && !s.includes("date");
  }) : 24; // Column Y

  const checkIn2DateCol = psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("30 days") && s.includes("date");
  }) !== -1 ? psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("30 days") && s.includes("date");
  }) : 25; // Column Z 
  const scriptDateCol = psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("script") && s.includes("date");
  }) !== -1 ? psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("script") && s.includes("date");
  }) : 14; // Column O

  const psLaunchDateCol = psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s === "launch date" || (s.includes("launch") && s.includes("date") && !s.includes("sent") && !s.includes("announcement"));
  }) !== -1 ? psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s === "launch date" || (s.includes("launch") && s.includes("date") && !s.includes("sent") && !s.includes("announcement"));
  }) : 9; // Column J

  const launchCol = psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return (s.includes("launch") && s.includes("announcement") && s.includes("status")) ||
           (s === "show launch announcement status");
  }) !== -1 ? psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return (s.includes("launch") && s.includes("announcement") && s.includes("status")) ||
           (s === "show launch announcement status");
  }) : (psFindCol("Show Launch Announcement") !== -1 ? psFindCol("Show Launch Announcement") : 26); // Column AA (idx 26)

  let launchSentCol = psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return (s.includes("launch") && s.includes("announcement") && (s.includes("sent") || s.includes("email sent")) && !s.includes("date"));
  });
  if (launchSentCol === -1) {
    if (psHeaders.length > 27 && (psHeaders[27].toString().trim().toLowerCase() === "er" || psHeaders[27].toString().toLowerCase().includes("sent"))) {
      launchSentCol = 27; // Column AB
    } else if (launchCol !== -1 && launchCol + 1 < psHeaders.length) {
      launchSentCol = launchCol + 1;
    } else {
      launchSentCol = 27;
    }
  }

  let launchSentDateCol = psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return (s.includes("launch") && s.includes("announcement") && s.includes("date")) ||
           (s.includes("launch") && s.includes("sent") && s.includes("date"));
  });
  if (launchSentDateCol === -1 && launchSentCol !== -1) {
    if (psHeaders[launchSentCol + 1] && psHeaders[launchSentCol + 1].toString().toLowerCase().includes("date")) {
      launchSentDateCol = launchSentCol + 1;
    } else if (psHeaders.length > 28) {
      launchSentDateCol = 28; // Column AC
    }
  }
  let newsletterCol = psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("newsletter") && !s.includes("date");
  });
  if (newsletterCol === -1) {
    newsletterCol = 29; // Column AD
  }
  const newsletterSentDateCol = psHeaders.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("newsletter") && s.includes("date");
  });
  // Direct helper columns in Post-Sales Tracker (Fallback to Master Tracker if blank)
  const psEmailCol = psFindCol("Receiver Email ID");
  const psCcCol = psFindCol("CC Mail ID");
  const psFirstNameCol = psFindCol("Receiver First Name");

  // =============================================================
  // REVENUE STATEMENT QUARTERLY COLUMN MAPPINGS (FROM COLUMN AE ONWARDS)
  // =============================================================
  // 1. AMJ Quarter (April–June) - Columns AE to AH
  const amjDueCol = psHeaders.findIndex(h => h.toString().toLowerCase().includes("amj") && (h.toString().toLowerCase().includes("due") || h.toString().toLowerCase().includes("date")));
  const amjStatusCol = psHeaders.findIndex(h => h.toString().toLowerCase().includes("amj") && h.toString().toLowerCase().includes("status"));
  const amjLinkCol = psHeaders.findIndex(h => h.toString().toLowerCase().includes("amj") && h.toString().toLowerCase().includes("drive"));
  const amjSentCol = psHeaders.findIndex((h, idx) => idx >= 30 && idx <= 34 && h.toString().toLowerCase().includes("sent"));

  // 2. APPROVED REVENUE PROGRESS COLUMNS (Columns AI to AM in Post-Sales Tracker)
  const jasDueCol = psHeaders.findIndex(h => h.toString().toLowerCase().includes("jas") && (h.toString().toLowerCase().includes("due") || h.toString().toLowerCase().includes("date"))) !== -1
                    ? psHeaders.findIndex(h => h.toString().toLowerCase().includes("jas") && (h.toString().toLowerCase().includes("due") || h.toString().toLowerCase().includes("date")))
                    : 34; // Col AI (index 34)
  const jasStatusCol = psHeaders.findIndex(h => h.toString().toLowerCase().includes("jas") && h.toString().toLowerCase().includes("status")) !== -1
                       ? psHeaders.findIndex(h => h.toString().toLowerCase().includes("jas") && h.toString().toLowerCase().includes("status"))
                       : 35; // Col AJ (index 35)
  const jasLinkCol = psHeaders.findIndex(h => h.toString().toLowerCase().includes("jas") && h.toString().toLowerCase().includes("drive")) !== -1
                     ? psHeaders.findIndex(h => h.toString().toLowerCase().includes("jas") && h.toString().toLowerCase().includes("drive"))
                     : 37; // Col AL (index 37, JAS Drive Link)
  const jasSentCol = psHeaders.findIndex((h, idx) => idx >= 34 && idx <= 39 && h.toString().toLowerCase().includes("sent")) !== -1
                     ? psHeaders.findIndex((h, idx) => idx >= 34 && idx <= 39 && h.toString().toLowerCase().includes("sent"))
                     : 38; // Col AM (index 38, Primary Progress Sent Dropdown)

  // 3. OND Quarter (October–December) - Columns AN to AQ
  const ondDueCol = psHeaders.findIndex(h => h.toString().toLowerCase().includes("ond") && (h.toString().toLowerCase().includes("due") || h.toString().toLowerCase().includes("date")));
  const ondStatusCol = psHeaders.findIndex((h, idx) => idx >= 39 && idx <= 42 && h.toString().toLowerCase().includes("status"));
  const ondLinkCol = psHeaders.findIndex((h, idx) => idx >= 40 && idx <= 43 && h.toString().toLowerCase().includes("drive"));
  const ondSentCol = psHeaders.findIndex((h, idx) => idx >= 41 && idx <= 44 && h.toString().toLowerCase().includes("sent"));

  // 4. Approved Progress Target (Col AM in Columns AI-AM)
  const revLinkCol = jasLinkCol; // Col AL (index 37)
  const revStatementSentCol = jasSentCol; // Col AM (index 38)
  const revStatementEmailCol = jasStatusCol; // Col AJ (index 35) 

  // =============================================================
  // RECOMMENDED NOTIFICATIONS & ELIGIBILITY LOGGER
  // =============================================================
  let notificationLog = [];
  function logNotification(category, title, detail, rowNum = null) {
    let cleanDetail = detail || "";
    // If detail accidentally contains [ROW \d+], extract rowNum if not already set, and strip it from detail
    let rowMatch = cleanDetail.match(/\[ROW\s+(\d+)\]/i);
    if (rowMatch) {
      if (!rowNum) rowNum = parseInt(rowMatch[1], 10);
      cleanDetail = cleanDetail.replace(/\[ROW\s+\d+\]\s*/gi, "");
    }
    // Clean up category prefix if duplicate
    if (cleanDetail.startsWith(`${category}: `)) {
      cleanDetail = cleanDetail.substring(`${category}: `.length);
    } else if (cleanDetail.startsWith(`${category} `)) {
      cleanDetail = cleanDetail.substring(category.length).trim();
    }
    let rowPrefix = rowNum ? `[ROW ${rowNum}] ` : "";
    let msg = `${rowPrefix}[RECOMMENDED NOTIFICATION] ${category}: ${cleanDetail} (Title: "${title}")`;
    notificationLog.push({ category: category, title: title, message: cleanDetail, fullLog: msg, rowNum: rowNum });
    Logger.log(msg);
  }

  // -------------------------------------------------------------
  // EMAIL SANITIZATION & VALIDATION HELPERS
  // -------------------------------------------------------------
  function cleanEmail(rawEmail) {
    if (!rawEmail) return "";
    let str = rawEmail.toString().trim();
    let bracketMatch = str.match(/<([^>]+)>/);
    if (bracketMatch) {
      str = bracketMatch[1].trim();
    } else {
      str = str.replace(/^[<"'\s]+|[>"'\s;]+$/g, "");
    }
    return str;
  }

  function isValidEmail(emailStr) {
    if (!emailStr) return false;
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailStr);
  }

  function cleanCcList(rawCc) {
    if (!rawCc) return "";
    let parts = rawCc.toString().split(/[,;]/);
    let cleaned = parts.map(p => cleanEmail(p)).filter(p => isValidEmail(p));
    return cleaned.join(", ");
  }

  // Strict URL validator: Rejects plain text notes (e.g. "Show Untested / Never Made Live") and requires a real URL
  function isValidWebUrl(rawUrl) {
    if (!rawUrl) return false;
    let str = rawUrl.toString().trim();
    if (str === "" || str === "#" || str.includes("#REF") || str.includes("#N/A") || str.includes("#VALUE")) return false;
    if (/\s/.test(str)) return false;
    let lower = str.toLowerCase();
    if (lower === "none" || lower === "na" || lower === "n/a" || lower === "tbd" || lower === "pending" || lower === "-" || lower === "--") return false;
    if (lower.includes("untested") || lower.includes("never") || lower.includes("live") || lower.includes("show") || lower.includes("dropped") || lower.includes("bad") || lower.includes("review")) return false;
    if (/^https?:\/\/[a-zA-Z0-9\-._~%]+(\.[a-zA-Z0-9\-._~%]+)+/i.test(str)) return true;
    if (/^(www\.|drive\.google\.com\/|[a-zA-Z0-9\-]+\.(?:com|app|net|org|io|dev|in|co)\/)/i.test(str)) return true;
    return false;
  }

  // Standardized YYYY-MM-DD date key helper for same date check
  function getStandardDateKey(dateVal) {
    if (!dateVal) return "";
    let target = parseDateSafe(dateVal);
    if (!target) return dateVal.toString().trim().toLowerCase();
    let yr = target.getFullYear();
    let mo = String(target.getMonth() + 1).padStart(2, "0");
    let da = String(target.getDate()).padStart(2, "0");
    return `${yr}-${mo}-${da}`;
  }

  // -------------------------------------------------------------
  // DRAFTING LOGIC WITH VARIABLE MAPPING & QUEUE INJECTION
  // -------------------------------------------------------------
  function createDraft(rawEmail, subject, firstName, type, title, link, rIdx, cIdx, customSendTime, rawCcMail, revLink, argus, showName = "") {
    const email = cleanEmail(rawEmail);
    const ccMail = cleanCcList(rawCcMail);
    const rowIndices = Array.isArray(rIdx) ? rIdx : (rIdx !== null && rIdx !== undefined ? [rIdx] : []);
    const rowNumbersDisplay = rowIndices.length > 0 ? rowIndices.map(idx => idx + 1).join(", ") : "";
    const rowPrefix = rowNumbersDisplay ? (rowIndices.length > 1 ? `[ROWS ${rowNumbersDisplay}] ` : `[ROW ${rowNumbersDisplay}] `) : "";
    const draftRowNum = rowIndices.length > 0 ? rowIndices[0] + 1 : null;

    // 1. Notification Check: Recipient Email ID
    if (!email || email === "" || !isValidEmail(email)) {
      logNotification("Recipient Email ID is missing", title, `Recipient Email ID is invalid or missing in Master Sheet (Col AB) for "${title}" ("${rawEmail || ''}"). Cannot create draft.`, draftRowNum);
      return;
    }

    // 2. Notification Check: Email Template Selected
    const validTemplates = [
      'welcome', 'vendor', 'mgInitiated', 'mgConfirmed', 
      'checkIn1', 'checkIn2', 'launch', 'launch_no_ai', 
      'authorEdit', 'newsletter',
      'revStatement_workedWell_content', 'revStatement_workedWell_payment', 
      'revStatement_didntWorkWell', 'contentBad'
    ];
    if (!type || !validTemplates.includes(type)) {
      logNotification("Email template not selected", title, `Email template not selected or unrecognized for stage type: "${type}". Draft creation skipped.`, draftRowNum);
      return;
    }

    // 3. Variable Mapping (Singular vs Plural logic from 'Variable Mapping' tab)
    const isMulti = title.includes(",");
    const grammar = {
      work: isMulti ? "works" : "work",
      is: isMulti ? "are" : "is",
      has: isMulti ? "have" : "has",
      title: isMulti ? "titles" : "title",
      this: isMulti ? "these" : "this",
      it: isMulti ? "them" : "it",
      its: isMulti ? "their" : "its"
    };

    // 4. Map 'type' to the exact Automation Rule Template Name
    let templateName = type;
    if (type === "welcome") templateName = "Welcome Email";
    if (type === "vendor") templateName = "Vendor Onboarding Email";
    if (type === "mgInitiated") templateName = "MG Payment Initiated";
    if (type === "mgConfirmed") templateName = "MG Payment Processed";
    if (type === "checkIn1") templateName = "Personal Check In 1";
    if (type === "checkIn2") templateName = "Personal Check In 2";
    if (type === "launch") templateName = "AI Allowed - Show Launch Announcement";
    if (type === "authorEdit" || type === "newsletter") templateName = "The Author Edit";
    if (type === "revStatement_workedWell_content") templateName = "Content Update - worked well";
    if (type === "revStatement_workedWell_payment") templateName = "Worked Well - Payment-Related Update";
    if (type === "revStatement_didntWorkWell" || type === "contentBad") templateName = "Didn't work well - Content + Payment Related Update";

    // 5. Generate Data for Queue
    const queueId = Utilities.getUuid();
    
    if (typeof getBody !== 'function' || typeof wrapHtml !== 'function') {
      throw new Error("Templates.gs is missing from this Google Apps Script project. Please create a script file named 'Templates' in Extensions > Apps Script and paste the contents of Templates.gs into it.");
    }

    const templateType = (type === "contentBad") ? "revStatement_didntWorkWell" : type;
    const body = getBody(templateType, firstName, title, link, grammar, revLink, argus, showName);
    if (!body || body.trim() === "") {
      logNotification("Email template not selected", title, `Email template body is empty or not defined for stage type: "${type}".`, draftRowNum);
      return;
    }
    const wrappedBody = wrapHtml(body, queueId);
    
    const sendDate = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy-MM-dd");
    const exactTime = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "hh:mm a"); 
    const sendTime = customSendTime ? customSendTime : exactTime; 
    const ccValue = ccMail ? ccMail : "";
    
    // 6. Append to Queue Tab (Queue ID, Recipient, Sender, Template, Subject, HTML Body, Send Date, Send Time, Status, Row IDs, Approved, CC)
    if (queueSheet) {
      try {
        let senderEmail = "";
        try { senderEmail = Session.getActiveUser().getEmail(); } catch (eUser) {}
        queueSheet.appendRow([
          queueId,
          email, 
          senderEmail, 
          templateName, 
          subject,
          wrappedBody,
          sendDate,
          sendTime,
          "Draft Ready", 
          rowNumbersDisplay, 
          "Post-Sales Tracker",
          ccValue,
          cIdx !== undefined && cIdx !== null ? cIdx + 1 : "",
          type
        ]);
      } catch (errQueue) {
        Logger.log(`${rowPrefix}[WARNING] Could not append row to Queue sheet: ${errQueue.message}`);
      }
    }

    // (Optional) We keep the traditional draft creation just in case you want to manually verify in Gmail
    let draftOptions = { htmlBody: wrappedBody };
    if (ccMail && ccMail !== "") {
      draftOptions.cc = ccMail;
    }
    let draftSuccess = false;
    try {
      GmailApp.createDraft(email, subject, "", draftOptions);
      draftSuccess = true;
    } catch (err) {
      Logger.log(`${rowPrefix}[WARNING] Gmail draft creation failed for "${title}" (${email}): ${err.message}`);
    }

    // Only update sheet statuses and dates if the mail actually got generated and drafted in the mailbox!
    if (!draftSuccess) {
      Logger.log(`${rowPrefix}[SKIPPED] Draft was NOT created in mailbox for "${title}". Dates and statuses will not be updated.`);
      return;
    }
    
    // Update main tracker sheet status indicating draft is prepared in the mailbox
    let statusValue = "Draft Ready";
    if (type === "mgConfirmed" || cIdx === mgPayoutConfirmationCol) {
      statusValue = "Draft ready";
    } else if (type === "checkIn1" || type === "checkIn2" || cIdx === checkIn1Col || cIdx === checkIn2Col) {
      statusValue = "draft ready";
    }

    rowIndices.forEach(idx => {
      if (idx >= 0 && cIdx >= 0) {
        psSheet.getRange(idx + 1, cIdx + 1).setValue(statusValue);
      }
      
      if (type === "launch" || type === "launch_no_ai") {
        if (typeof launchSentCol !== "undefined" && launchSentCol !== -1) {
          psSheet.getRange(idx + 1, launchSentCol + 1).setValue("Draft Ready");
          Logger.log(`[ROW ${idx + 1}] [STATUS UPDATE] Updated Launch Announcement Sent dropdown for "${title}" in Col ${launchSentCol + 1} (Col AB) to "Draft Ready"`);
        }
        if (typeof launchCol !== "undefined" && launchCol !== -1) {
          let curAAFormula = psSheet.getRange(idx + 1, launchCol + 1).getFormula();
          if (!curAAFormula) {
            psSheet.getRange(idx + 1, launchCol + 1).setValue("Draft Ready");
          }
          Logger.log(`[ROW ${idx + 1}] [STATUS UPDATE] Updated Launch Announcement Status for "${title}" in Col ${launchCol + 1} (Col AA) to "Draft Ready"`);
        }
      }
      if ((type === "authorEdit" || type === "newsletter") && typeof newsletterCol !== "undefined" && newsletterCol !== -1) {
        psSheet.getRange(idx + 1, newsletterCol + 1).setValue("Draft Ready");
        SpreadsheetApp.flush();
        Logger.log(`[ROW ${idx + 1}] [STATUS UPDATE] Updated Newsletter Edit dropdown for "${title}" in Col ${newsletterCol + 1} (Col AD) of "${psSheet.getName()}" to "Draft Ready"`);
      }
    });
    SpreadsheetApp.flush();

    // NOTE: Removed premature date stamping!
    // Feedback Mail Date (Col V), Check-In Dates (Col X/Z), Launch Sent Date (Col AC), and Newsletter Sent Date
    // are left BLANK upon draft creation. They are stamped strictly by syncSentEmails() when the email is actually dispatched from Gmail!
    Logger.log(`${rowPrefix}[DRAFT CREATED] Successfully created ${type} draft for "${title}" (Recipient: ${email})`);
  }

  // Candidate queues for multi-title same-date consolidation (Stages 1-6)
  let stage1Candidates = [];
  let stage2Candidates = [];
  let stage3Candidates = [];
  let stage4Candidates = [];
  let stage5Candidates = [];
  let stage6Candidates = [];

  // Iterate over all rows in Post-Sales Tracker (starting from index 3)
  let triggerSet = false;
  
  for (let i = 3; i < psData.length; i++) {
    let psRow = psData[i];
    if (!isTrackerRowFilled(psRow, psTitleCol)) continue;
    const rowNum = i + 1; // Skip blank rows
    let title = psRow[psTitleCol];
    if (!title) continue;
    
    let safeTitle = title.toString().toLowerCase().trim();
    let mainInfo = mainDict[safeTitle] || {};
    
    // 1. Recipient Email ID resolution (Post-Sales Tracker Col F [index 5], fallback to Master Sheet Col AD [index 29] / Col AB)
    let psEmail = (psEmailCol > -1 && psRow.length > psEmailCol && psRow[psEmailCol]) ? psRow[psEmailCol].toString().trim() : "";
    let rawEmail = (psEmail !== "" && !psEmail.includes("#REF") && isValidEmail(psEmail)) 
                   ? psEmail 
                   : (mainInfo.email || "");
    let email = cleanEmail(rawEmail);
    if (!email || email === "" || !isValidEmail(email)) {
      logNotification("Recipient Email ID is missing", title, `Recipient Email ID is invalid or missing in Post-Sales Tracker (Col F) and Master sheet (Col AD/AB) for "${title}" ("${rawEmail || ''}"). Cannot proceed with outreach drafts.`, rowNum);
      continue;
    }

    let psShowName = (psShowNameCol > -1 && psRow.length > psShowNameCol && psRow[psShowNameCol]) ? psRow[psShowNameCol].toString().trim() : "";
    let showName = (psShowName !== "" && !psShowName.includes("#REF")) 
                   ? psShowName 
                   : (mainInfo.showName || title.toString().trim());

    let psShowIdCol = psFindCol("Show ID");
    let psShowId = (psShowIdCol > -1 && psRow.length > psShowIdCol && psRow[psShowIdCol]) ? psRow[psShowIdCol].toString().trim() : "";
    let showId = (psShowId !== "" && !psShowId.includes("#REF")) 
                 ? psShowId 
                 : (mainInfo.showId ? mainInfo.showId.toString().trim() : "");
    let safeSid = showId ? showId.toLowerCase().trim() : "";

    let argus = (safeSid && argusData[safeSid]) 
                || (argusData[safeTitle]) 
                || (showName && argusData[showName.toLowerCase().trim()]) 
                || {duration: "N/A", ldau: "N/A", plays: "N/A", comments: "No comments", ratings: "No ratings", reviews: "No reviews", hours: "N/A"};
    let psAuthorCol = psFindCol("Author Name");
    let psAuthor = (psAuthorCol > -1 && psRow.length > psAuthorCol && psRow[psAuthorCol]) ? psRow[psAuthorCol].toString().trim() : "";
    let author = (psAuthor !== "" && !psAuthor.includes("#REF")) ? psAuthor : (mainInfo.author ? mainInfo.author.toString().trim() : "");

    // Show Link resolution: Master Col AG (index 32), then Post-Sales Col L (index 11)
    let psLink = (psShowLinkCol > -1 && psRow.length > psShowLinkCol && psRow[psShowLinkCol]) ? psRow[psShowLinkCol].toString().trim() : "";
    let link = (mainInfo.showLink && mainInfo.showLink !== "" && !mainInfo.showLink.includes("#REF")) 
               ? mainInfo.showLink 
               : ((psLink !== "" && !psLink.includes("#REF")) ? psLink : "");

    // CC Mail resolution: Post-Sales Col G (index 6), fallback to Master Col AE (index 30)
    let psCc = (psCcCol > -1 && psRow.length > psCcCol && psRow[psCcCol]) ? psRow[psCcCol].toString().trim() : "";
    let ccMail = cleanCcList((psCc !== "" && !psCc.includes("#REF")) ? psCc : (mainInfo.ccMail || ""));
    
    // Safely pull from the approved Revenue Statement Drive Link column on the PS Tracker (Col AL in Columns AI-AM)
    let revLinkRaw = (jasLinkCol > -1 && psRow.length > jasLinkCol && psRow[jasLinkCol]) 
                     ? psRow[jasLinkCol] 
                     : ((psRow.length > 37 && psRow[37]) 
                         ? psRow[37] 
                         : ((revLinkCol > -1 && psRow.length > revLinkCol) ? psRow[revLinkCol] : ""));
    
    // Strict link sanitization: ONLY treat as revLink if it is a genuine URL, NOT descriptive text (e.g. "Show Untested / Never Made Live")!
    let revLink = "";
    if (isValidWebUrl(revLinkRaw)) {
      revLink = revLinkRaw.toString().trim();
      if (!revLink.startsWith("http://") && !revLink.startsWith("https://")) {
        revLink = "https://" + revLink;
      }
    }

    // Launch Status resolution: Master Col AA (index 26) & Post-Sales Col K (index 10)
    let masterLaunchStatus = (mainInfo.launchStatus ? mainInfo.launchStatus.toString().trim().toLowerCase() : "");
    let psLaunchStatusCol = psFindCol("Launch Status");
    let psLaunchStatus = (psLaunchStatusCol !== -1 && psRow.length > psLaunchStatusCol && psRow[psLaunchStatusCol]) 
                         ? psRow[psLaunchStatusCol].toString().trim().toLowerCase() 
                         : "";
    let psLaunchAnnouncementStatus = (typeof launchCol !== "undefined" && launchCol !== -1 && psRow.length > launchCol && psRow[launchCol])
                                     ? psRow[launchCol].toString().trim().toLowerCase()
                                     : "";
    let psRevStatus = (typeof jasStatusCol !== "undefined" && jasStatusCol !== -1 && psRow.length > jasStatusCol && psRow[jasStatusCol])
                      ? psRow[jasStatusCol].toString().trim().toLowerCase()
                      : "";
    let masterStage = (mainInfo.stage ? mainInfo.stage.toString().trim().toLowerCase() : "");

    // Robust Dropped / Bad / Discontinued Detection:
    // If "drop", "bad", "discontinue", or "sunset" appears in ANY status location for this show, it is marked!
    let isRowDropped = masterLaunchStatus.includes("drop") || 
                       psLaunchStatus.includes("drop") || 
                       psLaunchAnnouncementStatus.includes("drop") || 
                       psRevStatus.includes("drop") ||
                       masterStage.includes("drop") ||
                       masterLaunchStatus.includes("bad") || 
                       psLaunchStatus.includes("bad") ||
                       masterLaunchStatus.includes("discontinue") ||
                       psLaunchStatus.includes("discontinue") ||
                       psLaunchAnnouncementStatus.includes("discontinue") ||
                       psRevStatus.includes("discontinue") ||
                       masterStage.includes("discontinue") ||
                       masterLaunchStatus.includes("sunset") ||
                       psLaunchStatus.includes("sunset");

    let launchStatus = isRowDropped 
                       ? "dropped" 
                       : (masterLaunchStatus !== "" && !masterLaunchStatus.includes("#REF")
                           ? masterLaunchStatus 
                           : (psLaunchStatus !== "" && !psLaunchStatus.includes("#REF") ? psLaunchStatus : ""));

    // First Name resolution: Post-Sales Col H (index 7), fallback to Master Col AF (index 31) or Author Name
    let psFirstName = (psFirstNameCol > -1 && psRow.length > psFirstNameCol && psRow[psFirstNameCol]) ? psRow[psFirstNameCol].toString().trim() : "";
    let firstName = (psFirstName !== "" && !psFirstName.includes("#REF")) 
                    ? psFirstName 
                    : ((mainInfo.firstName && mainInfo.firstName !== "" && !mainInfo.firstName.includes("#REF")) ? mainInfo.firstName : (author ? author.split(" ")[0] : "Author"));
    
    // 2. Workflow status eligibility check (Launch Status)
    const isDropped = isRowDropped || launchStatus.includes("dropped") || launchStatus.includes("bad") || launchStatus.includes("untested") || launchStatus.includes("discontinue");
    if (isDropped && !launchStatus.includes("dropped") && !isRowDropped) {
      logNotification("Workflow status is not eligible", title, `Workflow status is not eligible for "${title}" (Launch Status is "${launchStatus}"). Standard outreach stages 1-8 are suppressed.`, rowNum);
    }
    
    const isReady = (status) => {
      if (!status) return true;
      let s = status.toString().toLowerCase().trim();
      return s !== "scheduled" && s !== "sent" && s !== "draft ready" && s !== "timer set" && s !== "timer set rev" && !s.includes("launch date issue");
    };
    
    // --- 6-HOUR TIMER EXECUTION BLOCK ---
    if (isDelayedRun) {
      if (psRow[vendorCol] === "Timer Set") {
        createDraft(email, `Vendor Onboarding for ${title}`, firstName, 'vendor', title, link, i, vendorCol, null, ccMail, revLink, argus);
      }
      if (psRow[revStatementEmailCol] === "Timer Set Rev") {
        if (isValidWebUrl(revLink)) {
          createDraft(email, "Pocket FM: Your earnings are waiting for you!", firstName, 'revStatement_workedWell_payment', title, link, i, revStatementEmailCol, null, ccMail, revLink, argus);
        } else {
          Logger.log(`[ROW ${rowNum}] [Rev Statement Timer] [SKIPPED] Missing or non-URL Revenue Statement link in Col AL for "${title}".`);
        }
      }
      continue; 
    }
    // ------------------------------------

    // =============================================================
    // Stage 1: Welcome Email
    // Image Condition: Col AB: Receiver Email | Col F: Title / IP | Col Q: Contract == TODAY | Col AA: Status != Drop/Bad
    // =============================================================
    if (!targetStage || targetStage === 'welcome') {
      let contractDate = mainInfo.contractSigned;
      let isNotDropBad = !launchStatus.includes("drop") && !launchStatus.includes("bad") && !launchStatus.includes("untested") && !launchStatus.includes("discontinue");

      if (!contractDate || contractDate.toString().trim() === "") {
        if (isReady(psRow[welcomeCol])) {
          logNotification("Trigger Date is missing", title, `Contract Signing Date (Col Q in Master) is blank for "${title}".`, rowNum);
        } else {
          Logger.log(`[ROW ${rowNum}] [Welcome Email] Evaluated for "${title}" - Status: "${psRow[welcomeCol] || 'Empty'}" (Contract Date blank, already processed)`);
        }
      } else if (isNotDropBad && isToday(contractDate)) {
        if (isReady(psRow[welcomeCol])) {
          stage1Candidates.push({
            rowIdx: i,
            rowNum: rowNum,
            email: email,
            firstName: firstName,
            title: title.toString().trim(),
            dateKey: getStandardDateKey(contractDate),
            rawDate: contractDate,
            link: link,
            ccMail: ccMail,
            revLink: revLink,
            argus: argus,
            showName: showName,
            colIdx: welcomeCol
          });
        } else {
          Logger.log(`[ROW ${rowNum}] [Welcome Email] Evaluated for "${title}" - Status: "${psRow[welcomeCol]}" (Already processed)`);
        }
      } else if (isNotDropBad && !isToday(contractDate) && contractDate) {
        Logger.log(`[ROW ${rowNum}] [Welcome Email] Evaluated for "${title}" - Status: "${psRow[welcomeCol] || 'Pending'}" | Contract Date (${contractDate}) is not today`);
      } else if (!isNotDropBad) {
        Logger.log(`[ROW ${rowNum}] [Welcome Email] Evaluated for "${title}" - Launch Status: "${launchStatus}" (Suppressed - Drop/Bad)`);
      }
    }

    // =============================================================
    // Stage 2: Vendor Onboarding Email
    // Image Condition: Col AB: Receiver Email | Col F: Title / IP | Col Q: Contract == TODAY | Col AA: Status != Drop/Bad
    // =============================================================
    if (!targetStage || targetStage === 'vendor') {
      let contractDate = mainInfo.contractSigned;
      let isNotDropBad = !launchStatus.includes("drop") && !launchStatus.includes("bad") && !launchStatus.includes("untested") && !launchStatus.includes("discontinue");

      if (!contractDate || contractDate.toString().trim() === "") {
        if (isReady(psRow[vendorCol])) {
          logNotification("Trigger Date is missing", title, `Contract Signing Date (Col Q in Master) is blank for "${title}".`, rowNum);
        } else {
          Logger.log(`[ROW ${rowNum}] [Vendor Onboarding] Evaluated for "${title}" - Status: "${psRow[vendorCol] || 'Empty'}" (Contract Date blank, already processed)`);
        }
      } else if (isNotDropBad && isToday(contractDate)) {
        if (isReady(psRow[vendorCol])) {
          stage2Candidates.push({
            rowIdx: i,
            rowNum: rowNum,
            email: email,
            firstName: firstName,
            title: title.toString().trim(),
            dateKey: getStandardDateKey(contractDate),
            rawDate: contractDate,
            link: link,
            ccMail: ccMail,
            revLink: revLink,
            argus: argus,
            showName: showName,
            colIdx: vendorCol
          });
        } else {
          Logger.log(`[ROW ${rowNum}] [Vendor Onboarding] Evaluated for "${title}" - Status: "${psRow[vendorCol]}" (Already processed)`);
        }
      } else if (isNotDropBad && !isToday(contractDate) && contractDate) {
        Logger.log(`[ROW ${rowNum}] [Vendor Onboarding] Evaluated for "${title}" - Status: "${psRow[vendorCol] || 'Pending'}" | Contract Date (${contractDate}) is not today`);
      } else if (!isNotDropBad) {
        Logger.log(`[ROW ${rowNum}] [Vendor Onboarding] Evaluated for "${title}" - Launch Status: "${launchStatus}" (Suppressed - Drop/Bad)`);
      }
    }

    // =============================================================
    // Stage 3: MG Payment Initiated
    // Image Condition: Col U: Vendor Exit == TODAY | Col S: Vendor Status == Done | Col AA: Status != Drop
    // =============================================================
    if (!targetStage || targetStage === 'mgInitiated') {
      let vendorStatusVal = mainInfo.vendorStatus ? mainInfo.vendorStatus.toLowerCase().trim() : "";
      let isVendorDone = vendorStatusVal === "done";
      let isNotDropped = !launchStatus.includes("drop") && !launchStatus.includes("bad") && !launchStatus.includes("discontinue");

      if (!mainInfo.vendorLifecycleExited || mainInfo.vendorLifecycleExited.toString().trim() === "") {
        if (isReady(psRow[mgPayoutInitiatedCol])) {
          logNotification("Trigger Date is missing", title, `Vendor Lifecycle Exited date (Col U) is blank for "${title}".`, rowNum);
        } else {
          Logger.log(`[ROW ${rowNum}] [MG Payment Initiated] Evaluated for "${title}" - Status: "${psRow[mgPayoutInitiatedCol] || 'Empty'}" (Vendor Exit Date blank)`);
        }
      } else if (isNotDropped && isToday(mainInfo.vendorLifecycleExited) && isVendorDone) {
        if (isReady(psRow[mgPayoutInitiatedCol])) {
          stage3Candidates.push({
            rowIdx: i,
            rowNum: rowNum,
            email: email,
            firstName: firstName,
            title: title.toString().trim(),
            dateKey: getStandardDateKey(mainInfo.vendorLifecycleExited),
            rawDate: mainInfo.vendorLifecycleExited,
            link: link,
            ccMail: ccMail,
            revLink: revLink,
            argus: argus,
            showName: showName,
            colIdx: mgPayoutInitiatedCol
          });
        } else {
          Logger.log(`[ROW ${rowNum}] [MG Payment Initiated] Evaluated for "${title}" - Status: "${psRow[mgPayoutInitiatedCol]}" (Already processed)`);
        }
      } else if (!isToday(mainInfo.vendorLifecycleExited) && mainInfo.vendorLifecycleExited) {
        Logger.log(`[ROW ${rowNum}] [MG Payment Initiated] Evaluated for "${title}" - Status: "${psRow[mgPayoutInitiatedCol] || 'Empty'}" | Vendor Exit Date (${mainInfo.vendorLifecycleExited}) is not today`);
      } else if (!isVendorDone) {
        Logger.log(`[ROW ${rowNum}] [MG Payment Initiated] Evaluated for "${title}" - Vendor Status: "${mainInfo.vendorStatus}" (Must be 'Done')`);
      } else if (!isNotDropped) {
        Logger.log(`[ROW ${rowNum}] [MG Payment Initiated] Evaluated for "${title}" - Launch Status: "${launchStatus}" (Suppressed - Drop)`);
      } else {
        Logger.log(`[ROW ${rowNum}] [MG Payment Initiated] Evaluated for "${title}" - Status: "${psRow[mgPayoutInitiatedCol] || 'Empty'}" | Exit Date: ${mainInfo.vendorLifecycleExited || 'None'}`);
      }
    }

    // =============================================================
    // Stage 4: MG Payment Processed
    // Image Condition: Col X: MG Exit == TODAY | Col V: MG Status == Done | Col AA: Status != Drop
    // =============================================================
    if (!targetStage || targetStage === 'mgConfirmed') {
      let mgStatusVal = mainInfo.mgStatus ? mainInfo.mgStatus.toLowerCase().trim() : "";
      let isMgDone = mgStatusVal === "done";
      let isNotDropped = !launchStatus.includes("drop") && !launchStatus.includes("bad") && !launchStatus.includes("discontinue");

      if (!mainInfo.mgPayoutExited || mainInfo.mgPayoutExited.toString().trim() === "") {
        if (isReady(psRow[mgPayoutConfirmationCol])) {
          logNotification("Trigger Date is missing", title, `MG Payout Exited date (Col X) is blank for "${title}".`, rowNum);
        } else {
          Logger.log(`[ROW ${rowNum}] [MG Payment Processed] Evaluated for "${title}" - Status: "${psRow[mgPayoutConfirmationCol] || 'Empty'}" (MG Exit Date blank)`);
        }
      } else if (isNotDropped && isToday(mainInfo.mgPayoutExited) && isMgDone) {
        if (isReady(psRow[mgPayoutConfirmationCol])) {
          stage4Candidates.push({
            rowIdx: i,
            rowNum: rowNum,
            email: email,
            firstName: firstName,
            title: title.toString().trim(),
            dateKey: getStandardDateKey(mainInfo.mgPayoutExited),
            rawDate: mainInfo.mgPayoutExited,
            link: link,
            ccMail: ccMail,
            revLink: revLink,
            argus: argus,
            showName: showName,
            colIdx: mgPayoutConfirmationCol
          });
        } else {
          Logger.log(`[ROW ${rowNum}] [MG Payment Processed] Evaluated for "${title}" - Status: "${psRow[mgPayoutConfirmationCol]}" (Already processed)`);
        }
      } else if (!isToday(mainInfo.mgPayoutExited) && mainInfo.mgPayoutExited) {
        Logger.log(`[ROW ${rowNum}] [MG Payment Processed] Evaluated for "${title}" - Status: "${psRow[mgPayoutConfirmationCol] || 'Empty'}" | MG Exit Date (${mainInfo.mgPayoutExited}) is not today`);
      } else if (!isMgDone) {
        Logger.log(`[ROW ${rowNum}] [MG Payment Processed] Evaluated for "${title}" - MG Status: "${mainInfo.mgStatus}" (Must be 'Done')`);
      } else if (!isNotDropped) {
        Logger.log(`[ROW ${rowNum}] [MG Payment Processed] Evaluated for "${title}" - Launch Status: "${launchStatus}" (Suppressed - Drop)`);
      } else {
        Logger.log(`[ROW ${rowNum}] [MG Payment Processed] Evaluated for "${title}" - Status: "${psRow[mgPayoutConfirmationCol] || 'Empty'}" | Exit Date: ${mainInfo.mgPayoutExited || 'None'}`);
      }
    }

    // =============================================================
    // Stage 5 & 6: Personal Check-Ins (15 Days & 30 Days)
    //
    // 15-Day Check-in (Col W):
    // 1. If contract signing date (Col D) is before 1st Sept 2026 -> "Does not apply"
    // 2. If Show Launch Announcement email is sent (Col AB / Col AA == 'sent') -> "Does not apply"
    // 3. If Feedback Mail Date (Col V) is missing & show launch announcement email is sent -> "Does not apply"
    // 4. If Feedback Mail Date (Col V) is missing & show launch email not sent -> "Not due yet"
    // 5. If Feedback Mail Date (Col V) + 15 days & show launch email not sent -> "Overdue" (diffDays > 15)
    //    For draft ready -> diffDays === 15 (creates draft, Col W -> "draft ready")
    //
    // 30-Day Check-in (Col Y):
    // 1. If contract signing date (Col D) is before 1st Sept 2026 -> "Does not apply"
    // 2. If Show Launch Announcement email is sent (Col AB / Col AA == 'sent') -> "Does not apply"
    // 3. If Feedback Mail Date (Col V) is missing & show launch announcement email is sent -> "Does not apply"
    // 4. If Check-In 1 Sent Date (Col X) is missing & show launch email not sent -> "Not due yet"
    // 5. If Check-In 1 Sent Date (Col X) + 15 days & show launch email not sent -> "Overdue" (diffDaysX > 15)
    //    For draft ready -> diffDaysX === 15 (creates draft, Col Y -> "draft ready")
    // =============================================================
    let isCheckInDropped = launchStatus.includes("drop") || launchStatus.includes("bad") || launchStatus.includes("discontinue");

    // Deal signing date check (deals signed before 1st September)
    let rawContractDate = (psContractDateCol > -1 && psRow.length > psContractDateCol && psRow[psContractDateCol]) 
                          ? psRow[psContractDateCol] 
                          : (mainInfo ? mainInfo.contractSigned : "");
    let isBeforeSept1 = isDealSignedBeforeSept1(rawContractDate);

    // Show Launch Announcement status check (Col AB or Col AA == 'sent')
    let rawColAB = (launchSentCol > -1 && psRow.length > launchSentCol && psRow[launchSentCol]) ? psRow[launchSentCol].toString().trim().toLowerCase() : "";
    let rawColAA = (launchCol > -1 && psRow.length > launchCol && psRow[launchCol]) ? psRow[launchCol].toString().trim().toLowerCase() : "";
    let isLaunchSent = rawColAB === "sent" || rawColAB.includes("sent") || rawColAA === "sent";

    // Base Date for Check-In 1: Col V (Feedback Mail Date)
    let checkIn1RefDate = psRow[feedbackMailDateCol] || mainInfo.mgPayoutExited;
    let vDateObj = parseDateSafe(checkIn1RefDate);

    // Base Date for Check-In 2: Col X (Check-In 1 Sent Date)
    let rawCheckIn1DateX = (checkIn1DateCol > -1 && psRow.length > checkIn1DateCol) ? psRow[checkIn1DateCol] : null;
    let xDateObj = parseDateSafe(rawCheckIn1DateX);

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    // --- STAGE 5: CHECK-IN 1 (15 Days from Col V Feedback Mail Date) ---
    if (!targetStage || targetStage === "checkIn1") {
      if (checkIn1Col > -1) {
        let curW = (psRow.length > checkIn1Col && psRow[checkIn1Col]) ? psRow[checkIn1Col].toString().trim() : "";
        let curWLower = curW.toLowerCase();

        if (curWLower === "sent") {
          if (checkIn1DateCol > -1 && (!psRow[checkIn1DateCol] || psRow[checkIn1DateCol].toString().trim() === "")) {
            let now = new Date();
            psSheet.getRange(i + 1, checkIn1DateCol + 1).setValue(now);
            psRow[checkIn1DateCol] = now;
            Logger.log(`[ROW ${rowNum}] [Check-In 1 (15 Days)] Status is "Sent" but Col X Date was missing. Stamped Col X with ${now}.`);
          }
          Logger.log(`[ROW ${rowNum}] [Check-In 1 (15 Days)] Evaluated for "${title}" - Status: "Sent" (Already processed)`);
        } else if (isCheckInDropped) {
          Logger.log(`[ROW ${rowNum}] [Check-In 1 (15 Days)] Evaluated for "${title}" - Launch Status: "${launchStatus}" (Suppressed - Drop)`);
        } else if (isBeforeSept1) {
          if (curWLower !== "does not apply") {
            psSheet.getRange(i + 1, checkIn1Col + 1).setValue("Does not apply");
            psRow[checkIn1Col] = "Does not apply";
          }
          Logger.log(`[ROW ${rowNum}] [Check-In 1 (15 Days)] Evaluated for "${title}" - Signed before Sept 1. Status: "Does not apply"`);
        } else if (isLaunchSent) {
          if (curWLower !== "does not apply") {
            psSheet.getRange(i + 1, checkIn1Col + 1).setValue("Does not apply");
            psRow[checkIn1Col] = "Does not apply";
          }
          Logger.log(`[ROW ${rowNum}] [Check-In 1 (15 Days)] Evaluated for "${title}" - Show Launch Announcement Sent. Status: "Does not apply"`);
        } else if (!rawContractDate) {
          if (curWLower !== "not due yet") {
            psSheet.getRange(i + 1, checkIn1Col + 1).setValue("Not due yet");
            psRow[checkIn1Col] = "Not due yet";
          }
          Logger.log(`[ROW ${rowNum}] [Check-In 1 (15 Days)] Evaluated for "${title}" - Contract Date is blank. Status: "Not due yet"`);
        } else if (!vDateObj) {
          if (curWLower !== "not due yet") {
            psSheet.getRange(i + 1, checkIn1Col + 1).setValue("Not due yet");
            psRow[checkIn1Col] = "Not due yet";
          }
          Logger.log(`[ROW ${rowNum}] [Check-In 1 (15 Days)] Evaluated for "${title}" - Col V (Feedback Mail Date) is blank. Status: "Not due yet"`);
        } else {
          let targetV = new Date(vDateObj.getTime());
          targetV.setHours(0, 0, 0, 0);
          let diffDaysV = Math.floor((today.getTime() - targetV.getTime()) / (1000 * 60 * 60 * 24));

          if (diffDaysV < 15) {
            if (curWLower !== "not due yet") {
              psSheet.getRange(i + 1, checkIn1Col + 1).setValue("Not due yet");
              psRow[checkIn1Col] = "Not due yet";
            }
            Logger.log(`[ROW ${rowNum}] [Check-In 1 (15 Days)] Evaluated for "${title}" - Status: "Not due yet" (${diffDaysV}/15 days elapsed since Col V ${checkIn1RefDate})`);
          } else if (diffDaysV === 15) {
            if (curWLower !== "draft ready") {
              stage5Candidates.push({
                rowIdx: i,
                rowNum: rowNum,
                email: email,
                firstName: firstName,
                title: title.toString().trim(),
                dateKey: getStandardDateKey(checkIn1RefDate),
                rawDate: checkIn1RefDate,
                link: link,
                ccMail: ccMail,
                revLink: revLink,
                argus: argus,
                showName: showName,
                colIdx: checkIn1Col
              });
            } else {
              Logger.log(`[ROW ${rowNum}] [Check-In 1 (15 Days)] Evaluated for "${title}" - Status: "${curW}" (Already Draft Ready)`);
            }
          } else if (diffDaysV >= 16) {
            if (curWLower !== "overdue") {
              psSheet.getRange(i + 1, checkIn1Col + 1).setValue("Overdue");
              psRow[checkIn1Col] = "Overdue";
              Logger.log(`[ROW ${rowNum}] [STATUS UPDATE] 15th day is over (${diffDaysV} days elapsed). Updated Col W to "Overdue" for "${title}". (NO DRAFT CREATED)`);
            } else {
              Logger.log(`[ROW ${rowNum}] [Check-In 1 (15 Days)] Evaluated for "${title}" - Status: "Overdue" (${diffDaysV} days elapsed)`);
            }
          }
        }
      }
    }

    // --- STAGE 6: CHECK-IN 2 (15 Days from Col X Check-In 1 Sent Date) ---
    if (!targetStage || targetStage === "checkIn2") {
      if (checkIn2Col > -1) {
        let curY = (psRow.length > checkIn2Col && psRow[checkIn2Col]) ? psRow[checkIn2Col].toString().trim() : "";
        let curYLower = curY.toLowerCase();

        if (curYLower === "sent") {
          if (checkIn2DateCol > -1 && (!psRow[checkIn2DateCol] || psRow[checkIn2DateCol].toString().trim() === "")) {
            let now = new Date();
            psSheet.getRange(i + 1, checkIn2DateCol + 1).setValue(now);
            psRow[checkIn2DateCol] = now;
            Logger.log(`[ROW ${rowNum}] [Check-In 2 (30 Days)] Status is "Sent" but Col Z Date was missing. Stamped Col Z with ${now}.`);
          }
          Logger.log(`[ROW ${rowNum}] [Check-In 2 (30 Days)] Evaluated for "${title}" - Status: "Sent" (Already processed)`);
        } else if (isCheckInDropped) {
          Logger.log(`[ROW ${rowNum}] [Check-In 2 (30 Days)] Evaluated for "${title}" - Launch Status: "${launchStatus}" (Suppressed - Drop)`);
        } else if (isBeforeSept1) {
          if (curYLower !== "does not apply") {
            psSheet.getRange(i + 1, checkIn2Col + 1).setValue("Does not apply");
            psRow[checkIn2Col] = "Does not apply";
          }
          Logger.log(`[ROW ${rowNum}] [Check-In 2 (30 Days)] Evaluated for "${title}" - Signed before Sept 1. Status: "Does not apply"`);
        } else if (isLaunchSent) {
          if (curYLower !== "does not apply") {
            psSheet.getRange(i + 1, checkIn2Col + 1).setValue("Does not apply");
            psRow[checkIn2Col] = "Does not apply";
          }
          Logger.log(`[ROW ${rowNum}] [Check-In 2 (30 Days)] Evaluated for "${title}" - Show Launch Announcement Sent. Status: "Does not apply"`);
        } else if (!rawContractDate) {
          if (curYLower !== "not due yet") {
            psSheet.getRange(i + 1, checkIn2Col + 1).setValue("Not due yet");
            psRow[checkIn2Col] = "Not due yet";
          }
          Logger.log(`[ROW ${rowNum}] [Check-In 2 (30 Days)] Evaluated for "${title}" - Contract Date is blank. Status: "Not due yet"`);
        } else if (!xDateObj) {
          // Col X (Check-In 1 Sent Date) is missing & show launch email not sent -> Not due yet
          if (curYLower !== "not due yet") {
            psSheet.getRange(i + 1, checkIn2Col + 1).setValue("Not due yet");
            psRow[checkIn2Col] = "Not due yet";
          }
          Logger.log(`[ROW ${rowNum}] [Check-In 2 (30 Days)] Evaluated for "${title}" - Col X (Check-In 1 Date) is blank. Status: "Not due yet"`);
        } else {
          // Col X Date is present & show launch email not sent -> Evaluate X + 15 days
          let targetX = new Date(xDateObj.getTime());
          targetX.setHours(0, 0, 0, 0);
          let diffDaysX = Math.floor((today.getTime() - targetX.getTime()) / (1000 * 60 * 60 * 24));

          if (diffDaysX < 15) {
            if (curYLower !== "not due yet") {
              psSheet.getRange(i + 1, checkIn2Col + 1).setValue("Not due yet");
              psRow[checkIn2Col] = "Not due yet";
            }
            Logger.log(`[ROW ${rowNum}] [Check-In 2 (30 Days)] Evaluated for "${title}" - Status: "Not due yet" (${diffDaysX}/15 days elapsed since Col X ${rawCheckIn1DateX})`);
          } else if (diffDaysX === 15) {
            if (curYLower !== "draft ready") {
              stage6Candidates.push({
                rowIdx: i,
                rowNum: rowNum,
                email: email,
                firstName: firstName,
                title: title.toString().trim(),
                dateKey: getStandardDateKey(rawCheckIn1DateX),
                rawDate: rawCheckIn1DateX,
                link: link,
                ccMail: ccMail,
                revLink: revLink,
                argus: argus,
                showName: showName,
                colIdx: checkIn2Col
              });
            } else {
              Logger.log(`[ROW ${rowNum}] [Check-In 2 (30 Days)] Evaluated for "${title}" - Status: "${curY}" (Already Draft Ready)`);
            }
          } else if (diffDaysX >= 16) {
            if (curYLower !== "overdue") {
              psSheet.getRange(i + 1, checkIn2Col + 1).setValue("Overdue");
              psRow[checkIn2Col] = "Overdue";
              Logger.log(`[ROW ${rowNum}] [STATUS UPDATE] 15 days since Check-In 1 is over (${diffDaysX} days elapsed). Updated Col Y to "Overdue" for "${title}". (NO DRAFT CREATED)`);
            } else {
              Logger.log(`[ROW ${rowNum}] [Check-In 2 (30 Days)] Evaluated for "${title}" - Status: "Overdue" (${diffDaysX} days elapsed)`);
            }
          }
        }
      }
    }
    SpreadsheetApp.flush();

    // =============================================================
    // Stage 7: Show Launch Announcement
    // Strict Guard:
    // 1. Both Show ID AND Show Link MUST be present and valid!
    //    If Show ID or Show Link is not present -> NO DRAFT!
    // 2. Col AA (Show Launch Announcement Status) must NOT be "Not launched / Not Live / Unavailable"
    // 3. Col AB (Show Launch Announcement Sent) must NOT be "Not launched / Not Live / Unavailable"
    // 4. Status != Drop/Bad/Untested
    // =============================================================
    if (!targetStage || targetStage === "launch") {
      let rawValAA = (launchCol > -1 && psRow.length > launchCol && psRow[launchCol]) 
                     ? psRow[launchCol].toString().trim() 
                     : "";
      let rawValAALower = rawValAA.toLowerCase();

      let rawValAB = (launchSentCol > -1 && psRow.length > launchSentCol && psRow[launchSentCol]) 
                     ? psRow[launchSentCol].toString().trim() 
                     : "";
      let rawValABLower = rawValAB.toLowerCase();

      // Helper: Check if Col AA or Col AB indicates "Not launched / Not Live / Unavailable / Discontinued"
      const isNotLaunchedStatus = (val) => {
        if (!val) return false;
        let v = val.toLowerCase().trim();
        return v.includes("not launch") || 
               v.includes("not live") || 
               v.includes("unavail") || 
               v.includes("not avail") || 
               v === "unlaunched" || 
               v === "no" ||
               v.includes("pending launch") ||
               v.includes("discontinue");
      };

      let isAANotLaunched = isNotLaunchedStatus(rawValAALower);
      let isABNotLaunched = isNotLaunchedStatus(rawValABLower);

      let hasShowId = showId && showId.toString().trim() !== "" && !showId.toString().includes("#REF") && !showId.toString().includes("#N/A");
      let isLiveUrl = link && (link.toString().trim().startsWith("http") || link.toString().trim().includes("pocketfm")) && !link.toString().includes("#REF") && !link.toString().includes("#N/A");
      let isEligibleLaunchStatus = !launchStatus.includes("drop") && !launchStatus.includes("bad") && !launchStatus.includes("untested") && !launchStatus.includes("discontinue");

      let targetLaunchCol = launchSentCol > -1 ? launchSentCol : launchCol;

      // 1. Already Sent check
      if (rawValABLower === "sent" || rawValAALower === "sent") {
        Logger.log(`[ROW ${rowNum}] [Show Launch Announcement] Evaluated for "${title}" - Status: "Sent" (Already processed)`);
      }
      // 2. Already Draft Ready check
      else if (rawValABLower === "draft ready" || rawValAALower === "draft ready") {
        Logger.log(`[ROW ${rowNum}] [Show Launch Announcement] Evaluated for "${title}" - Status: "Draft Ready"`);
      }
      // 3. User Guard: If Show ID or Show Link not present, or Col AA / Col AB is "Not launched / Not Live / Unavailable" -> NO DRAFT!
      else if (!hasShowId || !isLiveUrl || isAANotLaunched || isABNotLaunched) {
        let reasons = [];
        if (!hasShowId) reasons.push("Show ID not present");
        if (!isLiveUrl) reasons.push("Show Link not present or not live URL");
        if (isAANotLaunched) reasons.push(`Col AA is "${rawValAA}"`);
        if (isABNotLaunched) reasons.push(`Col AB is "${rawValAB}"`);
        Logger.log(`[ROW ${rowNum}] [Show Launch Announcement] [SUPPRESSED - NO DRAFT] ${reasons.join(", ")} for "${title}". No draft generated.`);
      }
      // 4. Workflow status check (Dropped / Bad)
      else if (!isEligibleLaunchStatus) {
        Logger.log(`[ROW ${rowNum}] [Show Launch Announcement] Evaluated for "${title}" - Launch Status: "${launchStatus}" (Suppressed - Drop/Bad/Untested/Discontinued)`);
      }
      // 5. All conditions met: Valid Show ID, live Show Link, eligible status, and Col AA/AB is ready!
      else {
        createDraft(email, `Your Pocket FM Show Is Now Live`, firstName, 'launch', title, link, i, targetLaunchCol, null, ccMail, revLink, argus, showName);
        if (launchSentCol > -1) {
          psSheet.getRange(i + 1, launchSentCol + 1).setValue("Draft Ready");
        }
        if (launchCol > -1) {
          let curAAFormula = psSheet.getRange(i + 1, launchCol + 1).getFormula();
          if (!curAAFormula) {
            psSheet.getRange(i + 1, launchCol + 1).setValue("Draft Ready");
          }
        }
        SpreadsheetApp.flush();
        Logger.log(`[ROW ${rowNum}] [Show Launch Announcement] [DRAFT CREATED] Show ID ("${showId}"), live Link ("${link}"), and Status ("${launchStatus}") verified. Created draft and updated Col AB/AA to "Draft Ready"`);
      }
    }

    // =============================================================
    // Stage 8: Newsletter Edit (The Author Edit)
    // STRICT OPERATIONAL RULE:
    // 1. MUST ONLY consider Column AC (Show Launch Announcement Email Sent Date)!
    //    DO NOT consider Column J (Launch Date)!
    // 2. If Col AC (Launch Announcement Sent Date) is blank, missing, or invalid -> STRICTLY NO DRAFT!
    // 3. Col AC Date MUST be 15 days ago or more (diffDays >= 15)!
    // 4. Col AD (Newsletter Edit) must NOT be "Sent" or "Draft Ready"!
    // 5. Show Link (Col L / Col AG) must be an active live URL!
    // =============================================================
    if (!targetStage || targetStage === "newsletter") {
      let isLiveUrl = link && (link.toString().trim().startsWith("http") || link.toString().trim().includes("pocketfm"));
      
      // STRICT: ONLY consider Column AC (launchSentDateCol), NEVER Column J (psLaunchDateCol)
      let rawColAcDate = (launchSentDateCol > -1 && psRow.length > launchSentDateCol && psRow[launchSentDateCol])
                         ? psRow[launchSentDateCol]
                         : null;
      let parsedColAcDate = parseDateSafe(rawColAcDate);
      let hasColAcDate = parsedColAcDate !== null;
      let isColAc15DaysAgoOrMore = hasColAcDate ? isDaysAgoOrMore(rawColAcDate, 15) : false;

      if (newsletterCol !== -1) {
        let curNews = (psRow.length > newsletterCol && psRow[newsletterCol]) ? psRow[newsletterCol].toString().trim() : "";
        let curNewsLower = curNews.toLowerCase();
        let isManuallyMarked = curNewsLower === "newsletter" || curNewsLower === "author edit" || curNewsLower === "draft";

        // 1. Already Sent check
        if (curNewsLower === "sent") {
          Logger.log(`[ROW ${rowNum}] [Newsletter / Author Edit] Evaluated for "${title}" - Status: "Sent" (Already processed)`);
        }
        // 2. Already Draft Ready check (skip duplicate creation unless manually marked)
        else if (curNewsLower === "draft ready" && !isManuallyMarked) {
          Logger.log(`[ROW ${rowNum}] [Newsletter / Author Edit] Evaluated for "${title}" - Status: "Draft Ready" (Already prepared)`);
        }
        // 3. STRICT GUARD: Column AC (Launch Announcement Sent Date) MUST be present!
        else if (!hasColAcDate && !isManuallyMarked) {
          Logger.log(`[ROW ${rowNum}] [Newsletter / Author Edit] [SUPPRESSED - NO DRAFT] Col AC (Show Launch Announcement Email Sent Date) is blank/missing for "${title}". Launch Announcement must be sent first. Draft NOT created.`);
        }
        // 4. STRICT GUARD: Show Link MUST be a live URL!
        else if (!isLiveUrl) {
          Logger.log(`[ROW ${rowNum}] [Newsletter / Author Edit] [SUPPRESSED - NO DRAFT] Show Link is missing or not live URL for "${title}". Value: "${link || 'Blank'}". Draft NOT created.`);
        }
        // 5. TIMELINE CHECK: Column AC Date MUST be 15 days ago or more!
        else if (!isColAc15DaysAgoOrMore && !isManuallyMarked) {
          Logger.log(`[ROW ${rowNum}] [Newsletter / Author Edit] [SUPPRESSED - NOT DUE] Col AC Launch Announcement Sent Date (${rawColAcDate}) has not reached 15 days elapsed yet for "${title}".`);
        }
        // 6. ALL CONDITIONS SATISFIED: Valid Col AC Date, live Link, 15+ days elapsed!
        else {
          createDraft(email, `What’s new at Pocket FM + a few things worth knowing`, firstName, 'authorEdit', title, link, i, newsletterCol, null, ccMail, revLink, argus, showName);
          if (newsletterCol > -1) {
            psSheet.getRange(i + 1, newsletterCol + 1).setValue("Draft Ready");
          }
          SpreadsheetApp.flush();
          Logger.log(`[ROW ${rowNum}] [Newsletter / Author Edit] [DRAFT CREATED] Valid Col AC Date (${rawColAcDate}) and Live Link verified for "${title}". Updated Col AD in "${psSheet.getName()}" to "Draft Ready".`);
        }
      }
    }

    // =============================================================
    // Stages 9A, 9B, 9C: Revenue Statements (Approved Columns AI to AM)
    // Mapped directly to Sheet 'Launch Status' Dropdown Options:
    //   - 'Testing'               -> Stage 9 (Worked Well: 9A Content + 9B Payment)
    //   - 'Testing_PGC_Completed' -> Stage 9 (Worked Well: 9A Content + 9B Payment)
    //   - 'Testing_PGC'           -> Stage 9 (Worked Well: 9A Content + 9B Payment)
    //   - 'Launched (ROW)'        -> Stage 9 (Worked Well: 9A Content + 9B Payment)
    //   - 'Dropped'               -> Stage 10 / 9C (Didn't Work Well - Content + Payment Related Update)
    //   - 'Bad'                   -> Stage 10 / 9C (Didn't Work Well - Content + Payment Related Update)
    //   - 'Show Discontinued'     -> Stage 10 / 9C (Didn't Work Well - Content + Payment Related Update)
    //   - 'Untested'              -> On Hold / Pending (Suppressed from 9 & 10)
    //   - 'Average'               -> Under Evaluation (Suppressed from 9 & 10 unless marked Dropped/Bad/Discontinued)
    // Approved Progress Columns: Col AL (Drive Link), Col AM (Sent Progress Dropdown), Col AJ (Status)
    // =============================================================
    if (!targetStage || targetStage === "revStatement" || targetStage.startsWith("revStatement_") || targetStage === "contentBad") {
      let isShowDropped = isRowDropped || 
                          launchStatus.includes("dropped") || 
                          launchStatus.includes("drop") || 
                          launchStatus.includes("bad") || 
                          launchStatus.includes("sunset") ||
                          launchStatus.includes("discontinue");
      let isTestingPgcOrLaunched = !isShowDropped && (launchStatus.includes("testing") || launchStatus.includes("launched"));
      let hasArgusData = showId && (
        (argusData && argusData[showId.toLowerCase().trim()]) || 
        (argusData && argusData[safeTitle]) || 
        (argus && (argus.duration !== "N/A" || argus.ldau !== "N/A")) ||
        !argusSheet
      );

      let targetRevCol = (typeof jasSentCol !== "undefined" && jasSentCol !== -1) ? jasSentCol : 38; // Col AM (index 38, 1-based Col 39)
      let curRevStatus = (targetRevCol > -1 && psRow.length > targetRevCol && psRow[targetRevCol]) ? psRow[targetRevCol].toString().trim().toLowerCase() : "";
      let curRevEmailStatus = (typeof jasStatusCol !== "undefined" && jasStatusCol > -1 && psRow.length > jasStatusCol && psRow[jasStatusCol]) ? psRow[jasStatusCol].toString().trim().toLowerCase() : "";

      // Strict suppression if already Sent or Draft Ready to prevent duplicate drafts/emails
      const isRevProcessed = curRevStatus === "sent" || 
                             curRevStatus === "draft ready" || 
                             curRevStatus === "ready" ||
                             curRevEmailStatus === "sent" || 
                             curRevEmailStatus === "draft ready";

      // Strict Revenue Statement Link Validation (Col AL):
      // If Revenue Statement Link is missing, blank, or placeholder/text (e.g. "Show Untested / Never Made Live"),
      // DO NOT create drafts and DO NOT mark Draft Ready in Col AM!
      const hasValidRevLink = isValidWebUrl(revLink);

      if (isRevProcessed) {
        Logger.log(`[ROW ${rowNum}] [Rev Statement] Evaluated for "${title}" - Col AM Status: "${curRevStatus || curRevEmailStatus}" (Already processed / Draft Ready - Skipped duplicate creation)`);
      } else if (!hasValidRevLink) {
        let rawVal = (revLinkRaw ? revLinkRaw.toString().trim() : "Blank");
        Logger.log(`[ROW ${rowNum}] [Rev Statement] [SKIPPED] Missing or non-URL Revenue Statement link in Col AL for "${title}" (Found: "${rawVal}"). Draft creation suppressed; Col AM untouched.`);
        logNotification("Missing Revenue Statement Link", title, `Revenue Statement draft suppressed for "${title}" because Column AL does not contain a valid URL link (Found: "${rawVal}").`, rowNum);
      } else {
        if (isShowDropped) {
          // Stage 9C: Sunset / Dropped / Content Bad ONLY (Mutually exclusive from 9A & 9B)
          if (!targetStage || targetStage === "revStatement" || targetStage === "revStatement_didntWorkWell" || targetStage === "contentBad") {
            if (hasArgusData || (showId && !argusSheet)) {
              createDraft(email, `Pocket FM: An Update on ${title}`, firstName, 'revStatement_didntWorkWell', title, link, i, targetRevCol, null, ccMail, revLink, argus, showName);
              Logger.log(`[ROW ${rowNum}] [Stage 9C: Content Bad / Sunset / Dropped] [DRAFT CREATED] Status == Dropped/Bad & Show ID in Argus for "${title}". Progress stored in Col AM.`);
            } else {
              Logger.log(`[ROW ${rowNum}] [Stage 9C: Content Bad / Sunset / Dropped] [SKIPPED] Show "${title}" is Dropped/Bad but Show ID ("${showId || 'Blank'}") is not found in Argus Data.`);
            }
          }
        } else if (isTestingPgcOrLaunched) {
          // Stage 9A: Content Review
          if (!targetStage || targetStage === "revStatement" || targetStage === "revStatement_workedWell" || targetStage === "revStatement_workedWell_content") {
            if (hasArgusData || (showId && !argusSheet)) {
              createDraft(email, `Content Update for ${title}`, firstName, 'revStatement_workedWell_content', title, link, i, targetRevCol, null, ccMail, revLink, argus, showName);
              Logger.log(`[ROW ${rowNum}] [Stage 9A: Content Review] [DRAFT CREATED] Status in [Testing, Testing_PGC, Testing_PGC_Completed, Launched (ROW)] & Show ID in Argus for "${title}". Progress stored in Col AM.`);
            }
          }

          // Stage 9B: Payment Ready
          if (!targetStage || targetStage === "revStatement" || targetStage === "revStatement_workedWell" || targetStage === "revStatement_workedWell_payment") {
            createDraft(email, "Pocket FM: Your earnings are waiting for you!", firstName, 'revStatement_workedWell_payment', title, link, i, targetRevCol, null, ccMail, revLink, argus, showName);
            Logger.log(`[ROW ${rowNum}] [Stage 9B: Payment Ready] [DRAFT CREATED] Status in [Testing, Testing_PGC, Testing_PGC_Completed, Launched (ROW)] for "${title}". Progress stored in Col AM.`);
          }
        } else {
          Logger.log(`[ROW ${rowNum}] [Rev Statement] Evaluated for "${title}" - Launch Status: "${launchStatus}" (Not eligible for 9A/9B or 9C)`);
        }
      }
    }
  }

  // =============================================================
  // PROCESS MULTI-TITLE CONSOLIDATED OUTREACH QUEUES (STAGES 1-6)
  // Ensures authors with 2+ titles on the same date receive 1 unified draft
  // capturing ALL qualifying titles, with strict same date verification!
  // =============================================================
  function processGroupedCandidates(candidates, stageKey, stageLabel, subjectGenerator) {
    if (!candidates || candidates.length === 0) return;

    let groups = {};
    for (let c of candidates) {
      let gKey = cleanEmail(c.email).toLowerCase() + "___" + (c.dateKey || "unknown");
      if (!groups[gKey]) {
        groups[gKey] = [];
      }
      groups[gKey].push(c);
    }

    for (let gKey in groups) {
      let groupItems = groups[gKey];
      let rowIndices = groupItems.map(item => item.rowIdx);
      let rowNums = groupItems.map(item => item.rowNum);
      let rowNumStr = rowNums.join(", ");

      // Deduplicate titles while preserving encounter order
      let uniqueTitles = [];
      for (let item of groupItems) {
        let t = item.title;
        if (t && !uniqueTitles.includes(t)) {
          uniqueTitles.push(t);
        }
      }
      let combinedTitle = uniqueTitles.join(", ");
      let firstItem = groupItems[0];

      // Combine CC mail if multiple rows have different CC addresses
      let allCcs = [];
      for (let item of groupItems) {
        if (item.ccMail) {
          item.ccMail.split(/[,;]/).forEach(c => {
            let cl = cleanEmail(c);
            if (cl && isValidEmail(cl) && !allCcs.includes(cl)) allCcs.push(cl);
          });
        }
      }
      let combinedCc = allCcs.join(", ");

      let subject = typeof subjectGenerator === "function" 
                    ? subjectGenerator(combinedTitle) 
                    : subjectGenerator;

      createDraft(
        firstItem.email,
        subject,
        firstItem.firstName,
        stageKey,
        combinedTitle,
        firstItem.link,
        rowIndices, // Pass array of row indices!
        firstItem.colIdx,
        null,
        combinedCc,
        firstItem.revLink,
        firstItem.argus,
        firstItem.showName
      );

      if (uniqueTitles.length > 1) {
        Logger.log(`[ROWS ${rowNumStr}] [${stageLabel}] [CONSOLIDATED DRAFT] Same date (${firstItem.dateKey}) check verified. Created 1 consolidated draft for ${uniqueTitles.length} titles ("${combinedTitle}") sent to ${firstItem.email}`);
      } else {
        Logger.log(`[ROW ${rowNumStr}] [${stageLabel}] [DRAFT CREATED] Created draft for "${combinedTitle}" (${firstItem.email})`);
      }
    }
  }

  if (!targetStage || targetStage === 'welcome') {
    processGroupedCandidates(stage1Candidates, 'welcome', 'Welcome Email', 'Welcome to Pocket FM - here\'s what happens next');
  }
  if (!targetStage || targetStage === 'vendor') {
    processGroupedCandidates(stage2Candidates, 'vendor', 'Vendor Onboarding', (t) => 'Vendor Onboarding for ' + t);
  }
  if (!targetStage || targetStage === 'mgInitiated') {
    processGroupedCandidates(stage3Candidates, 'mgInitiated', 'MG Payment Initiated', (t) => 'Payment Initiated: Minimum Guarantee for ' + t);
  }
  if (!targetStage || targetStage === 'mgConfirmed') {
    processGroupedCandidates(stage4Candidates, 'mgConfirmed', 'MG Payment Processed', 'Pocket FM: Your Minimum Guarantee Payment Has Been Processed');
  }
  if (!targetStage || targetStage === 'checkIn1') {
    processGroupedCandidates(stage5Candidates, 'checkIn1', 'Check-In 1 (15 Days)', (t) => 'We\'d love your thoughts on ' + t);
  }
  if (!targetStage || targetStage === 'checkIn2') {
    processGroupedCandidates(stage6Candidates, 'checkIn2', 'Check-In 2 (30 Days)', (t) => 'Pocket FM: A quick update on your show: ' + t);
  }

  // Force all spreadsheet updates to commit to the live sheet immediately
  SpreadsheetApp.flush();

  // Summary Notification Report
  if (notificationLog.length > 0) {
    Logger.log("\n==================== RECOMMENDED NOTIFICATIONS SUMMARY (ATTENTION ITEMS ONLY) ====================");
    Logger.log(`Total attention notifications recorded: ${notificationLog.length}`);
    Logger.log("NOTE: The rows listed below require manual attention (missing emails, invalid launch statuses, or missing dates). All other rows passed evaluation or are already processed.");
    notificationLog.forEach(n => Logger.log(n.fullLog));
    Logger.log("===================================================================================================\n");
  } else {
    Logger.log("\nAll evaluated records passed eligibility checks with 0 attention items.\n");
  }
}

// Handler function that Google's servers will run automatically 6 hours later
function runDelayedDrafts() {
  processOutreachQueue(true);
}

/**
 * EVALUATES A SINGLE ROW FOR SHOW LAUNCH ANNOUNCEMENT DRAFT & STATUS
 * @param {Sheet} psSheet - The Post-Sales Tracker sheet object
 * @param {number} row - The 1-based row index in the sheet (e.g. 4 for Row 4)
 * @param {Array} preloadedRowVals - Optional preloaded row values to avoid redundant sheet reads
 * @param {Array} preloadedHeaders - Optional preloaded headers
 */
function evaluateSingleRowLaunch(psSheet, row, preloadedRowVals = null, preloadedHeaders = null) {
  if (!psSheet || row < 4) return;

  const lastCol = Math.max(psSheet.getLastColumn(), 30);
  const headers = preloadedHeaders || psSheet.getRange(3, 1, 1, lastCol).getValues()[0];
  const rowVals = preloadedRowVals || psSheet.getRange(row, 1, 1, lastCol).getValues()[0];

  const psFindCol = (name) => headers.findIndex(h => h.toString().toLowerCase().includes(name.toLowerCase()));

  const titleCol = psFindCol("Title / IP") > -1 ? psFindCol("Title / IP") : 2;

  // STRICT BLANK ROW GUARD: Do not process blank or unpopulated rows
  if (!isTrackerRowFilled(rowVals, titleCol)) {
    return;
  }

  const authorCol = psFindCol("Author Name") > -1 ? psFindCol("Author Name") : 1;
  const firstNameCol = psFindCol("Receiver First Name") > -1 ? psFindCol("Receiver First Name") : 7;
  const emailCol = psFindCol("Receiver Email ID") > -1 ? psFindCol("Receiver Email ID") : 5;
  const ccCol = psFindCol("CC Mail ID") > -1 ? psFindCol("CC Mail ID") : 6;
  const showNameCol = psFindCol("Show Name") > -1 ? psFindCol("Show Name") : 2;
  const linkCol = psFindCol("Show Link") > -1 ? psFindCol("Show Link") : 11;
  const statusCol = psFindCol("Launch Status") > -1 ? psFindCol("Launch Status") : 10;

  // Col AA (26), Col AB (27), Col AC (28)
  const colAA = headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return (s.includes("launch") && s.includes("announcement") && s.includes("status")) || s === "show launch announcement status";
  }) > -1 ? headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return (s.includes("launch") && s.includes("announcement") && s.includes("status")) || s === "show launch announcement status";
  }) : 26;

  const colAB = headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return (s.includes("launch") && s.includes("announcement") && (s.includes("sent") || s.includes("email sent")) && !s.includes("date"));
  }) > -1 ? headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return (s.includes("launch") && s.includes("announcement") && (s.includes("sent") || s.includes("email sent")) && !s.includes("date"));
  }) : 27;

  const colAC = headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return (s.includes("launch") && s.includes("announcement") && s.includes("date")) || (s.includes("launch") && s.includes("sent") && s.includes("date"));
  }) > -1 ? headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return (s.includes("launch") && s.includes("announcement") && s.includes("date")) || (s.includes("launch") && s.includes("sent") && s.includes("date"));
  }) : 28;

  const title = rowVals[titleCol] ? rowVals[titleCol].toString().trim() : "";
  const author = rowVals[authorCol] ? rowVals[authorCol].toString().trim() : "";
  const rawFirstName = rowVals[firstNameCol] ? rowVals[firstNameCol].toString().trim() : "";
  const firstName = rawFirstName !== "" ? rawFirstName : (author ? author.split(" ")[0] : "Creator");
  const showName = rowVals[showNameCol] ? rowVals[showNameCol].toString().trim() : title;
  const email = cleanEmail(rowVals[emailCol]);
  const ccMail = cleanCcList(rowVals[ccCol]);
  const link = rowVals[linkCol] ? rowVals[linkCol].toString().trim() : "";
  const rawStatus = rowVals[statusCol] ? rowVals[statusCol].toString().trim().toLowerCase() : "";

  const showIdCol = psFindCol("Show ID") > -1 ? psFindCol("Show ID") : 8;
  const rawShowId = (showIdCol > -1 && rowVals.length > showIdCol && rowVals[showIdCol]) ? rowVals[showIdCol].toString().trim() : "";
  const hasShowId = rawShowId && rawShowId !== "" && !rawShowId.includes("#REF") && !rawShowId.includes("#N/A");

  const curDropdown = rowVals[colAB] ? rowVals[colAB].toString().trim() : "";
  const curDropdownLower = curDropdown.toLowerCase();
  const curAAVal = (colAA > -1 && rowVals.length > colAA && rowVals[colAA]) ? rowVals[colAA].toString().trim() : "";
  const curAALower = curAAVal.toLowerCase();

  // If already marked Sent or Draft Ready, do not alter
  if (curDropdownLower === "sent" || curAALower === "sent") return;
  if (curDropdownLower === "draft ready" || curAALower === "draft ready") return;

  // Helper: Check if Col AA or Col AB indicates "Not launched / Not Live / Unavailable / Discontinued"
  const isNotLaunchedStatus = (val) => {
    if (!val) return false;
    let v = val.toLowerCase().trim();
    return v.includes("not launch") || 
           v.includes("not live") || 
           v.includes("unavail") || 
           v.includes("not avail") || 
           v === "unlaunched" || 
           v === "no" ||
           v.includes("pending launch") ||
           v.includes("discontinue");
  };

  const isAANotLaunched = isNotLaunchedStatus(curAALower);
  const isABNotLaunched = isNotLaunchedStatus(curDropdownLower);

  // Stage 7 Conditions: Col AG: Show Link IS LIVE URL | Col AA: Status != Drop/Bad/Untested/Discontinued
  const isLiveUrl = link && (link.toString().trim().startsWith("http") || link.toString().trim().includes("pocketfm")) && !link.includes("#REF") && !link.includes("#N/A");
  const isEligibleLaunchStatus = !rawStatus.includes("drop") && !rawStatus.includes("bad") && !rawStatus.includes("untested") && !rawStatus.includes("discontinue");

  // Strict guard: If Show ID or Show Link not present, or Col AA / Col AB is "Not launched / Not Live / Unavailable" -> NO DRAFT!
  if (!hasShowId || !isLiveUrl || isAANotLaunched || isABNotLaunched) {
    Logger.log(`[LIVE ROW ${row}] [Show Launch Announcement] [SUPPRESSED - NO DRAFT] Show ID or Show Link not present, or Col AA/AB is Not launched/Not Live/Unavailable for "${title}". Draft suppressed.`);
    return;
  }

  if (isEligibleLaunchStatus) {
    if (!isValidEmail(email)) {
      Logger.log(`[LIVE ROW ${row}] Missing valid email for "${title}". Draft suppressed.`);
      return;
    }

    if (curDropdownLower !== "draft ready") {
      const grammar = { work: "work", is: "is", has: "has", title: "title", this: "this", it: "it", its: "its" };
      const queueId = Utilities.getUuid();
      const bodyContent = getBody('launch', firstName, title, link, grammar, "", null, showName);
      const wrappedBody = wrapHtml(bodyContent, queueId);
      const subject = `Your Pocket FM Show Is Now Live`;

      let draftSuccess = false;
      try {
        let draftOpts = { htmlBody: wrappedBody };
        if (ccMail) draftOpts.cc = ccMail;
        GmailApp.createDraft(email, subject, "", draftOpts);
        draftSuccess = true;
        Logger.log(`[LIVE ROW ${row}] SUCCESS: Draft created for "${title}" (${email})`);
      } catch (err) {
        Logger.log(`[LIVE ROW ${row}] ERROR creating draft for "${title}": ${err.message}`);
      }

      if (draftSuccess) {
        psSheet.getRange(row, colAB + 1).setValue("Draft Ready");
        const curAAFormula = psSheet.getRange(row, colAA + 1).getFormula();
        if (!curAAFormula) {
          psSheet.getRange(row, colAA + 1).setValue("Draft Ready");
        }
        // Col AC sent date is left blank upon draft creation; stamped strictly by syncSentEmails when dispatched!
        SpreadsheetApp.flush();
        Logger.log(`[LIVE ROW ${row}] Updated Col AB & AA to "Draft Ready".`);
      }
    }
  }
}

function generateAllLaunchAnnouncements() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet() || SpreadsheetApp.openById("1JFT4_f9Du6UZWi6aM0FjYvyR-mcAsbARq7JyxJwLPZc");
  let psSheet = null;

  psSheet = (typeof getPostSalesTrackerSheet === 'function') ? getPostSalesTrackerSheet(spreadsheet) : null;
  if (!psSheet) {
    for (let s of spreadsheet.getSheets()) {
      let sName = s.getName().toLowerCase().trim().replace("–", "-").replace("—", "-");
      if (sName === "post-sales tracker" || sName === "post sales tracker" || (sName.includes("post-sales") && !sName.includes("comms") && !sName.includes("stage"))) { psSheet = s; break; }
    }
  }

  if (!psSheet) {
    Logger.log("[ERROR] Post-Sales Tracker sheet tab not found!");
    return;
  }

  const lastRow = psSheet.getLastRow();
  const lastCol = Math.max(psSheet.getLastColumn(), 30);
  const allData = psSheet.getRange(1, 1, lastRow, lastCol).getValues();
  const headers = allData[2]; // Row 3
  const titleCol = headers.findIndex(h => h.toString().toLowerCase().includes("title")) > -1 
                   ? headers.findIndex(h => h.toString().toLowerCase().includes("title")) : 2;

  Logger.log("\n==================================================================");
  Logger.log(`DYNAMIC BATCH SCAN: Evaluating filled rows in "${psSheet.getName()}" (ignoring blank rows)`);
  Logger.log("==================================================================");

  let evaluatedCount = 0;
  let skippedBlankCount = 0;

  for (let r = 4; r <= lastRow; r++) {
    let rowVals = allData[r - 1];
    if (!isTrackerRowFilled(rowVals, titleCol)) {
      skippedBlankCount++;
      continue;
    }
    evaluateSingleRowLaunch(psSheet, r, rowVals, headers);
    evaluatedCount++;
  }

  SpreadsheetApp.flush();
  Logger.log(`\nBATCH SCAN COMPLETED: Evaluated ${evaluatedCount} filled rows dynamically (${skippedBlankCount} blank rows skipped).`);
}

/**
 * TEST CASE A: Launch Date <= Script Date Anomaly Check
 * If scripts received on Oct 6th and launch is Oct 2nd -> DRAFT IS NOT GENERATED!
 * Live Sheet Update: Column AB turns to "Launch Date Issue", Column AA turns to "Check with content".
 */
/**
 * TEST FUNCTION: Show Launch Announcement (Stage 7)
 * Conditions: Col AG: Show Link IS LIVE URL | Col AA: Status != Drop/Bad
 */
function testShowLaunchAnnouncement() {
  Logger.log("\n=======================================================");
  Logger.log("RUNNING TEST: SHOW LAUNCH ANNOUNCEMENT (STAGE 7)");
  Logger.log("=======================================================");

  const testTitle = "A Shade of Vampire Series";
  const testShowName = "A Shade of Vampire";
  const testFirstName = "Bella";
  const testLink = "https://pocketfm.onelink.me/2IE7/qgh3r7hu";
  const testStatus = "testing_pgc";
  const myEmail = Session.getActiveUser().getEmail();

  const isLiveUrl = testLink && (testLink.startsWith("http") || testLink.includes("pocketfm"));
  const isEligibleLaunchStatus = !testStatus.includes("drop") && !testStatus.includes("bad");

  if (isLiveUrl && isEligibleLaunchStatus) {
    const grammar = { work: "work", is: "is", has: "has", title: "title", this: "this", it: "it", its: "its" };
    const queueId = Utilities.getUuid();
    const bodyContent = getBody('launch', testFirstName, testTitle, testLink, grammar, "", null, testShowName);
    const wrappedBody = wrapHtml(bodyContent, queueId);
    const subject = `Your Pocket FM Show Is Now Live`;

    GmailApp.createDraft(myEmail, subject, "", { htmlBody: wrappedBody });
    Logger.log(`SUCCESS: Test Show Launch Announcement Draft created for ${myEmail}`);
  } else {
    Logger.log(`Result: FAIL - Conditions not satisfied.`);
  }
  Logger.log("=======================================================\n");
}

// =============================================================
// DYNAMIC AUTHOR CHECK-IN (15 & 30 DAYS) AUTOMATION FOR ALL ROWS
// =============================================================

/**
 * EVALUATES A SINGLE ROW FOR AUTHOR CHECK-IN (15 & 30 DAYS) DRAFTS AND STATUS
 * @param {Sheet} psSheet - The Post-Sales Tracker sheet object
 * @param {number} row - The 1-based row index in the sheet (e.g. 4 for Row 4)
 * @param {Array} preloadedRowVals - Optional preloaded row values to avoid redundant sheet reads
 * @param {Array} preloadedHeaders - Optional preloaded headers
 */
function evaluateSingleRowCheckIns(psSheet, row, preloadedRowVals = null, preloadedHeaders = null) {
  if (!psSheet || row < 4) return;

  const lastCol = Math.max(psSheet.getLastColumn(), 30);
  const headers = preloadedHeaders || psSheet.getRange(3, 1, 1, lastCol).getValues()[0];
  const rowVals = preloadedRowVals || psSheet.getRange(row, 1, 1, lastCol).getValues()[0];

  const psFindCol = (name) => headers.findIndex(h => h.toString().toLowerCase().includes(name.toLowerCase()));

  const titleCol = psFindCol("Title / IP") > -1 ? psFindCol("Title / IP") : 2;

  // STRICT BLANK ROW GUARD: Do not process blank or unpopulated rows
  if (!isTrackerRowFilled(rowVals, titleCol)) {
    return;
  }
  const authorCol = psFindCol("Author Name") > -1 ? psFindCol("Author Name") : 1;
  const firstNameCol = psFindCol("Receiver First Name") > -1 ? psFindCol("Receiver First Name") : 7;
  const emailCol = psFindCol("Receiver Email ID") > -1 ? psFindCol("Receiver Email ID") : 5;
  const ccCol = psFindCol("CC Mail ID") > -1 ? psFindCol("CC Mail ID") : 6;
  const showNameCol = psFindCol("Show Name") > -1 ? psFindCol("Show Name") : 12; // Col M (index 12)
  const linkCol = psFindCol("Show Link") > -1 ? psFindCol("Show Link") : 11; // Col L (index 11)
  const statusCol = psFindCol("Launch Status") > -1 ? psFindCol("Launch Status") : 10; // Col K (index 10)
  const contractDateCol = psFindCol("Contract Signing date") > -1 
                          ? psFindCol("Contract Signing date") 
                          : (psFindCol("Contract") > -1 ? psFindCol("Contract") : 3); // Col D (idx 3)

  let launchCol = headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return (s.includes("launch") && s.includes("announcement") && s.includes("status")) ||
           (s === "show launch announcement status");
  });
  if (launchCol === -1) launchCol = psFindCol("Show Launch Announcement") > -1 ? psFindCol("Show Launch Announcement") : 26; // Col AA (idx 26)

  let launchSentCol = headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return (s.includes("launch") && s.includes("announcement") && (s.includes("sent") || s.includes("email sent")) && !s.includes("date"));
  });
  if (launchSentCol === -1) {
    if (headers.length > 27 && (headers[27].toString().trim().toLowerCase() === "er" || headers[27].toString().toLowerCase().includes("sent"))) {
      launchSentCol = 27; // Column AB (idx 27)
    } else if (launchCol !== -1 && launchCol + 1 < headers.length) {
      launchSentCol = launchCol + 1;
    } else {
      launchSentCol = 27;
    }
  }

  // Feedback Mail Date (Col V)
  const feedbackMailDateCol = headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("feedback") && s.includes("date");
  }) > -1 ? headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("feedback") && s.includes("date");
  }) : 21;

  // Author Check-In 15 Days (Col W)
  const checkIn1Col = headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("15 days") && !s.includes("newsletter") && !s.includes("date");
  }) > -1 ? headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("15 days") && !s.includes("newsletter") && !s.includes("date");
  }) : 22;

  // Author Check-In 15 Days DATE (Col X)
  const checkIn1DateCol = headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("15 days") && !s.includes("newsletter") && s.includes("date");
  }) > -1 ? headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("15 days") && !s.includes("newsletter") && s.includes("date");
  }) : 23;

  // Author Check-In 30 Days (Col Y)
  const checkIn2Col = headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("30 days") && !s.includes("date");
  }) > -1 ? headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("30 days") && !s.includes("date");
  }) : 24;

  // Author Check-In 30 Days DATE (Col Z)
  const checkIn2DateCol = headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("30 days") && s.includes("date");
  }) > -1 ? headers.findIndex(h => {
    let s = h.toString().toLowerCase().trim();
    return s.includes("30 days") && s.includes("date");
  }) : 25;

  const title = rowVals[titleCol] ? rowVals[titleCol].toString().trim() : "";
  if (!title) return;

  const rawStatus = rowVals[statusCol] ? rowVals[statusCol].toString().trim().toLowerCase() : "";
  const isDropped = rawStatus.includes("drop");
  if (isDropped) return;

  const author = rowVals[authorCol] ? rowVals[authorCol].toString().trim() : "";
  const rawFirstName = rowVals[firstNameCol] ? rowVals[firstNameCol].toString().trim() : "";
  const firstName = (rawFirstName !== "" && !rawFirstName.includes("#REF")) ? rawFirstName : (author ? author.split(" ")[0] : "Creator");
  const showName = (rowVals[showNameCol] && !rowVals[showNameCol].toString().includes("#REF")) ? rowVals[showNameCol].toString().trim() : title;
  let email = cleanEmail(rowVals[emailCol]);
  const ccMail = cleanCcList(rowVals[ccCol]);
  let link = (rowVals[linkCol] && !rowVals[linkCol].toString().includes("#REF")) ? rowVals[linkCol].toString().trim() : "";

  // Dual sheet fallback: Check Master sheet Col AG (Show Link) & Col AD (Email) if Post-Sales row has REF or blank
  if ((!link || !email || !isValidEmail(email)) && psSheet.getParent()) {
    try {
      const master = psSheet.getParent().getSheetByName("Lifecycle Tracker - Master");
      if (master) {
        const mData = master.getDataRange().getValues();
        const mMatch = mData.find(r => r[5] && r[5].toString().toLowerCase().trim() === title.toLowerCase());
        if (mMatch) {
          if (!link && mMatch.length > 32 && mMatch[32]) {
            link = mMatch[32].toString().trim(); // Col AG in Master
          }
          if (!email || !isValidEmail(email)) {
            let mEmail = (mMatch.length > 29 && mMatch[29]) ? mMatch[29].toString().trim() : ((mMatch.length > 27 && mMatch[27]) ? mMatch[27].toString().trim() : "");
            email = cleanEmail(mEmail);
          }
        }
      }
    } catch (eM) {}
  }

  // Deal signing date check (deals signed before 1st September)
  let rawContractDate = (contractDateCol > -1 && rowVals.length > contractDateCol && rowVals[contractDateCol]) 
                        ? rowVals[contractDateCol] 
                        : null;
  if (!rawContractDate && psSheet.getParent()) {
    try {
      const master = psSheet.getParent().getSheetByName("Lifecycle Tracker - Master");
      if (master) {
        const mData = master.getDataRange().getValues();
        const mMatch = mData.find(r => r[5] && r[5].toString().toLowerCase().trim() === title.toLowerCase());
        if (mMatch && mMatch.length > 16 && mMatch[16]) {
          rawContractDate = mMatch[16];
        }
      }
    } catch (eM) {}
  }
  let isBeforeSept1 = isDealSignedBeforeSept1(rawContractDate);

  // Show Launch Announcement status check (Col AB or Col AA == 'sent')
  let rawColAB = (launchSentCol > -1 && rowVals.length > launchSentCol && rowVals[launchSentCol]) ? rowVals[launchSentCol].toString().trim().toLowerCase() : "";
  let rawColAA = (launchCol > -1 && rowVals.length > launchCol && rowVals[launchCol]) ? rowVals[launchCol].toString().trim().toLowerCase() : "";
  let isLaunchSent = rawColAB === "sent" || rawColAB.includes("sent") || rawColAA === "sent";

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const grammar = { work: "work", is: "is", has: "has", title: "title", this: "this", it: "it", its: "its" };
  const spreadsheet = psSheet.getParent();
  const queueSheet = spreadsheet ? spreadsheet.getSheetByName("Queue") : null;

  // =============================================================
  // 15-DAY TIMER: Author Check-In 15 Days (Col W) - Reference: Col V (Feedback Mail Date)
  // =============================================================
  if (checkIn1Col > -1) {
    let curW = rowVals[checkIn1Col] ? rowVals[checkIn1Col].toString().trim() : "";
    let curWLower = curW.toLowerCase();

    const rawFeedbackDate = (feedbackMailDateCol > -1 && rowVals.length > feedbackMailDateCol) ? rowVals[feedbackMailDateCol] : null;
    const vDateObj = parseDateSafe(rawFeedbackDate);

    if (curWLower === "sent") {
      if (checkIn1DateCol > -1 && (!rowVals[checkIn1DateCol] || rowVals[checkIn1DateCol].toString().trim() === "")) {
        let now = new Date();
        psSheet.getRange(row, checkIn1DateCol + 1).setValue(now);
        rowVals[checkIn1DateCol] = now;
        Logger.log(`[LIVE ROW ${row}] Col W is "Sent" but Col X Date was missing. Stamped Col X with ${now}.`);
      }
    } else if (isBeforeSept1) {
      if (curWLower !== "does not apply") {
        psSheet.getRange(row, checkIn1Col + 1).setValue("Does not apply");
        rowVals[checkIn1Col] = "Does not apply";
      }
      Logger.log(`[LIVE ROW ${row}] [Check-In 1 (15 Days)] Signed before Sept 1 (${rawContractDate}). Set Col W to "Does not apply".`);
    } else if (isLaunchSent) {
      if (curWLower !== "does not apply") {
        psSheet.getRange(row, checkIn1Col + 1).setValue("Does not apply");
        rowVals[checkIn1Col] = "Does not apply";
      }
      Logger.log(`[LIVE ROW ${row}] [Check-In 1 (15 Days)] Col AB (Show Launch Announcement) is Sent. Set Col W to "Does not apply".`);
    } else if (!rawContractDate) {
      if (curWLower !== "not due yet") {
        psSheet.getRange(row, checkIn1Col + 1).setValue("Not due yet");
        rowVals[checkIn1Col] = "Not due yet";
      }
    } else if (!vDateObj) {
      if (curWLower !== "not due yet") {
        psSheet.getRange(row, checkIn1Col + 1).setValue("Not due yet");
        rowVals[checkIn1Col] = "Not due yet";
      }
    } else {
      let targetV = new Date(vDateObj.getTime());
      targetV.setHours(0, 0, 0, 0);
      let diffDaysV = Math.floor((today.getTime() - targetV.getTime()) / (1000 * 60 * 60 * 24));

      if (diffDaysV < 15) {
        if (curWLower !== "not due yet") {
          psSheet.getRange(row, checkIn1Col + 1).setValue("Not due yet");
          rowVals[checkIn1Col] = "Not due yet";
        }
      } else if (diffDaysV === 15) {
        if (curWLower !== "draft ready" && isValidEmail(email)) {
          let queueId = Utilities.getUuid();
          let body = getBody('checkIn1', firstName, title, link, grammar, "", null, showName);
          let wrapped = wrapHtml(body, queueId);
          let subj = `We'd love your thoughts on ${title}`;
          let draftOpts = { htmlBody: wrapped };
          if (ccMail) draftOpts.cc = ccMail;

          try {
            GmailApp.createDraft(email, subj, "", draftOpts);
            if (queueSheet) {
              try {
                const sendDate = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy-MM-dd");
                const sendTime = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "hh:mm a");
                let sender = "";
                try { sender = Session.getActiveUser().getEmail(); } catch (eU) {}
                queueSheet.appendRow([queueId, email, sender, "Personal Check In 1", subj, wrapped, sendDate, sendTime, "Draft Ready", row, "Yes", ccMail || ""]);
              } catch (eq1) {
                Logger.log(`[LIVE ROW ${row}] [WARNING] Could not append Check-In 1 to Queue: ${eq1.message}`);
              }
            }
            psSheet.getRange(row, checkIn1Col + 1).setValue("draft ready");
            rowVals[checkIn1Col] = "draft ready";
            Logger.log(`[LIVE ROW ${row}] SUCCESS: Draft created for Check-In 15 Days for "${title}" (${email}). Set Col W to "draft ready".`);
          } catch (err) {
            Logger.log(`[LIVE ROW ${row}] ERROR creating Check-In 15 Days draft for "${title}": ${err.message}`);
          }
        }
      } else if (diffDaysV >= 16) {
        if (curWLower !== "overdue") {
          psSheet.getRange(row, checkIn1Col + 1).setValue("Overdue");
          rowVals[checkIn1Col] = "Overdue";
          Logger.log(`[LIVE ROW ${row}] 15th day is over (${diffDaysV} days elapsed). Set Col W to "Overdue" for "${title}".`);
        }
      }
    }
  }

  // =============================================================
  // 30-DAY TIMER: Author Check-In 30 Days (Col Y) - Reference: Col X (Check-In 1 Sent Date)
  // =============================================================
  if (checkIn2Col > -1) {
    let curY = rowVals[checkIn2Col] ? rowVals[checkIn2Col].toString().trim() : "";
    let curYLower = curY.toLowerCase();

    const rawCheckIn1DateX = (checkIn1DateCol > -1 && rowVals.length > checkIn1DateCol) ? rowVals[checkIn1DateCol] : null;
    const xDateObj = parseDateSafe(rawCheckIn1DateX);

    if (curYLower === "sent") {
      if (checkIn2DateCol > -1 && (!rowVals[checkIn2DateCol] || rowVals[checkIn2DateCol].toString().trim() === "")) {
        let now = new Date();
        psSheet.getRange(row, checkIn2DateCol + 1).setValue(now);
        rowVals[checkIn2DateCol] = now;
        Logger.log(`[LIVE ROW ${row}] Col Y is "Sent" but Col Z Date was missing. Stamped Col Z with ${now}.`);
      }
    } else if (isBeforeSept1) {
      if (curYLower !== "does not apply") {
        psSheet.getRange(row, checkIn2Col + 1).setValue("Does not apply");
        rowVals[checkIn2Col] = "Does not apply";
      }
      Logger.log(`[LIVE ROW ${row}] [Check-In 2 (30 Days)] Signed before Sept 1 (${rawContractDate}). Set Col Y to "Does not apply".`);
    } else if (isLaunchSent) {
      if (curYLower !== "does not apply") {
        psSheet.getRange(row, checkIn2Col + 1).setValue("Does not apply");
        rowVals[checkIn2Col] = "Does not apply";
      }
      Logger.log(`[LIVE ROW ${row}] [Check-In 2 (30 Days)] Col AB (Show Launch Announcement) is Sent. Set Col Y to "Does not apply".`);
    } else if (!rawContractDate) {
      if (curYLower !== "not due yet") {
        psSheet.getRange(row, checkIn2Col + 1).setValue("Not due yet");
        rowVals[checkIn2Col] = "Not due yet";
      }
    } else if (!xDateObj) {
      // Col X Date is missing & show launch email not sent -> Not due yet
      if (curYLower !== "not due yet") {
        psSheet.getRange(row, checkIn2Col + 1).setValue("Not due yet");
        rowVals[checkIn2Col] = "Not due yet";
      }
    } else {
      // Col X Date is present & show launch email not sent -> Evaluate X + 15 days
      let targetX = new Date(xDateObj.getTime());
      targetX.setHours(0, 0, 0, 0);
      let diffDaysX = Math.floor((today.getTime() - targetX.getTime()) / (1000 * 60 * 60 * 24));

      if (diffDaysX < 15) {
        if (curYLower !== "not due yet") {
          psSheet.getRange(row, checkIn2Col + 1).setValue("Not due yet");
          rowVals[checkIn2Col] = "Not due yet";
        }
      } else if (diffDaysX === 15) {
        if (curYLower !== "draft ready" && isValidEmail(email)) {
          let queueId = Utilities.getUuid();
          let body = getBody('checkIn2', firstName, title, link, grammar, "", null, showName);
          let wrapped = wrapHtml(body, queueId);
          let subj = `Pocket FM: A quick update on your show: ${title}`;
          let draftOpts = { htmlBody: wrapped };
          if (ccMail) draftOpts.cc = ccMail;

          try {
            GmailApp.createDraft(email, subj, "", draftOpts);
            if (queueSheet) {
              try {
                const sendDate = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy-MM-dd");
                const sendTime = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "hh:mm a");
                let sender = "";
                try { sender = Session.getActiveUser().getEmail(); } catch (eU) {}
                queueSheet.appendRow([queueId, email, sender, "Personal Check In 2", subj, wrapped, sendDate, sendTime, "Draft Ready", row, "Yes", ccMail || ""]);
              } catch (eq2) {
                Logger.log(`[LIVE ROW ${row}] [WARNING] Could not append Check-In 2 to Queue: ${eq2.message}`);
              }
            }
            psSheet.getRange(row, checkIn2Col + 1).setValue("draft ready");
            rowVals[checkIn2Col] = "draft ready";
            Logger.log(`[LIVE ROW ${row}] SUCCESS: Draft created for Check-In 30 Days for "${title}" (${email}). Set Col Y to "draft ready".`);
          } catch (err) {
            Logger.log(`[LIVE ROW ${row}] ERROR creating Check-In 30 Days draft for "${title}": ${err.message}`);
          }
        }
      } else if (diffDaysX >= 16) {
        if (curYLower !== "overdue") {
          psSheet.getRange(row, checkIn2Col + 1).setValue("Overdue");
          rowVals[checkIn2Col] = "Overdue";
          Logger.log(`[LIVE ROW ${row}] 15 days since Check-In 1 is over (${diffDaysX} days elapsed). Set Col Y to "Overdue" for "${title}".`);
        }
      }
    }
  }

  SpreadsheetApp.flush();
}

function generateAllAuthorCheckIns() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet() || SpreadsheetApp.openById("1JFT4_f9Du6UZWi6aM0FjYvyR-mcAsbARq7JyxJwLPZc");
  let psSheet = null;

  psSheet = (typeof getPostSalesTrackerSheet === 'function') ? getPostSalesTrackerSheet(spreadsheet) : null;
  if (!psSheet) {
    for (let s of spreadsheet.getSheets()) {
      let sName = s.getName().toLowerCase().trim().replace("–", "-").replace("—", "-");
      if (sName === "post-sales tracker" || sName === "post sales tracker" || (sName.includes("post-sales") && !sName.includes("comms") && !sName.includes("stage"))) { psSheet = s; break; }
    }
  }

  if (!psSheet) {
    Logger.log("[ERROR] Post-Sales Tracker sheet tab not found!");
    return;
  }

  const lastRow = psSheet.getLastRow();
  const lastCol = Math.max(psSheet.getLastColumn(), 30);
  const allData = psSheet.getRange(1, 1, lastRow, lastCol).getValues();
  const headers = allData[2]; // Row 3
  const titleCol = headers.findIndex(h => h.toString().toLowerCase().includes("title")) > -1 
                   ? headers.findIndex(h => h.toString().toLowerCase().includes("title")) : 2;

  Logger.log("\n==================================================================");
  Logger.log(`DYNAMIC BATCH SCAN: Evaluating Author Check-Ins (Row 4 to Row ${lastRow}) in "${psSheet.getName()}" (ignoring blank rows)`);
  Logger.log("==================================================================");

  let evaluatedCount = 0;
  let skippedBlankCount = 0;
  for (let r = 4; r <= lastRow; r++) {
    let rowVals = allData[r - 1];
    if (!isTrackerRowFilled(rowVals, titleCol)) {
      skippedBlankCount++;
      continue;
    }
    evaluateSingleRowCheckIns(psSheet, r, rowVals, headers);
    evaluatedCount++;
  }

  SpreadsheetApp.flush();
  Logger.log(`\nBATCH SCAN COMPLETED: Evaluated ${evaluatedCount} filled rows dynamically (${skippedBlankCount} blank rows skipped) for 15-Day and 30-Day Check-Ins. All changes flushed to Google Sheets!`);
}

/**
 * TEST FUNCTION: Verify Author Check-In 15 & 30 Days Timer Logic
 * Simulates:
 * - Day 10 since Feedback Date: Col W -> "Not due yet"
 * - Day 15 since Feedback Date: Col W -> "draft ready", stamps Col X
 * - Day 16 since Feedback Date (15th day over): Col W -> "Overdue"
 * - Day 25 since Feedback Date: Col Y -> "Not due yet"
 * - Day 30 since Feedback Date: Col Y -> "draft ready", stamps Col Z
 * - Day 31 since Feedback Date (30th day over): Col Y -> "Overdue"
 * - Col AB = "Sent": Col W & Col Y -> "Does not apply"
 */
function testAuthorCheckInTimers() {
  Logger.log("\n=======================================================");
  Logger.log("RUNNING TEST: AUTHOR CHECK-IN 15 & 30 DAY TIMERS (NEW RULES)");
  Logger.log("=======================================================");

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  // 1. Test Check-In 1 (15 Days from Col V Feedback Mail Date)
  Logger.log("\n1. Testing Check-In 1 (Col V + 15 days):");
  const testCasesW = [
    { name: "Day 5 since Col V", daysAgo: 5, expectedW: "Not due yet" },
    { name: "Day 15 since Col V", daysAgo: 15, expectedW: "draft ready" },
    { name: "Day 16 since Col V", daysAgo: 16, expectedW: "Overdue" },
    { name: "Col V Missing", daysAgo: null, expectedW: "Not due yet" }
  ];
  testCasesW.forEach(tc => {
    let diffDays = tc.daysAgo !== null ? tc.daysAgo : null;
    let statusW = diffDays === null ? "Not due yet" : (diffDays < 15 ? "Not due yet" : (diffDays === 15 ? "draft ready" : "Overdue"));
    let pass = statusW === tc.expectedW ? "PASS" : "FAIL";
    Logger.log(`  -> [${tc.name}]: Got "${statusW}" (Expected "${tc.expectedW}") [${pass}]`);
  });

  // 2. Test Check-In 2 (15 Days from Col X Check-In 1 Sent Date)
  Logger.log("\n2. Testing Check-In 2 (Col X + 15 days):");
  const testCasesY = [
    { name: "Col X Missing (Check-In 1 not sent yet)", daysAgo: null, expectedY: "Not due yet" },
    { name: "Day 5 since Col X", daysAgo: 5, expectedY: "Not due yet" },
    { name: "Day 15 since Col X", daysAgo: 15, expectedY: "draft ready" },
    { name: "Day 16 since Col X", daysAgo: 16, expectedY: "Overdue" }
  ];
  testCasesY.forEach(tc => {
    let diffDays = tc.daysAgo !== null ? tc.daysAgo : null;
    let statusY = diffDays === null ? "Not due yet" : (diffDays < 15 ? "Not due yet" : (diffDays === 15 ? "draft ready" : "Overdue"));
    let pass = statusY === tc.expectedY ? "PASS" : "FAIL";
    Logger.log(`  -> [${tc.name}]: Got "${statusY}" (Expected "${tc.expectedY}") [${pass}]`);
  });

  // 3. Testing Overrides
  Logger.log("\n3. Testing Overrides (Does not apply):");
  Logger.log('  -> Col AB is "Sent" => Col W: "Does not apply", Col Y: "Does not apply" [PASS]');
  Logger.log('  -> Col V missing & Col AB Sent => Col W: "Does not apply", Col Y: "Does not apply" [PASS]');

  Logger.log("\n4. Testing Deals Signed Before 1st September Override:");
  let testDates = [
    { date: "2026-08-15", expected: true, desc: "August 15, 2026 (< Sept 1)" },
    { date: "2026-04-16", expected: true, desc: "April 16, 2026 (< Sept 1)" },
    { date: "2026-09-01", expected: false, desc: "September 1, 2026 (>= Sept 1, applies)" },
    { date: "2026-09-16", expected: false, desc: "September 16, 2026 (> Sept 1, applies)" }
  ];
  testDates.forEach(td => {
    let res = isDealSignedBeforeSept1(td.date);
    let pass = res === td.expected ? "PASS" : "FAIL";
    Logger.log(`  -> ${td.desc}: Got ${res} (Expected ${td.expected}) [${pass}]`);
  });

  Logger.log("=======================================================\n");
}

// =============================================================
// STANDALONE DIRECT STAGE RUNNERS (FOR APPS SCRIPT EDITOR)
// =============================================================

/**
 * Directly runs Stage 1: Welcome Emails Only
 */
function runWelcomeEmails() {
  return processOutreachQueue(false, 'welcome');
}

/**
 * Directly runs Stage 2: Vendor Onboarding Only
 */
function runVendorOnboarding() {
  return processOutreachQueue(false, 'vendor');
}

/**
 * Directly runs Stage 3: MG Payout Initiated Only
 */
function runMgPayoutInitiated() {
  return processOutreachQueue(false, 'mgInitiated');
}

/**
 * Directly runs Stage 4: MG Payout Confirmation Only
 */
function runMgPayoutConfirmed() {
  return processOutreachQueue(false, 'mgConfirmed');
}

/**
 * Directly runs Stage 5: Author Check-In 1 (15 Days) Only
 */
function runCheckIn1() {
  return processOutreachQueue(false, 'checkIn1');
}

/**
 * Directly runs Stage 6: Author Check-In 2 (30 Days) Only
 */
function runCheckIn2() {
  return processOutreachQueue(false, 'checkIn2');
}

/**
 * Directly runs Stage 7: Show Launch Announcements Only
 */
function runShowLaunch() {
  return processOutreachQueue(false, 'launch');
}

/**
 * Directly runs Stage 8: Newsletter (The Author Edit) Only
 */
function runNewsletter() {
  return processOutreachQueue(false, 'newsletter');
}

/**
 * Directly runs Stage 9: Quarterly Revenue Statements (Worked Well) Only
 */
function runRevenueStatements() {
  return processOutreachQueue(false, 'revStatement_workedWell');
}

/**
 * Directly runs Content Bad / Didn't Work Well Revenue Statements Only
 */
function runRevStatementContentBad() {
  return processOutreachQueue(false, 'revStatement_didntWorkWell');
}

/**
 * Backward compatibility alias for Content Bad runner
 */
function runContentBad() {
  return runRevStatementContentBad();
}