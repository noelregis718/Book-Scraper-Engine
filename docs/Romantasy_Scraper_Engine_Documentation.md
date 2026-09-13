# Romantasy Scraper Engine: Complete Technical Documentation

## Overview
The Romantasy Scraper Engine is a highly robust, multi-stage, automated pipeline designed to read book series assignments from an Excel spreadsheet, scrape the correct primary books from Goodreads, download the books from OceanOfPDF (with a fallback to Z-Library), and convert the downloaded files into DOCX format. 

The pipeline is specifically optimized for uninterrupted batch processing, aggressive ad-evasion, and strict duplicate prevention.

---

## 1. The Pipeline Runner (`romantasy_pipeline_runner.py`)
The pipeline runner acts as the orchestrator of the entire process.

### Features:
- **Targeted Processing:** Scans `Romantasy - Subjective Reviews - 9.9.26.xlsx` and strictly processes only rows where the `POC` column is exactly set to "Noel Regis".
- **Batch Controls:** Supports targeted execution via command-line arguments:
  - `--start`: The starting row index (e.g., `--start 2`)
  - `--limit`: Processes exactly `N` valid rows assigned to the user, automatically skipping other POCs.
- **Global Duplicate Tracking:** 
  - Maintains a master ledger of processed series at `downloads/processed_series.txt`.
  - Before opening any browser, it checks if the Goodreads link exists in the ledger. If found, it instantly skips the row, preventing the same series from being scraped twice across multiple runs.
- **Smart Skip (Resume Capability):** If the pipeline is interrupted, it will check the specific `downloads/{row_idx}_{SeriesName}` directory. If the final `.docx`, `.pdf`, or `.epub` already exists for a book, it will skip downloading it and instantly mark it as completed.

---

## 2. The Goodreads Scraper (`romantasy_goodreads_series.py`)
The first stage of the pipeline fetches the authoritative list of books for a given series.

### Features:
- **Cloudflare Bypass:** Uses Playwright (headed mode) with a strategic timeout to allow Cloudflare anti-bot checks to pass before extracting the HTML.
- **Primary Book Extraction:** 
  - Parses the series page to extract only whole-number primary books (Book 1, Book 2, etc.).
  - **Strict Prequel Filtering:** Completely ignores prequels, novellas, and spin-offs (e.g., Book 0, Book 0.5, Book 1.5).
  - **Romantasy Limit:** Hard-capped to only extract Books 1 through 5 of any given series.

---

## 3. The Primary Downloader: OceanOfPDF (`romantasy_ocean_downloader.py`)
The primary source for fetching the actual book files.

### Features:
- **5-Attempt Retry Loop:** Both the search phase and the download phase utilize a strict 5-attempt retry loop to ensure network timeouts or temporary server blocks don't kill the script.
- **Ad-Bypass & Native Interception:** 
  - OceanOfPDF uses aggressive popup ads disguised as download buttons (`target="_blank"`). 
  - The script actively strips `target="_blank"` from the buttons so the click happens in the same tab.
  - If the script detects it was redirected to an ad, it immediately executes `page.go_back()` and retries the click.
  - Uses Playwright's `page.expect_download()` to natively intercept the file stream, saving it directly to the designated series folder.

---

## 4. The Fallback Downloader: Z-Library (`zlib_scraper.py`)
If a book is completely missing from OceanOfPDF or fails all 5 download attempts, the pipeline seamlessly falls back to Z-Library.

### Features:
- **Session Persistence:** Saves login cookies to `zlib_state.json`, meaning the scraper only logs in once and reuses the session for all future runs, preventing rate limits and saving massive amounts of time.
- **Advanced Search Matching:** Compares search results against the author and exact title to ensure the correct book is selected.
- **5-Attempt Retry Loop:** Like OceanOfPDF, uses a 5-attempt retry loop for both search discovery and the final download trigger to handle network instability.

---

## 5. File Processing & Optimization
Once files are successfully downloaded, they go through a final optimization and conversion phase.

### Features:
- **PDF Compression (`file_optimizer.py`):** Very large PDF files are compressed using `PyMuPDF` (formerly `fitz`) to reduce file size without losing text quality, ensuring the conversion process doesn't run out of memory.
- **DOCX Conversion (`pdf_converter.py`):** All downloaded `.pdf` files are run through `pdf2docx` to create a perfectly formatted Microsoft Word Document. 
- **EPUB Support:** If OceanOfPDF provides an `.epub` instead of a PDF, the pipeline will keep the EPUB and skip the DOCX conversion.

---

## Final Output Structure
Everything is neatly organized in the `downloads/` directory:

```text
downloads/
 ├── processed_series.txt             (The global duplicate tracker)
 ├── 123_The Crown of Oaths/          (Prefix: Row Number)
 │    ├── 1_The Crown of Oaths.docx   (Prefix: Book Number)
 │    ├── 2_The Throne of Blood.docx
 │    └── 3_The Queen of Fire.docx
 └── 124_Shadows of the Realm/
      ├── 1_Shadows.docx
      └── 2_Light.docx
```
