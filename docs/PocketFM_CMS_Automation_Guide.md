# PocketFM CMS Scraping & Automation Pipeline
**Last Updated:** October 2026

## Overview
This document outlines the architecture, setup, and usage of the automated **Playwright + BeautifulSoup** scraper designed to extract internal show metrics directly from the proprietary PocketFM CMS and sync them directly into the Operations Lifecycle Excel Tracker.

## 1. Technical Stack & Tools
The pipeline utilizes a hybrid approach of browser automation and static DOM parsing to balance login security with extraction reliability:
*   **Playwright (`playwright.sync_api`)**: Handles the Chromium browser launch, automates the complex JumpCloud Single Sign-On (SSO) login flow, and executes Javascript to render the React-based CMS dashboard.
*   **BeautifulSoup (`bs4`)**: Once the dynamic React dashboard is rendered, Playwright dumps the static HTML. BeautifulSoup is used to parse the DOM using structural CSS locators. This prevents the scraper from breaking if minor frontend CSS classes change or animations delay Playwright assertions.
*   **Pandas (`pandas`)**: Reads the target Excel file, iterates over the rows to fetch `Show ID`s, updates the in-memory dataframe, and flushes the data back to the disk.
*   **Dotenv (`python-dotenv`)**: Securely loads environment variables to prevent hardcoding company credentials.

## 2. Security & Session Management
Because the CMS requires authenticated access via a proprietary JumpCloud SSO gateway, strict security boundaries are enforced:

### The `.env` File
User credentials must never be committed to source control (GitHub). They are stored locally in the root workspace inside a `.env` file:
```env
CMS_EMAIL=ext-noel.regis@pocketfm.com
CMS_PASSWORD=******
```
*Note: The `.env` file is explicitly listed in `.gitignore`.*

### `auth.json` (Session Persistence)
To prevent the script from triggering anti-bot mechanisms or requiring the user to wait through the 15-second SSO jump every single run, Playwright saves the authenticated browser context to `scratch/auth.json`. 
When the script runs, it checks for `auth.json`. If valid cookies are found, it instantly bypasses the login screen and proceeds directly to the data scraping loop.

## 3. The Target Data Source
*   **Excel File**: `Internal Copy of US_Licensing_Lifecycle_Tracker  (1).xlsx`
*   **Sheet Name**: `Argus Show data`
*   **Primary Key**: The script reads the `Show ID` column, skipping blank rows or `NaN` values.
*   **Generated URL Structure**: `https://cms.pocketfm.com/shows/audiobooks?tab=published&id={show_id}`

## 4. Extraction Logic & Selectors
The PocketFM React dashboard utilizes hashed CSS classes (e.g., `sc-fmNzgT`). Since these hashes can theoretically change in future builds, the BeautifulSoup logic relies on robust relational parsing:
1.  **Locate Label**: Searches the DOM for specific label strings (e.g., "Plays", "Hours", "Reviews").
2.  **Verify Parent Class**: Verifies that the matched string sits inside a known dashboard label container (e.g., `sc-fmNzgT`).
3.  **Extract Sibling Value**: Navigates to the parent container and extracts the exact string value from the adjacent numerical `div`.

**Extracted Fields:**
*   `Show Name`: Extracted from the primary title header (`<p class="sc-imWYAI">`).
*   `Plays `: Number of listens/plays.
*   `Durations`: Show length in hours.
*   `Ratings`: Average star rating.
*   `Reviews`: Total number of reviews.
*   `Comments`: Total number of comments.

## 5. Execution Workflow

### Initial Setup
Ensure all required Python libraries and the Chromium browser binaries are installed:
```bash
pip install playwright pandas openpyxl python-dotenv beautifulsoup4
python -m playwright install chromium
```

### Running the Scraper
To launch the automated syncing process, execute the main script from the terminal:
```bash
python cms_scraper_final.py
```

### User Interaction (First Run / Expired Session)
If `auth.json` is missing or the login session has expired:
1.  Playwright will launch a visible Chromium window.
2.  It will automatically click the "JumpCloud" login button.
3.  It will read the `.env` file and type the email and password.
4.  The script will **PAUSE**.
5.  The user must manually check the browser, input their Multi-Factor Authentication (MFA) / Auth Code, and wait for the CMS dashboard to render completely.
6.  The user then presses **ENTER** in the terminal to resume the script.

### The Automated Loop
Once authenticated, the script runs autonomously:
1.  Iterates through every `Show ID` in the Excel file.
2.  Navigates to the specific URL.
3.  Waits for the "Plays" and "Reviews" components to mount on the React DOM.
4.  Extracts the 6 required metrics.
5.  Writes the metrics directly into the Pandas DataFrame.
6.  Upon finishing the loop, overrides the `.xlsx` file with the completed data.
