# Pocket FM Revenue Statements Internal Hub — Design System & Structural Specifications

> **STATUS**: LOCKED REFERENCE ARCHITECTURE  
> **TARGET ASSETS**: `backend/generate_revenue_statements.py` & `docs/unified_statements/internal_hub.html`  
> **LIVE PRODUCTION DOMAIN**: `https://pocketfm-statements.vercel.app/internal_hub`

---

## 1. Executive Summary & Core Mandate

This document serves as the immutable architectural blueprint and strict guardrail specification for the **Pocket FM Internal Revenue Statement Hub**. 

Any future modifications, additions of quarterly statements, or feature updates **must adhere strictly to the rules, layout hierarchies, CSS classes, and DOM structures detailed below**. Under no circumstances should unauthorized wrapper boxes, inconsistent button colors, obsolete disclaimers, or layout reshuffling be introduced.

---

## 2. Top Toolbar Architecture (`.toolbar`)

The toolbar on the Statement Cards tab is structured into exactly **two distinct rows**:

```
+---------------------------------------------------------------------------------------------------+
|  [🔍 Search show title or author...]           [All Periods ▾]              [All Deals ▾]         |  <-- Line 1: .toolbar-search-row
+---------------------------------------------------------------------------------------------------+
|  [Export CSV]   [Sync from Google Sheets]   [Download Word Template (.doc)]   [Add New Statement]  |  <-- Line 2: .toolbar-actions-row
+---------------------------------------------------------------------------------------------------+
```

### Layout Specifications
- **Row 1 (`.toolbar-search-row`)**:
  - Contains `#searchInput`, `#filterPeriod`, and `#filterStyle`.
  - Spans `width: 100%; display: flex; align-items: center; gap: 12px;`.
  - `#searchInput` has `flex: 1; min-width: 220px; height: 42px; border: 1.5px solid #d0d7de; border-radius: 8px;`.
  - Focus border color: `#E51A4D` with box-shadow `0 0 0 3px rgba(229, 26, 77, 0.14)`.
  - `#filterPeriod` and `#filterStyle` dropdowns align horizontally in the same row.

- **Row 2 (`.toolbar-actions-row`)**:
  - Positioned directly below Row 1 with `margin-top: 0; display: flex; align-items: center; gap: 10px; flex-wrap: wrap;`.
  - Holds all four action buttons in one line.

### Button Styling Rules
All action buttons on Row 2 are **solid black with bold white text**:
```css
.btn-export,
.btn-sync,
.btn-download-template,
.btn-add {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 9px 16px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  background-color: #1f2328;
  color: #ffffff;
  border: 1px solid #1f2328;
  transition: all 0.18s ease;
  white-space: nowrap;
}

.btn-export:hover,
.btn-sync:hover,
.btn-download-template:hover,
.btn-add:hover {
  background-color: #32383f;
  border-color: #32383f;
  color: #ffffff;
}
```

---

## 3. Tab Switching Menu (`.hub-tabs-container` & `.hub-tabs`)

The tab navigation switcher is centered on the page and styled as an **oval pill container** with **pill buttons** inside. **Tab labels strictly contain NO numbers in parentheses** (to maintain a clean aesthetic and avoid static counts):

```
                  +----------------------------------------------------------------------------------------------------+
                  |  ( Statement Cards )   (( Master Revenue Summary ))   ( Gross Deals Ledger )   ( Net Deals Ledger )|
                  +----------------------------------------------------------------------------------------------------+
```

### Exact CSS Rules
```css
.hub-tabs-container {
  display: flex;
  justify-content: center;
  margin-bottom: 26px;
}

.hub-tabs {
  background: #ffffff;
  border: 1px solid #d0d7de;
  border-radius: 50px;
  padding: 5px;
  display: inline-flex;
  gap: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  flex-wrap: wrap;
}

.hub-tab-btn {
  padding: 8px 20px;
  font-size: 13.5px;
  font-weight: 600;
  border-radius: 40px;
  border: none;
  background: transparent;
  color: #57606a;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.hub-tab-btn:hover {
  color: #1f2328;
  background: #f6f8fa;
}

.hub-tab-btn.active {
  background: #E51A4D;
  color: #ffffff;
  box-shadow: 0 2px 6px rgba(229, 26, 77, 0.35);
}
```

### Tab Markup:
```html
<div class="hub-tabs-container">
  <div class="hub-tabs">
    <button class="hub-tab-btn active" id="tabBtnStatements" onclick="switchHubTab('statements')">Statement Cards</button>
    <button class="hub-tab-btn" id="tabBtnMaster" onclick="switchHubTab('master')">Master Revenue Summary</button>
    <button class="hub-tab-btn" id="tabBtnGross" onclick="switchHubTab('gross')">Gross Deals Ledger</button>
    <button class="hub-tab-btn" id="tabBtnNet" onclick="switchHubTab('net')">Net Deals Ledger</button>
  </div>
</div>
```
  flex-wrap: wrap;
}

.hub-tab-btn {
  display: inline-flex;
  align-items: center;
  padding: 9px 20px;
  border-radius: 40px;
  font-size: 13.5px;
  font-weight: 600;
  border: none;
  background: transparent;
  color: #57606a;
  cursor: pointer;
  transition: all 0.2s ease;
}

.hub-tab-btn:hover {
  color: #1f2328;
  background: #f6f8fa;
}

.hub-tab-btn.active {
  background: #E51A4D;
  color: #ffffff;
  box-shadow: 0 2px 6px rgba(229, 26, 77, 0.28);
}
```

---

## 4. Deal Views Architecture (Master, Gross, & Net Tabs)

For **Master Revenue Summary** (`#tabContentMaster`), **Gross Deals Ledger** (`#tabContentGross`), and **Net Deals Ledger** (`#tabContentNet`):

