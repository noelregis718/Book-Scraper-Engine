/**
 * =======================================================================
 * POCKET FM CMS SCRAPER & DATA MANAGER - MODULE 2: CMS SERVICE
 * File: CmsService.gs (or CmsService.js)
 * =======================================================================
 * Handles:
 * - Direct HTTP calls to Pocket FM CMS via UrlFetchApp
 * - Response parsing (HTML DOM regex and Next.js / JSON state extraction)
 * - Built-in Webhook Receiver (doPost / doGet) for external push sync
 */

/**
 * Fetches show metrics directly from Pocket FM CMS using UrlFetchApp
 * @param {string} showId - 40-character hex Show ID
 * @returns {Object} Extracted metrics object { showId, showName, plays, duration, ratings, reviews, comments, listeningHours, success, error }
 */
function fetchShowMetricsFromCms(showId) {
  const result = {
    showId: showId,
    showName: "",
    plays: 0,
    duration: 0,
    ratings: 0,
    reviews: 0,
    comments: 0,
    listeningHours: 0,
    success: false,
    error: ""
  };

  const cleanId = extractShowId(showId);
  if (!cleanId) {
    result.error = "Invalid Show ID format";
    return result;
  }

  const token = getCmsAuthToken();
  if (!token) {
    result.error = "No active CMS session token configured. Please click 'Paste / Update Session Token' in the scraper dialog to authenticate.";
    return result;
  }

  const url = `${CMS_SHOW_URL}${cleanId}`;

  const headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache"
  };

  if (token.startsWith("Bearer ") || !token.includes("=")) {
    headers["Authorization"] = token.startsWith("Bearer ") ? token : `Bearer ${token}`;
  } else {
    headers["Cookie"] = token;
  }

  // Attempt 1: Query Pocket FM CMS backend API directly (fast JSON)
  try {
    const apiHeaders = Object.assign({}, headers, {
      "Accept": "application/json, text/plain, */*",
      "Origin": CMS_BASE_URL,
      "Referer": url
    });

    const apiEndpoint = `https://api.cms.pocketfm.com/content_api/book.published_shows?show_id=${cleanId}`;
    const apiResp = UrlFetchApp.fetch(apiEndpoint, {
      method: "get",
      headers: apiHeaders,
      followRedirects: true,
      muteHttpExceptions: true
    });

    if (apiResp.getResponseCode() === 200) {
      const apiJson = JSON.parse(apiResp.getContentText());
      const showObj = (apiJson.result && (apiJson.result.books ? apiJson.result.books[0] : apiJson.result)) || apiJson.data;
      if (showObj && (showObj.title || showObj.name || showObj.show_name)) {
        result.showName = (showObj.title || showObj.name || showObj.show_name).replace(/\s*\|\s*Pocket\s*FM/i, "").trim();
        if (showObj.plays !== undefined || showObj.play_count !== undefined) result.plays = cleanCmsMetric(showObj.plays || showObj.play_count);
        if (showObj.duration !== undefined || showObj.hours !== undefined) result.duration = cleanCmsMetric(showObj.duration || showObj.hours);
        if (showObj.ratings !== undefined || showObj.rating !== undefined) result.ratings = cleanCmsMetric(showObj.ratings || showObj.rating);
        if (showObj.reviews !== undefined || showObj.review_count !== undefined) result.reviews = cleanCmsMetric(showObj.reviews || showObj.review_count);
        if (showObj.comments !== undefined || showObj.comment_count !== undefined) result.comments = cleanCmsMetric(showObj.comments || showObj.comment_count);
        result.listeningHours = result.duration;
        result.success = true;
        return result;
      }
    }
  } catch (apiErr) {
    Logger.log("API check info: " + apiErr);
  }

  // Attempt 2: HTML Page Request
  const options = {
    method: "get",
    headers: headers,
    followRedirects: true,
    muteHttpExceptions: true
  };

  try {
    const response = UrlFetchApp.fetch(url, options);
    const code = response.getResponseCode();
    const content = response.getContentText();
    const lower = content.toLowerCase();

    if (code === 401 || code === 403 || lower.includes("jumpcloud") || lower.includes("please login") || lower.includes("sign in to your account")) {
      result.error = "Authentication failed or session expired. Please refresh your CMS login in the browser and update the Session Token.";
      return result;
    }

    if (code >= 400) {
      result.error = `HTTP Error ${code}`;
      return result;
    }

    // Attempt 3: Check for Next.js or React hydration data (__NEXT_DATA__ or state JSON)
    const jsonMatch = content.match(/<script id="__NEXT_DATA__" type="application\/json">([\s\S]*?)<\/script>/i);
    if (jsonMatch && jsonMatch[1]) {
      try {
        const nextData = JSON.parse(jsonMatch[1]);
        const pageProps = nextData.props && nextData.props.pageProps;
        if (pageProps) {
          const showData = pageProps.show || pageProps.data || pageProps;
          if (showData.title || showData.name) {
            result.showName = showData.title || showData.name;
          }
          if (showData.plays !== undefined) result.plays = cleanCmsMetric(showData.plays);
          if (showData.duration !== undefined) result.duration = cleanCmsMetric(showData.duration);
          if (showData.ratings !== undefined) result.ratings = cleanCmsMetric(showData.ratings);
          if (showData.reviews !== undefined) result.reviews = cleanCmsMetric(showData.reviews);
          if (showData.comments !== undefined) result.comments = cleanCmsMetric(showData.comments);
          if (result.showName && !/^(CMS|CMS@PocketFM|Pocket\s*FM)$/i.test(result.showName)) {
            result.success = true;
            return result;
          }
        }
      } catch (jsonErr) {
        Logger.log(`JSON parse warning: ${jsonErr}`);
      }
    }

    // Attempt 4: HTML DOM Regex Matching (Mirrors Playwright scraper DOM selectors)
    // 1. Show Name (Strict: reject generic site title CMS@PocketFM)
    const titleMatch = content.match(/class="[^"]*sc-imWYAI[^"]*"[^>]*>([^<]+)<\/p>/i) ||
                       content.match(/<h[12][^>]*class="[^"]*title[^"]*"[^>]*>([^<]+)<\/h[12]>/i);
    if (titleMatch && titleMatch[1]) {
      const candidate = titleMatch[1].replace(/\s*\|\s*Pocket\s*FM/i, "").trim();
      if (!/^(CMS|CMS@PocketFM|Pocket\s*FM|Login|JumpCloud|Sign\s*In)$/i.test(candidate)) {
        result.showName = candidate;
      }
    }

    // 2. Plays
    const playsMatch = content.match(/([0-9.,KMBkmb]+)\s*<\/div>[^<]*<div[^>]*>\s*Plays\s*<\/div>/i) ||
                       content.match(/Plays<\/div>[^<]*<div[^>]*>([0-9.,KMBkmb]+)/i) ||
                       content.match(/([0-9.,]+)\s*Plays/i);
    if (playsMatch && playsMatch[1]) {
      result.plays = cleanCmsMetric(playsMatch[1]);
    }

    // 3. Duration / Hours
    const durMatch = content.match(/([0-9.,]+)\s*<\/div>[^<]*<div[^>]*>\s*Hours\s*<\/div>/i) ||
                     content.match(/Hours<\/div>[^<]*<div[^>]*>([0-9.,]+)/i) ||
                     content.match(/([0-9.,]+)\s*Hours/i);
    if (durMatch && durMatch[1]) {
      result.duration = cleanCmsMetric(durMatch[1]);
      result.listeningHours = cleanCmsMetric(durMatch[1]);
    }

    // 4. Comments
    const commentMatch = content.match(/([0-9.,KMBkmb]+)\s*<\/div>[^<]*<div[^>]*>\s*Comments\s*<\/div>/i) ||
                         content.match(/Comments<\/div>[^<]*<div[^>]*>([0-9.,KMBkmb]+)/i) ||
                         content.match(/([0-9.,]+)\s*Comments/i);
    if (commentMatch && commentMatch[1]) {
      result.comments = cleanCmsMetric(commentMatch[1]);
    }

    // 5. Ratings & Reviews
    const revMatch = content.match(/([0-9.,]+)\s*Reviews/i) ||
                     content.match(/([0-9.,]+)\s*Ratings/i);
    if (revMatch && revMatch[1]) {
      result.reviews = cleanCmsMetric(revMatch[1]);
      result.ratings = cleanCmsMetric(revMatch[1]);
    }

    result.success = !!(result.showName && (result.plays > 0 || result.duration > 0 || result.comments > 0 || result.ratings > 0 || result.reviews > 0));
    if (!result.success) {
      if (content.includes('id="root"') && !content.includes("sc-imWYAI")) {
        result.error = "CMS page rendered empty client shell (SPA). Session token may be missing or expired.";
      } else {
        result.error = result.showName ? "Show name found but metrics could not be parsed." : "Could not find show details. Verify Show ID and session authentication.";
      }
    }

  } catch (err) {
    result.error = err.toString();
  }

  return result;
}

