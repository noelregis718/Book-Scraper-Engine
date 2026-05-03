# PocketFM

A high-performance, industrial-scale data extraction engine designed for comprehensive book metadata harvesting. This platform orchestrates a multi-tiered pipeline to discover, extract, and enrich deep metadata for any genre, keyword, or attribute without limits.

## 🚀 Unlimited Scaling & Versatility

Unlike rigid scraping tools, this engine is built for **infinite discovery**:
- **Zero Limits**: Not restricted to any specific title count or genre boundary.
- **Dynamic Targeting**: Scrapes per genre, per attribute, or via custom search keywords as requested.
- **Multi-Genre Support**: Seamlessly transitions between Romantasy, Paranormal Romance, Werewolves, or any other niche market.
- **Attribute-Level Control**: Fine-tune extraction to target specific data points like price, series info, or author contact details.

## 🌟 Premium Features

- **Industrial Scaling Engine**: Automated multi-batch orchestration with state persistence and intelligent rate-limiting to ensure continuous operation.
- **Multi-Tiered Discovery Intelligence**: 
    - **Market Tier (Amazon)**: Deep extraction of bestseller ranks, pricing, series hierarchy, and publication details.
    - **Community Tier (Goodreads)**: Advanced fallback logic to resolve series URLs, book counts, and ratings.
    - **Author Contact Tier**: Automated discovery of official websites, social media (FB/IG/X), and professional agent representation.
- **Series Extraction Intelligence**: Sophisticated regex-based parsing to identify series names and link book sequences accurately.
- **Professional Data Delivery**: Generates high-fidelity, production-ready Excel (`.xlsx`) workbooks with optimized formatting and structured schemas.

## 🛠️ Technical Stack

- **Backend**: Python 3.11, Playwright (Async), Pandas, OpenPyXL.
- **Logic Engine**: Multi-tab extraction (optimized for high throughput), Regex-based normalization, and mission-aware state polling.
- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS, Framer Motion.

---

## 📁 System Architecture

```text
PocketFM/
├── backend/
│   ├── keyword_scraper.py   # Main Industrial Mission Orchestrator
│   ├── scraper.py           # Multi-Tiered Intelligence (Amazon/Goodreads/Author)
│   ├── repair_goodreads.py  # Quality Assurance & Deep Metadata Repair
│   ├── excel_utility.py     # Professional Excel Sync & Formatting
│   └── *_state.json         # Real-time Mission Tracking & Persistence
├── frontend/
│   ├── src/                 # Premium React UI for Mission Control
└── data/                    # Dynamic Output Directory for Master Workbooks
```

---

## 📊 Comprehensive Data Schema

| Section | Key Data Points |
| :--- | :--- |
| **Market Metadata** | Genre/Sub-Genre, Price, Stars, Ratings, Bestseller Rank, Publisher, ASIN. |
| **Series Intelligence** | Series URL, Book Order, Total Series Volumes, Series Ratings/Stats. |
| **Creative Content** | Loglines, One-Sentence hooks, Genre classifications. |
| **Author Enrichment** | Email, Agent Contacts, Website, Facebook, Instagram, Twitter/X. |

---

## ⚖️ Quality & Fidelity Standards

The platform enforces the **"Total Fidelity"** protocol:
1. **Deduplication**: Automatic filtering of sponsored results and duplicate entries across missions.
2. **Cross-Reference Validation**: Every record is cross-validated across multiple sources (Amazon/Goodreads) to ensure accuracy.
3. **Deep Contact Discovery**: Multi-source validation for author and professional representation emails.

