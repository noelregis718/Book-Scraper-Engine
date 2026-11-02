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
  const url = `${CMS_SHOW_URL}${cleanId}`;

  const headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache"
  };

  if (token) {
    if (token.startsWith("Bearer ") || !token.includes("=")) {
      headers["Authorization"] = token.startsWith("Bearer ") ? token : `Bearer ${token}`;
    } else {
      headers["Cookie"] = token;
    }
  }

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

    if (code === 401 || code === 403 || content.toLowerCase().includes("login with jumpcloud")) {
      result.error = "Authentication required or session expired. Please update CMS Session Token.";
      return result;
    }

    if (code >= 400) {
      result.error = `HTTP Error ${code}`;
      return result;
    }

    // Attempt 1: Check for Next.js or React hydration data (__NEXT_DATA__ or state JSON)
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
          if (result.showName) {
            result.success = true;
            return result;
          }
        }
      } catch (jsonErr) {
        Logger.log(`JSON parse warning: ${jsonErr}`);
      }
    }

    // Attempt 2: HTML Regex Matching (Mirrors Playwright scraper DOM selectors)
    // 1. Show Name (h1, h2, or title class)
    const titleMatch = content.match(/<h[12][^>]*>([^<]+)<\/h[12]>/i) ||
                       content.match(/class="[^"]*sc-imWYAI[^"]*"[^>]*>([^<]+)<\/p>/i) ||
                       content.match(/<title>([^<]+)<\/title>/i);
    if (titleMatch && titleMatch[1]) {
      result.showName = titleMatch[1].replace(/\s*\|\s*Pocket\s*FM/i, "").trim();
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

    result.success = !!(result.showName || result.plays || result.duration);
    if (!result.success) {
      result.error = "Could not parse metrics from response. Check session token or CMS structure.";
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

    if (secret && secret !== expectedSecret) {
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
 * Handles incoming HTTP GET requests for health check & info
 * @param {Object} e 
 * @returns {GoogleAppsScript.Content.TextOutput}
 */
function doGet(e) {
  return ContentService.createTextOutput(JSON.stringify({
    service: "Pocket FM CMS Sync Webhook",
    status: "active",
    authConfigured: !!getCmsAuthToken(),
    timestamp: new Date().toISOString()
  })).setMimeType(ContentService.MimeType.JSON);
}