/**
 * =======================================================================
 * WEBHOOK RECEIVER: doPost & doGet
 * =======================================================================
 * Allows external scrapers (e.g. Python Playwright or GitHub Actions) to
 * securely push scraped metrics straight into the Google Sheet.
 */

/**
 * Handles incoming HTTP POST requests with JSON payload
 * @param {Object} e - Event object containing postData
 * @returns {GoogleAppsScript.Content.TextOutput} JSON response
 */
function doPost(e) {
  try {
    if (!e || !e.postData || !e.postData.contents) {
      return ContentService.createTextOutput(JSON.stringify({
        status: "error",
        message: "Empty payload received"
      })).setMimeType(ContentService.MimeType.JSON);
    }

    const payload = JSON.parse(e.postData.contents);
    const secret = payload.secret || payload.token || "";
    const expectedSecret = getWebhookSecret();

    if (secret && secret !== expectedSecret && secret !== DEFAULT_WEBHOOK_SECRET) {
      return ContentService.createTextOutput(JSON.stringify({
        status: "unauthorized",
        message: "Invalid secret key"
      })).setMimeType(ContentService.MimeType.JSON);
    }

    const sheet = getOrCreateCmsSheet();
    let updatedCount = 0;

    // Case 1: Bulk array of shows
    if (Array.isArray(payload.shows)) {
      payload.shows.forEach(show => {
        if (updateOrAppendCmsShow(sheet, show)) {
          updatedCount++;
        }
      });
    } 
    // Case 2: Single show object
    else if (payload.showId) {
      if (updateOrAppendCmsShow(sheet, payload)) {
        updatedCount++;
      }
    }

    return ContentService.createTextOutput(JSON.stringify({
      status: "success",
      updatedShows: updatedCount,
      timestamp: new Date().toISOString()
    })).setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({
      status: "error",
      message: err.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * =======================================================================
 * CLIENT DIALOG AJAX HANDLERS
 * =======================================================================
 * Powers the interactive popup dialog in Google Sheets & Web App
 */

/**
 * Returns initialization data for the interactive scraper dialog
 * @returns {Object} { spreadsheetId, sheetName, totalShows, shows, hasToken }
 */
function getCmsInitData() {
  const ss = getCmsSpreadsheet();
  const sheet = getOrCreateCmsSheet(ss);
  const colMap = resolveCmsHeaderMap(sheet);
  const lastRow = sheet.getLastRow();
  const shows = [];

  if (lastRow > 1) {
    const vals = sheet.getRange(2, colMap.showId, lastRow - 1, 1).getValues();
    vals.forEach((r, idx) => {
      const id = extractShowId(r[0]);
      if (id) shows.push({ rowIdx: idx + 2, showId: id });
    });
  }

  return {
    spreadsheetId: SPREADSHEET_ID,
    sheetName: sheet.getName(),
    totalShows: shows.length,
    shows: shows,
    hasToken: !!getCmsAuthToken()
  };
}

/**
 * Scrapes a single show and immediately writes the row to Google Sheet
 * @param {string} showId 
 * @returns {Object} Scraped show metrics object
 */
function scrapeSingleShowAjax(showId) {
  const ss = getCmsSpreadsheet();
  const sheet = getOrCreateCmsSheet(ss);
  const metrics = fetchShowMetricsFromCms(showId);

  if (metrics.success) {
    updateOrAppendCmsShow(sheet, metrics);
  }

  return metrics;
}

/**
 * Saves CMS session token from interactive dialog
 * @param {string} token 
 * @returns {boolean} True if successfully stored
 */
function saveCmsTokenAjax(token) {
  setCmsAuthToken(token);
  return !!token;
}

/**
 * Handles incoming HTTP GET requests: serves interactive Web App UI or health JSON
 * @param {Object} e 
 * @returns {GoogleAppsScript.HTML.HtmlOutput|GoogleAppsScript.Content.TextOutput}
 */
function doGet(e) {
  if (e && e.parameter && (e.parameter.action === "getShows" || e.parameter.format === "json")) {
    const initData = getCmsInitData();
    return ContentService.createTextOutput(JSON.stringify(initData))
      .setMimeType(ContentService.MimeType.JSON);
  }

  return HtmlService.createHtmlOutput(buildCmsScraperDialogHtml())
    .setTitle("Pocket FM CMS Live Scraper")
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}