### The "Written Stuff in One Box" Principle
1. **White Card Box (`.master-summary-card`)**:
   - Contains **only** the written informational components:
     - Header row with view title and black **Export CSV** button (`.btn-excel-view`).
     - Financial framework title (`<h4>`) and explanatory description (`<p>`).
     - 3-column data cards grid (`.ledger-desc-grid` containing 3 `.ledger-step-card` elements).
   - `.master-summary-card` has `background: #ffffff; border: 1px solid #e1e4e8; border-radius: 10px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.03);`.
   - `.ledger-desc-box` wrapper has `background: transparent; border: none; padding: 0; margin-top: 20px; margin-bottom: 24px;` so there is **no redundant outer box inside the card**.
   - `.master-summary-card` **MUST CLOSE** (`</div>`) immediately after the description cards.

2. **Independent Table & Viewers**:
   - The tables (`#masterSummaryTable`, `#grossSummaryTable`, `#netSummaryTable`) are placed **OUTSIDE** `.master-summary-card` as **independent standalone components**.
   - Placed directly inside `.master-table-scroll` which has its own border and background:
     ```css
     .master-table-scroll {
       overflow-x: auto;
       -webkit-overflow-scrolling: touch;
       margin-top: 18px;
       border: 1px solid #d0d7de;
       border-radius: 8px;
       background: #ffffff;
     }
     ```
   - In Gross and Net tabs, the **Interactive Calculation Viewers** (`#grossCalcCardContainer`, `#netCalcCardContainer`) are also independent standalone components positioned below the tables.

---

## 5. Modal Windows Architecture (`.modal` & `.modal-overlay`)

When modal popups open (e.g. Word Template Download modal, Google Sheets Sync modal, Add Revenue Statement modal):

### Backdrop Blur Rule
- **Backdrop Blur**: Slightly less blurry with a balanced dark tint.
  ```css
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(15, 23, 42, 0.65);
    backdrop-filter: blur(0.5px);
    -webkit-backdrop-filter: blur(0.5px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }
  ```
- **Modal Close Controls**:
  - Close via the top-right corner cross button (`.btn-modal-close`).
  - No redundant bottom close buttons.

---

## 6. Dynamic Deal Counter & Page Sync Engine

To support full automation without hardcoding static figures or showing outdated counts:
- **No static numbers on navigation tabs**: Hub tabs remain strictly text (`Statement Cards`, `Master Revenue Summary`, `Gross Deals Ledger`, `Net Deals Ledger`).
- **Dynamic table header badges**:
  - Gross Deals Ledger: `Gross Deals Portfolio Summary (<span id="grossDealsCount">...</span> Titles)` (Currently **25 Titles / Statements**)
  - Net Deals Ledger: `Net Deals Portfolio Summary (<span id="netDealsCount">...</span> Titles)` (Currently **10 Titles / Statements**)
- **Dynamic filter options**:
  - `#masterDealFilter` updates option labels dynamically:
    - `All Deals (35 Series)`
    - `Gross Deals (25 Series)`
    - `Net Deals (10 Series)`
- **Dynamic Counting Engine (`updateAllDealCounts()`)**:
  - Dynamically calculates active deal counts directly from the active statement store (`currentShows` / `DEFAULT_SHOWS`).
  - Recalculates deal numbers and synchronizes all header counts and select dropdowns across all pages.
  - Automatically triggered upon:
    1. DOM initialization (`initAllModernDropdowns()`).
    2. Tab switching (`switchHubTab()`).
    3. Adding a new statement (`saveNewStatement()` — instantly increments the appropriate Gross/Net count and total count across all pages).
    4. Deleting a statement entry (`deleteStatement()` — instantly decrements counts across all pages).

---

## 7. Forbidden & Removed Elements (Do NOT Re-add)

The following items were explicitly requested to be removed by the user and **must never be reintroduced**:
1. ❌ **Footnote Disclaimers**:
   - `"Scroll horizontally to see all columns. St. Marin's has a combined Apr–Sep statement, not separate Q2/Q3 figures. Amounts shown are based on audited finance worksheets and remain subject to statement-status verification."`
2. ❌ **Old Subtitle Rows**:
   - `"2026 • Portfolio Performance & Minimum Guarantee Recoupment Ledger"`
   - `"2026 • 24 Active Series with Gross Revenue Royalty Agreements (15% & 20% Royalty Tiers)"`
   - `"2026 • 9 Active Series with Net Revenue Royalty Agreements (15% Royalty Tier)"`
3. ❌ **Redundant Inner Description Borders**:
   - Do NOT give `.ledger-desc-box` a gray background or border inside `.master-summary-card`.
4. ❌ **Trapping Tables inside the Written Card**:
   - Do NOT wrap tables inside `.master-summary-card`. Tables must remain independent.
5. ❌ **Static Deal Counts in Hub Navigation Tabs**:
   - Tab buttons must NEVER show numbers in parentheses like `Statement Cards (35)` or `Gross Deals Ledger (22)`.

---

## 8. Pipeline Execution & Production Verification

When regenerating or modifying the revenue statement platform:
1. Run generator:
   ```powershell
   python backend/generate_revenue_statements.py
   ```
2. Verify:
   - 35 total audited series processed.
   - 31 Master Summary rows across quarters.
   - Clean Vercel production deployment to `https://pocketfm-statements.vercel.app`.
   - Live HTTP 200 response with all layout assertions validated.


