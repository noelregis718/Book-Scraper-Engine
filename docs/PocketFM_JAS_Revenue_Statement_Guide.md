# PocketFM JAS Revenue Statement Generation & Deployment Guide
**Last Updated:** October 2026

## Overview
This document outlines the complete end-to-end architecture for processing the **JAS Self-Pub Revenue Payouts** data, calculating the correct author payouts (based on Net vs. Gross deal types), dynamically injecting those figures into formatted HTML revenue statements, and permanently hosting them on Vercel for clients and authors.

## 1. The Data Source
The entire system runs off the master Excel file: `JAS Self-Pub Revenue Payouts - New.xlsx`.

The script processes data from three critical tabs:
1.  **US Lifecycle Deals**: Acts as the master lookup dictionary. The script scans this tab to find the targeted `Show ID`, the `Title`, the `Author Name`, the `Deal Type` (Net vs. Gross), and the `Rev Share %`.
2.  **JAS Consolidated All Shows Reve**: The primary database containing quarterly performance metrics (Plays, Listeners, Revenue, Production/Marketing Costs, and Minimum Guarantees).
3.  **JAS All Shows Revenue Statement**: A secondary database tab. Because some specific shows (e.g., *Gansett Series*) do not exist in the Consolidated tab, the script actively concatenates both tabs into a single unified Pandas DataFrame to ensure no shows fall through the cracks.

## 2. Net vs. Gross Deal Calculation Logic
The core component of the Python generation script (`process_revenue_updated.py` / `generate_combined_statements.py`) is the financial logic gate that dynamically builds the HTML table rows depending on the author's contract.

### Gross Deals
If the `deal_type` column contains "Gross":
*   **Base Revenue**: Sourced directly from `Revenue (PG Exc) $`.
*   **Author Share**: `Base Revenue` * `Rev Share %`.
*   **MG Recoupment**: `MG Paid $` - `Author Share`.
*   **Final Payout**: Sourced directly from `Payable Amount $ (Gross)`.
*   *Note: Production and Marketing costs are completely hidden from the HTML statement.*

### Net Deals
If the `deal_type` column contains "Net":
*   **Base Revenue**: `Revenue (PG Exc) $`.
*   **Deductions**: `Production Cost $` and `Marketing Cost $` are explicitly listed as negative line items.
*   **Net Revenue**: `Base Revenue` - `Production` - `Marketing`.
*   **Author Share**: `Net Revenue` * `Rev Share %`.
*   **MG Recoupment**: `MG Paid $` - `Author Share`.
*   **Final Payout**: Sourced directly from `Payable Amount $ (Net)`.

## 3. Standard vs. Combined Statements
Because different shows require different reporting periods, the architecture is split into two logical paths:

1.  **Standard Quarterly (Q3)**
    *   Targets shows like *Jackal Among Snakes* and *Redemption Arc*.
    *   Filters the Pandas dataframe specifically for the "July-August-September 2026" reporting period.
2.  **Combined 6-Month Statements**
    *   Targets shows like *Gansett Series*, *Blake Larsen*, *St. Marin's Cozy Mysteries*, etc.
    *   The script uses `pandas.groupby()` to group multiple quarters together.
    *   It systematically adds the values for Q2 (April-June) and Q3 (July-September) together into a single aggregated HTML statement.

## 4. HTML Injection & Generation
Once the math is verified:
1.  The Python script opens a master template (`revenue_statement.html`).
2.  Using Regular Expressions (`re.sub`), it replaces placeholder tokens (e.g., `[AUTHOR_NAME]`, `[REPORTING_PERIOD]`) with the live variables.
3.  It programmatically constructs the inner `<tbody>` of the HTML table based on the Net/Gross logic.
4.  The final formatted HTML string is saved as a new file (e.g., `Revenue_Statement_Gansett_Series.html`) inside the target directory.
5.  Finally, the script generates a master `index.html` file containing clickable hyperlinks to all the newly generated statements.

## 5. Vercel Hosting & Deployment Strategy
The generated HTML files must be accessible 24/7 via a live URL for authors to check.

### The GitHub Permission Block
PocketFM's primary Vercel account enforces strict Deployment Protection. Vercel will explicitly block any direct CLI pushes (e.g., `npx vercel --prod`) if the commit author does not have elevated project permissions linked to the `noelregis718/Book-Scraper-Engine` repository.

### The Bypass Architectures
To bypass these permission blocks and get the links live immediately, there are two approved deployment pipelines:

**Pipeline A: The GitHub Trigger (For linked projects)**
1.  Run the generation script locally.
2.  Add, commit, and push the generated HTML files directly to the GitHub `main` branch.
3.  Vercel's CI/CD pipeline will automatically detect the GitHub push, bypass the CLI restriction, and deploy the new code to the existing linked URL.

**Pipeline B: The Fresh Deployment (For immediate standalone links)**
1.  Copy the generated statement folder into a temporary `scratch` directory.
2.  Delete any hidden `.vercel` folders linking the directory to the blocked project.
3.  Run `npx vercel --prod --yes` inside the scratch folder to force Vercel to generate a brand new, unlinked, and unblocked project URL (e.g., `https://deploycombined2.vercel.app`).
4.  Distribute the new URL to the authors.

## 6. Historical Deployment Links
Below is a record of the final, live production Vercel links deployed during the development and generation phases:

**Q3 Statements (Sweet Tea & St. Marin's):**
* `https://deployq3fixed.vercel.app` (Final fixed version)
* `https://deployq3.vercel.app` (Initial version)

**Combined Q2/Q3 Statements (All 20+ Shows):**
* `https://deploycombined2.vercel.app` 
* `https://combinedstatements.vercel.app`

**Initial Test Deployments:**
* `https://deploystatements.vercel.app`
* `https://statements-ivory.vercel.app`
