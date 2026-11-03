@echo off
title Kensington Unique Books - Goodreads Scraper
echo ======================================================================
echo    KENSINGTON UNIQUE BOOKS: GOODREADS ENRICHMENT SCRAPER
echo ======================================================================
echo Target: Kensington_Unique_Fantasy_Fiction_Catalog.xlsx (902 Books)
echo Progress: Auto-resumable, saves every 5 books
echo.

cd /d "%~dp0"
backend\venv\Scripts\python.exe backend\scrape_unique_kensington_goodreads.py

echo.
echo ======================================================================
echo Scraping complete! Press any key to exit.
echo ======================================================================
pause

