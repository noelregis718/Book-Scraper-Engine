# Master Pipeline Runner Guide

This document explains the workflow and execution instructions for the `pipeline_runner.py` script. This script is the "Master Orchestrator" that fully automates the process of identifying, downloading, and converting series books based on an Excel spreadsheet.

## 🚀 What It Does
The pipeline reads the `CT _ US _ Pipeline Master Sheet.xlsx` (specifically the **Self-Pub Prioritization** tab), identifies series links, finds all the books within those series, attempts to download them from multiple free sources, and finally converts them into Word documents (`.docx`).

## 🔄 The 5-Step Workflow

### 1. The Goodreads Initializer (`get_primary_books_from_goodreads`)
- **Action:** Opens the Goodreads series link provided in the Excel sheet.
- **Purpose:** Scrapes the page to find exactly how many "Primary Works" belong to the series (ignoring novellas, prequels, and boxed sets unless specified) and grabs their exact titles and authors.

### 2. The Smart Pre-Check (`Smart Skip`)
- **Action:** Checks the local `downloads/` directory.
- **Purpose:** If a `.docx`, `.pdf`, or `.epub` for a specific book already exists in the folder, the script marks it as `[Smart Skip]` and entirely skips the download process for that book, saving time and internet bandwidth.

### 3. Primary Scraper: OceanOfPDF (`process_ocean_downloads`)
- **Action:** Uses a 3-worker multithreaded Playwright browser to search OceanOfPDF.
- **Purpose:** Automatically searches for the title and author, ranks the search results to avoid boxed sets, bypasses Cloudflare security, and downloads the free PDF.

### 4. Fallback Scraper: Z-Library (`process_zlib_downloads`)
- **Action:** Uses a 2-worker multithreaded Playwright browser.
- **Purpose:** Acts as a safety net. It only processes the specific books that OceanOfPDF failed to find. It securely logs into Z-Library using your credentials, downloads the best available `.epub` or `.pdf`, and saves it.

### 5. Optimization & Conversion (`process_file_optimizations` & `process_pdf_conversions`)
- **Action:** Processes all successfully downloaded files.
- **Purpose:** Compresses any excessively large PDFs, and then automatically converts all the downloaded PDFs and EPUBs into clean `.docx` Word Documents.

---

## ⚙️ Setup & Prerequisites

Before running the pipeline, ensure your Z-Library credentials are set up as environment variables, as the fallback scraper requires an account to download books.

1. Open your Windows Start menu and search for **Environment Variables**.
2. Click **Edit the system environment variables**.
3. Add the following User variables:
   - `ZLIB_EMAIL` : Your Z-Library account email.
   - `ZLIB_PASSWORD` : Your Z-Library account password.

*Note: The system will automatically save your login session to `zlib_state.json` to prevent Z-Library from blocking you for logging in too frequently.*

---

## 💻 How to Run the Pipeline

The pipeline is designed to be run in "batches" so that it doesn't crash your computer or get you IP-banned by Goodreads or Cloudflare. You control this using the `--start` and `--end` row flags.

**To run the pipeline for a single row (e.g., Row 2):**
```powershell
python backend\pipeline_runner.py --start 2 --end 2
```

**To run the pipeline for a batch of rows (e.g., Rows 5 through 10):**
```powershell
python backend\pipeline_runner.py --start 5 --end 10
```

## 📊 Reading the Output
At the end of the run, the terminal will print a clear summary telling you exactly what happened:
- How many books successfully downloaded and converted to DOCX.
- How many books failed the DOCX conversion (but the raw PDF/EPUB was kept).
- How many books failed to download entirely (could not be found on either site). 
- Total execution time.
