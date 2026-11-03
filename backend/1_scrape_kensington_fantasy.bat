@echo off
title Step 1: Scrape Kensington Fantasy Books
echo ======================================================================
echo   STEP 1: SCRAPE KENSINGTON FANTASY BOOKS & AUTHORS
echo ======================================================================
echo Target: https://www.kensingtonbooks.com/shop/product-category/fiction/fantasy-fiction/
echo Output: Kensington_Fantasy_Fiction_Catalog.xlsx
echo.
echo Note: If a Cloudflare human verification box appears on the Chrome
echo       screen, simply click it to let the page load.
echo.

cd /d "%~dp0"
backend\venv\Scripts\python.exe backend\scrape_kensington_fantasy.py --no-enrich

echo.
echo ======================================================================
echo Step 1 Complete! Book names and authors saved to Excel.
echo You can now run '2_enrich_goodreads_data.bat' whenever you want.
echo ======================================================================
pause

