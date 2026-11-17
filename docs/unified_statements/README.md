# Pocket FM — Confidential Partner Portal & Internal Management Hub

Welcome to the official documentation for the **Pocket FM Confidential Partner Portal & Internal Management Hub** website. This platform provides an enterprise-grade, confidential royalty accounting, statement generation, and partner distribution ecosystem for Pocket FM authors, rights holders, and executive licensing managers.

---

## 📑 Table of Contents

1. [Executive Summary & Architecture](#-executive-summary--architecture)
2. [Architecture & Route Endpoints](#-architecture--route-endpoints)
3. [Website Structure & Page Guide](#-website-structure--page-guide)
   - [1. Confidential Partner Portal Gateway (`index.html`)](#1-confidential-partner-portal-gateway-indexhtml)
   - [2. Internal Statement Management Hub (`internal_hub.html`)](#2-internal-statement-management-hub-internal_hubhtml)
   - [3. Dynamic Statement Viewer (`statement_viewer.html`)](#3-dynamic-statement-viewer-statement_viewerhtml)
   - [4. Pre-Rendered Standalone Statements (`statements/*.html`)](#4-pre-rendered-standalone-statements-statementshtml)
4. [Royalty & Recoupment Accounting Mathematics](#-royalty--recoupment-accounting-mathematics)
   - [Gross Deal Mechanics](#gross-deal-mechanics-24-series)
   - [Net Deal Mechanics](#net-deal-mechanics-9-series)
5. [UI Features & Component Guide](#-ui-features--component-guide)
   - [Modern Classic Custom Dropdowns](#modern-classic-custom-dropdowns)
   - [Hub Navigation Tabs](#hub-navigation-tabs)
   - [Interactive Deal Ledgers](#interactive-deal-ledgers)
   - [Add New Revenue Statement Modal](#add-new-revenue-statement-modal)
6. [Single-Page Print & PDF Export Engine](#-single-page-print--pdf-export-engine)
7. [Data Ingestion & Automated Generator Pipeline](#-data-ingestion--automated-generator-pipeline)
8. [Deployment & Hosting Infrastructure](#-deployment--hosting-infrastructure)
9. [Operations & Maintenance Playbook](#-operations--maintenance-playbook)
10. [Appendix: Legacy Scraping & Automation Suite](#-appendix-legacy-scraping--automation-suite)

---

## 🏛 Executive Summary & Architecture

The Pocket FM Revenue Statements web ecosystem bridges the gap between raw audited financial spreadsheets and polished, confidential, author-facing royalty statements. It operates with two interconnected layers:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                   POCKET FM REVENUE STATEMENTS PLATFORM                   │
└──────────────────────────────────────────────────────────────────────────┘
                                      │
         ┌────────────────────────────┴───────────────────────────┐
         ▼                                                        ▼
┌─────────────────────────────────┐              ┌─────────────────────────────────┐
│     EXTERNAL PARTNER LAYER      │              │      INTERNAL LICENSING HUB     │
├─────────────────────────────────┤              ├─────────────────────────────────┤
│ • Branded Partner Portal Entry  │              │ • 33 Series Interactive Grid    │
│ • Secure, Slug-Hashed Statements│              │ • Master Revenue Summary Matrix │
│ • Dynamic Query Param Viewer    │              │ • Gross & Net Financial Ledgers │
│ • 1-Page Exact Print / PDF      │              │ • Add New Statement Generator   │
└─────────────────────────────────┘              └─────────────────────────────────┘
         ▲                                                        ▲
         │                                                        │
         └────────────────────────────┬───────────────────────────┘
                                      │
                       ┌──────────────┴──────────────┐
                       │  PYTHON AUTOMATION BACKEND  │
                       ├─────────────────────────────┤
                       │ • Finance XLSX Ingestion    │
                       │ • Recoupment Calculations   │
                       │ • HTML Template Compilation │
                       │ • Live Vercel Deployments   │
                       └─────────────────────────────┘
```

### Key Technical Highlights
- **Zero-Dependency Frontend**: Pure HTML5, modern vanilla CSS3, and ES6+ JavaScript. No bloated frameworks or hydration delays; loads instantaneously worldwide over the Vercel Edge Network.
- **Audited Financial Precision**: Exact mathematical alignment with Pocket FM Finance sheets for Gross Deals and Net Deals, handling minimum guarantee (MG) recoupment, payment gateway deductions, and multi-period carryovers.
- **Uniform Executive Typography & Borders**: All statement tables feature crisp, uniform `1px solid #000000` borders, `#f0f0f0` executive header backgrounds, and direct exposed table layouts without distracting card borders.
- **Pixel-Perfect 1-Page PDF Engine**: Engineered with strict `@media print` rules, margin bounding, and `-webkit-print-color-adjust: exact` to produce a single-page PDF document when printing.

---

## 🌐 Architecture & Route Endpoints

The web application is structured around clean, extensionless routing served via local preview or private internal hosting:

| Route / View | Source File | Purpose | Access Audience |
| :--- | :--- | :--- | :--- |
| **`/` (Gateway)** | `docs/unified_statements/index.html` | Public confidential gate & partner help info | Authors, Public |
| **`/internal_hub`** | `docs/unified_statements/internal_hub.html` | Internal management hub, ledgers & creator tool | Licensing Team, Execs |
| **`/statement_viewer`** | `docs/unified_statements/statement_viewer.html` | Dynamic single-statement renderer & PDF exporter | Authors, Licensing Team |
| **`/statements/<slug>.html`** | `docs/unified_statements/statements/` | Standalone pre-rendered official statements | Contracted Partners |

> 🔒 **Access Notice**: Deployed production domains, cloud credentials, and author-specific URLs remain strictly private to Pocket FM internal infrastructure. For local development and verification, run a local web server (e.g., Python `http.server` or `npx serve`).

---

## 💻 Website Structure & Page Guide

The website root is located at `docs/unified_statements/`:

```text
docs/unified_statements/
├── index.html                    # Confidential Partner Portal Gateway
├── internal_hub.html             # Internal Management Hub & Financial Ledgers
├── statement_viewer.html         # Dynamic Query-Driven Statement Renderer
├── vercel.json                   # Vercel Clean URLs Configuration
├── favicon.svg                   # Vector Brand Favicon
├── favicon.png                   # 32x32 Raster Favicon
├── favicon-128.png               # 128x128 Apple Touch Icon
├── Pocket_FM_Revenue_Statement_Template_Gross.docx # Gross Deal Modern Word Template (.docx)
├── Pocket_FM_Revenue_Statement_Template_Gross.doc  # Gross Deal Legacy Word Template (.doc)
├── Pocket_FM_Revenue_Statement_Template_Net.docx   # Net Deal Modern Word Template (.docx)
├── Pocket_FM_Revenue_Statement_Template_Net.doc    # Net Deal Legacy Word Template (.doc)
├── Pocket_FM_Revenue_Statement_Template.doc        # Legacy Reference Template
└── statements/                   # 33 Pre-Rendered Standalone HTML Statements
```

### 1. Confidential Partner Portal Gateway (`index.html`)

- **Role**: The author-facing entry point.
- **Visual Design**: Dark-mode luxury minimalist palette (matte black `#111111`, slate card `#1e1e1e`, pure white typography).
- **Core Features**:
  - **Dynamic Series Lookup Modal**: Authors select their series from a dropdown to automatically redirect to their secure statement.
  - **Interactive FAQ Accordion**: Clarifies calculation mechanics, payment cycles (Net 60), tax withholding, and audit procedures.
  - **Direct Support Dispatch**: One-click licensing manager email dispatch.

### 2. Internal Statement Management Hub (`internal_hub.html`)

- **Role**: Executive mission control for licensing directors and partner managers.
- **Visual Design**: High-density executive command center.
- **Core Features**:
  - **Executive Stats Banner**: Real-time aggregation of Total Statements (33), Net Rev Distributed, Recouped MG, and Outstanding MG.
  - **Show Catalog Grid**: Searchable, filterable directory with live search filtering, Deal Type filter pills, and instant view links.
  - **Master Revenue Summary Ledger**: Comprehensive multi-column horizontal matrix exposing Q2 AMJ and Q3 JAS breakdowns side-by-side.
  - **Gross Deals Ledger & Net Deals Ledger**: Dedicated tabs isolating accounting formulas by contractual structure.
  - **Add New Revenue Statement Modal**: In-browser statement generator to add new titles directly to the hub.

### 3. Dynamic Statement Viewer (`statement_viewer.html`)

- **Role**: Universal parametric renderer for statements generated on-the-fly.
- **URL Syntax**: Accessible via query parameters: `statement_viewer.html?series=Title&deal=Gross&share=15%...`
- **Features**: Real-time URL query parameter parsing, dynamic ledger population, responsive print styles.

### 4. Pre-Rendered Standalone Statements (`statements/*.html`)

- **Directory**: `docs/unified_statements/statements/`
- **File Count**: 33 self-contained, independent HTML documents.
- **Naming Scheme**: Deterministic URL slugs with truncated 8-character cryptographic hashes for privacy and anti-enumeration:
  - Example: `blood-vice-504adcc0.html`
  - Example: `st-marins-cozy-mysteries-6a7e0a29.html`
- **Self-Contained**: Each file has embedded CSS, table data, and print stylesheets. They require zero JavaScript execution to view and can be emailed as standalone attachments or downloaded directly.

---

## 🧮 Royalty & Recoupment Accounting Mathematics

Pocket FM operates two distinct contractual deal models for licensed IP:

### Gross Deal Mechanics (24 Series)

Royalty is calculated directly from **Gross Net Collected Revenue** without deducting platform processing fees, hosting, or operational costs.

$$\text{Author Royalty Share} = \text{Gross Revenue} \times \text{Royalty Percentage}$$

$$\text{Payable Balance} = \max(0, \text{Cumulative Author Royalty} - \text{Total Advance / MG Paid})$$

### Net Deal Mechanics (9 Series)

Royalty is calculated on **Net Distributed Revenue** after deduction of standard platform store fees (e.g. 15% payment gateway/app store fees) and specific contracted marketing chargebacks.

$$\text{Net Revenue} = \text{Gross Revenue} - \text{Deductions} - \text{Contracted Marketing Spend}$$

$$\text{Author Royalty Share} = \text{Net Revenue} \times \text{Royalty Percentage}$$

$$\text{Payable Balance} = \max(0, \text{Cumulative Author Royalty} - \text{Total Advance / MG Paid})$$

---

## 🎨 UI Features & Component Guide

### Modern Classic Custom Dropdowns
Replaces clunky native browser `<select>` boxes with sleek, accessible custom dropdown components styled with dark slate menus, smooth hovers, and clean arrow indicators.

### Hub Navigation Tabs
The Internal Hub features persistent tabbed views:
1. **Series Catalog**: Grid card view of all 33 shows.
2. **Master Revenue Summary**: Full spreadsheet-style financial matrix.
3. **Gross Deals**: Filtered table showing gross deals and recoupment balances.
4. **Net Deals**: Filtered table displaying net deals and deduction lines.

### Interactive Deal Ledgers
Compact tables detailing deal terms, revenue shares, recoupment status, and remaining MG balances per series.

### Add New Revenue Statement Modal
An interactive form allowing licensing managers to draft and preview new partner statements directly within the hub.

---

## 🖨 Single-Page Print & PDF Export Engine

The statements feature an engineered single-page print stylesheet:
- **Zero Page Breaks**: Strict `page-break-inside: avoid` rules prevent tables from splitting across pages.
- **Exact Margins**: Configured with `@page { size: portrait; margin: 10mm 12mm; }`.
- **Exact Color Rendering**: Enforces `-webkit-print-color-adjust: exact` and `print-color-adjust: exact` so table header shading (`#f0f0f0`) renders crisply in PDF exports.

---

## ⚙️ Data Ingestion & Automated Generator Pipeline

```text
[Audited Finance XLSX]  ──>  [Python Generation Engine]
                                      │
         ┌────────────────────────────┴───────────────────────────┐
         ▼                                                        ▼
   33 HTML Files                                          internal_hub.html
   (in statements/)                                       (Embedded Master Ledger)
         │                                                        │
         └────────────────────────────┬───────────────────────────┘
                                      ▼
                           [ vercel deploy --prod ]
                                      │
                                      ▼
                         [Private Production Domain]
```

### Pipeline Script: `backend/generate_revenue_statements.py`
1. **`load_finance_jas_data()`**: Ingests rows from the audited `Rev Share Report` tab in `Rev Statement from Finance - JAS.xlsx`. Extracts gross revenue, marketing spend, deductions, MG paid, and listener analytics from `JAS All Shows Revenue Statement`.
2. **`load_amj_data()`**: Ingests verified Q2 AMJ statements for *The Witches of Cleopatra Hill* and *Blood Vice*.
3. **`generate_statement_html(show)`**: Injects audited financial values into the master HTML statement template, generating crisp tables, SVG badges, and print styles.
4. **`generate_internal_hub(shows)`**: Compiles `internal_hub.html` with:
   - Filterable cards for all 33 shows.
   - Comprehensive `Master Revenue Summary` horizontal matrix.
   - Separate `Gross Deals Ledger` and `Net Deals Ledger`.
5. **`deploy_to_vercel()`**: Invokes the Vercel CLI to deploy `docs/unified_statements` to the private production environment.

### One-Click Batch Automation
A Windows batch runner is provided at `backend/run_revenue_generator.bat`. Double-clicking or executing this file runs the entire ingestion, compilation, and private deployment pipeline automatically.

---

## 🚀 Deployment & Hosting Infrastructure

The application is hosted on **Vercel** with clean extensionless routing.

### Configuration (`vercel.json`)
```json
{
  "cleanUrls": true
}
```
Enables clean, extensionless routing (`/internal_hub` resolves to `/internal_hub.html`, `/statement_viewer` resolves to `/statement_viewer.html`).

### Manual CLI Deployment
To deploy updates manually from terminal:
```powershell
# Navigate to the website root directory
cd docs/unified_statements

# Deploy directly to private Vercel production
vercel deploy --prod --yes
```

---

## 📖 Operations & Maintenance Playbook

### 1. Generating a PDF for an Author
1. Open the author's statement file (e.g. `/statements/<series-slug-hash>.html` or locally in `docs/unified_statements/statements/<series-slug-hash>.html`).
2. Click the floating red **"Download Statement (PDF)"** button in the bottom right corner (or press `Ctrl + P` / `Cmd + P`).
3. In the Chrome/Edge Print Dialog:
   - **Destination**: *Save as PDF*.
   - **Pages**: *All* (will automatically format as 1 page).
   - **Layout**: *Portrait*.
   - **Options**: Ensure **Background graphics** is checked.
4. Click **Save**.

### 2. Adding a New Deal via the Hub
1. Navigate to `/internal_hub` on your local server or internal deployment.
2. Click **`+ Add New Revenue Statement`**.
3. Select the Deal Type (**Gross Deal** or **Net Deal**).
4. Enter the Series Title, Author Name, Currency, and Reporting Period.
5. Fill in the financial fields; verify that the 4 summary tiles reflect the intended recoupment numbers.
6. Click **Save Statement & View Card**. The card will appear immediately in the **Other / Dynamic Series** section.

### 3. Adding New Official Shows to the Pipeline
When a new quarter's financial report is released:
1. Place the new audited Excel file in the project root (or update `Rev Statement from Finance - JAS.xlsx`).
2. Run the automation batch runner:
   ```cmd
   backend\run_revenue_generator.bat
   ```
3. The script will rebuild all 33+ static statements, update `internal_hub.html`, and deploy updates.

---

## 🗄 Appendix: Legacy Scraping & Automation Suite

For reference, the PocketFM repository also houses an industrial-grade intelligence and CRM automation suite:
- **Agency Catalog Scraper** (`backend/agency_mission_control.py`): Multi-tier Playwright scraper for Amazon and Goodreads metadata.
- **Google Drive Bulk Injection** (`backend/upload_and_link.py`): Headless bulk document uploader mapping shareable Drive links to CRM Excel trackers.
- **CRM Lifecycle Email Drafter** (`docs/apps_script_drafter.js`): Google Apps Script automation engine creating branded outreach drafts in Gmail for author lifecycle events (Welcome, Vendor Onboarding, MG Confirmed, Check-ins, Show Launch).

---

*Documentation maintained by the Pocket FM Licensing & Engineering Team.*  
*Confidential — For Internal Partner Operations & Royalty Settlement.*
