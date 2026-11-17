# Pocket FM Content Intelligence & Licensing Automation Suite

An end-to-end operational suite combining large-scale catalog intelligence, CMS synchronization, author lifecycle email automation, and royalty statement generation.

---

## 🚀 Key Modules & Capabilities

### 1. Catalog Intelligence & Web Scraping
- **Multi-Source Scraping**: High-concurrency Playwright and Python pipelines for extracting book metadata, ranks, and reviews from Amazon Bestsellers and Goodreads.
- **Genre & Catalog Classification**: Automated tagging and enrichment (e.g., Romance, Fantasy, Thriller) to evaluate title performance and market trends.
- **Data Standardization**: Automated cleaning, deduplication, and structured Excel/JSON exports.

### 2. CMS Automation & Content Pipeline
- **CMS Synchronization**: Automated workflows connecting scraped catalog intelligence to the Pocket FM CMS.
- **Asset & Metadata Management**: Tracking show IDs, original manuscripts, launch readiness, and episode metadata.
- **Data Validation**: Automated discrepancy checks between partner trackers and production CMS records.

### 3. CRM Lifecycle Email Automation (Google Apps Script)
- **Modular 5-Part Engine**: Built in Google Apps Script (`Config`, `Templates`, `DraftEngine`, `StageHandlers`, `Main`) running directly in Google Sheets.
- **Automated Milestone Drafts**: Dynamically generates branded HTML email drafts for key author milestones:
  - Welcome & Vendor Onboarding
  - Advance / Minimum Guarantee (MG) Payouts & Confirmations
  - 15-Day and 30-Day Creative Check-Ins
  - Show Launch Announcements & Author Newsletters
  - Quarterly Revenue & Performance Updates
- **Two-Way Gmail Sync**: Automatically detects sent emails in Gmail and updates status tracking and dispatch dates in Google Sheets.

### 4. Revenue Statements & Financial Reporting
- **Audited Financial Processing**: Ingestion engine that computes multi-period earnings across Gross and Net revenue share models with MG recoupment tracking.
- **Interactive Management Hub**: Centralized view for filtering titles, tracking recoupment balances, and monitoring performance across quarters.
- **Pixel-Perfect Statements**: Clean, single-page printable and PDF-exportable statements for author partners.

### 5. Web Dashboards & Frontend Tools
- **Modern Web Interface**: Lightweight, responsive web apps for searching titles, previewing statements, and inspecting catalog metrics.

---

## 🛠 Tech Stack

- **Backend & Scraping**: Python 3.12, Playwright, BeautifulSoup, Pandas, OpenPyXL
- **Automation & Integrations**: Google Apps Script (ES6+), Gmail API, Google Sheets API, Google Drive API
- **Web & Portals**: HTML5, Vanilla CSS3 / Tailwind CSS, Modern JavaScript, Vite, React
- **Hosting & Tooling**: Vercel Edge Hosting, GitHub Actions

---

## 📁 Repository Overview

```text
├── apps_script/          # Google Apps Script modular CRM automation files
├── backend/              # Python scrapers, data pipelines, and statement generators
├── docs/                 # Workflow guides, templates, and setup documentation
└── frontend/             # Web dashboard and UI applications
```
