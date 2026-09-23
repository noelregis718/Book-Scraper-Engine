import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import openpyxl
from backend.scrapers.romantasy_goodreads_series import get_primary_books_from_goodreads
from backend.scrapers.romantasy_ocean_downloader import process_ocean_downloads
from backend.scrapers.zlib_scraper import process_zlib_downloads
from backend.utils.file_optimizer import process_file_optimizations
from backend.utils.pdf_converter import process_pdf_conversions
from backend.utils.drive_uploader import upload_folder_to_drive
from urllib.parse import urlparse
from dotenv import load_dotenv

# Target Google Drive Folder ID provided by the user
TARGET_DRIVE_FOLDER_ID = "1XSby2d7Tf0s894JHpnAer_893zk-jo_O"


load_dotenv()

def sanitize_folder_name(name: str) -> str:
    """Removes invalid characters for folder names"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '')
    return name.strip()

import sys

from datetime import datetime

def run_pipeline(start_row: int, end_row: int = None, limit: int = None):
    import time
    pipeline_start_time = time.time()
    excel_path = r"e:\Internship\PocketFM\Romantasy - Subjective Reviews - 9.9.26.xlsx"
    downloads_base = r"e:\Internship\PocketFM\downloads_part2"
    
    if not os.path.exists(downloads_base):
        os.makedirs(downloads_base)
        
    print(f"Loading Excel file: {excel_path}")
    wb = openpyxl.load_workbook(excel_path, read_only=True, data_only=True)
    
    sheet_name = wb.sheetnames[0]
    ws = wb[sheet_name]
    
    total_ocean_downloaded = 0
    total_zlib_downloaded = 0
    valid_processed_count = 0
    last_row_checked = start_row - 1
    
    # Load history of already processed series to prevent duplicates across runs
    processed_history_path = os.path.join(downloads_base, "processed_series.txt")
    processed_links = set()
    if os.path.exists(processed_history_path):
        with open(processed_history_path, "r", encoding="utf-8") as f:
            for line in f:
                processed_links.add(line.strip())
                
    # Process exactly the 130 part2 rows to fill in missing books
    target_rows = [192, 193, 196, 197, 203, 204, 211, 215, 216, 221, 223, 225, 227, 228, 235, 239, 247, 250, 251, 252, 256, 257, 258, 259, 262, 263, 266, 268, 269, 273, 275, 276, 289, 290, 297, 303, 306, 310, 312, 314, 315, 316, 318, 320, 322, 323, 325, 329, 330, 332, 333, 334, 335, 338, 339, 343, 349, 351, 353, 354, 357, 360, 362, 364, 365, 370, 371, 372, 375, 376, 378, 379, 380, 381, 382, 615, 616, 618, 619, 620, 622, 623, 628, 703, 704, 709, 710, 712, 716, 718, 721, 722, 723, 725, 727, 729, 730, 731, 860, 864, 866, 867, 868, 869, 871, 876, 877, 878, 880, 881, 882, 883, 885, 887, 891, 893, 894, 897, 899, 902, 906, 908, 909, 910, 961, 990, 1004, 1005, 1007, 1008]
    
    for row_idx in target_rows:
        row = next(ws.iter_rows(min_row=row_idx, max_row=row_idx, values_only=True))
        
        series_name_raw = row[0]
        if not series_name_raw:
            continue
            
        series_name = str(series_name_raw).strip()
        goodreads_link = str(row[3] or '').strip()
        
        if not goodreads_link or goodreads_link.lower() == 'none':
            print(f"[Row {row_idx}] Skipping {series_name} - No link found.")
            continue
            
        if 'goodreads.com/series' not in goodreads_link:
            print(f"[Row {row_idx}] Skipping non-series link: {goodreads_link}")
            continue
            
        print(f"\n[Row {row_idx}] Targeting: {series_name} ({goodreads_link})")
        
        # 1. Scrape Goodreads for book list and true series name
        books, actual_series_name = get_primary_books_from_goodreads(goodreads_link)
        if not books:
            print(f"[Row {row_idx}] No primary books found or failed to scrape series.")
            continue
            
        clean_series_name = sanitize_folder_name(actual_series_name)
        series_dir = os.path.join(downloads_base, f"{row_idx}_{clean_series_name}")
        
        if not os.path.exists(series_dir):
            os.makedirs(series_dir)
            
        print(f"\n{'='*50}")
        print(f"Processing Series: {clean_series_name}")
        print(f"Link: {goodreads_link}")
        print(f"Directory: {series_dir}")
        print(f"{'='*50}")
        
        # Pre-check: Skip books that already exist in the folder
        from backend.scrapers.romantasy_ocean_downloader import sanitize_filename
        import re
        for book in books:
            # Clean Goodreads (Series, #1) trailing tags
            clean_book_title = re.sub(r'\s*\(.*?\)\s*$', '', book.title)
            safe_title_file = sanitize_filename(clean_book_title)
            base_filename = f"{book.number}_{safe_title_file}"
            
            docx_path = os.path.join(series_dir, f"{base_filename}.docx")
            pdf_path = os.path.join(series_dir, f"{base_filename}.pdf")
            epub_path = os.path.join(series_dir, f"{base_filename}.epub")
            
            if os.path.exists(docx_path):
                print(f"[Smart Skip] {book.title} already exists as DOCX. Skipping download and conversion.")
                book.status = "completed"
                book.source = "Pre-existing"
            elif os.path.exists(pdf_path):
                print(f"[Smart Skip] {book.title} already exists as PDF. Skipping download, queuing for conversion.")
                book.status = "downloaded"
                book.pdf_path = pdf_path
                book.source = "Pre-existing"
            elif os.path.exists(epub_path):
                print(f"[Smart Skip] {book.title} already exists as EPUB. Skipping download, queuing for conversion.")
                book.status = "downloaded"
                book.epub_path = epub_path
                book.source = "Pre-existing"
            
        max_retries = 3
        for attempt in range(max_retries):
            # Check if there are books that still need to be processed (failed or not started)
            pending_books = [b for b in books if b.status != "completed"]
            if not pending_books:
                break
                
            if attempt > 0:
                print(f"\n[Row {row_idx}] Retrying {len(pending_books)} failed books (Attempt {attempt+1}/{max_retries})...")
                for b in pending_books:
                    b.status = "pending"
                    b.error_message = ""
                    # If it previously failed conversion, delete the bad PDF so it can be re-downloaded
                    if hasattr(b, 'pdf_path') and b.pdf_path and os.path.exists(b.pdf_path):
                        try:
                            os.remove(b.pdf_path)
                            b.pdf_path = None
                        except Exception:
                            pass
                            
            # 2. Download PDFs from OceanOfPDF
            process_ocean_downloads(books, series_dir)
            
            # 2.5 Fallback to Z-Library for failed downloads
            process_zlib_downloads(books, series_dir)
            
            # 3. Optimize files (compress large PDFs, convert EPUBs to DOCX)
            process_file_optimizations(books)
            
            # 4. Convert downloaded PDFs to Word docs
            process_pdf_conversions(books)
            
        # 5. Upload the final folder to Google Drive
        try:
            upload_folder_to_drive(series_dir, TARGET_DRIVE_FOLDER_ID)
        except Exception as e:
            print(f"[Row {row_idx}] Exception during Google Drive Upload: {e}")
        
        success_count = sum(1 for b in books if b.status == "completed")
        failed_count = sum(1 for b in books if b.status == "conversion_failed")
        download_failed = sum(1 for b in books if b.status == "failed")
        
        ocean_count = sum(1 for b in books if getattr(b, 'source', None) == "OceanOfPDF" and b.status == "completed")
        zlib_count = sum(1 for b in books if getattr(b, 'source', None) == "Z-Library" and b.status == "completed")
        
        total_ocean_downloaded += ocean_count
        total_zlib_downloaded += zlib_count
        
        print(f"\n[Row {row_idx}] Finished processing series: {clean_series_name}")
        print(f"  - Successfully downloaded & converted to DOCX: {success_count} (OceanOfPDF: {ocean_count}, Z-Library: {zlib_count})")
        print(f"  - Failed DOCX conversion (PDF/EPUB kept): {failed_count}")
        print(f"  - Failed to download entirely: {download_failed}")
        
        # Mark as globally processed
        processed_links.add(goodreads_link)
        with open(processed_history_path, "a", encoding="utf-8") as f:
            f.write(f"{goodreads_link}\n")
        
        valid_processed_count += 1
        if limit is not None and valid_processed_count >= limit:
            print(f"\n[INFO] Reached requested limit of {limit} valid rows for Noel Regis.")
            break
        
    pipeline_end_time = time.time()
    total_seconds = int(pipeline_end_time - pipeline_start_time)
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    
    print(f"\n{'='*50}")
    print("PIPELINE RUN COMPLETE")
    print(f"Total valid 'Noel Regis' rows processed: {valid_processed_count}")
    print(f"Last Excel row checked: {last_row_checked}")
    print(f"-> START AT ROW {last_row_checked + 1} NEXT TIME <-")
    print(f"Grand Total - OceanOfPDF downloads: {total_ocean_downloaded}")
    print(f"Grand Total - Z-Library downloads:  {total_zlib_downloaded}")
    print(f"Total Execution Time: {minutes} minutes and {seconds} seconds")
    print(f"{'='*50}\n")
        
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run the romantasy downloader pipeline.")
    parser.add_argument("--start", type=int, required=True, help="Starting row index (e.g. 2)")
    parser.add_argument("--end", type=int, required=False, help="Ending row index (e.g. 100)")
    parser.add_argument("--limit", type=int, required=False, help="Process exactly N valid rows assigned to Noel Regis")
    args = parser.parse_args()
    
    run_pipeline(args.start, args.end, args.limit)
