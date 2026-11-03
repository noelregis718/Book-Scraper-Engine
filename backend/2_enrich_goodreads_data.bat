@echo off
title Step 2: Enrich Kensington Catalog with Goodreads Data
echo ======================================================================
echo   STEP 2: GOODREADS ENRICHMENT & ROMANTASY CLASSIFICATION
echo ======================================================================
echo Catalog: Kensington_Fantasy_Fiction_Catalog.xlsx
echo.
echo Searching Goodreads for links, ratings, synopsis, and Romantasy subgenres...
echo.

cd /d "%~dp0"
backend\venv\Scripts\python.exe backend\scrape_kensington_fantasy.py --enrich-only

echo.
echo ======================================================================
echo Step 2 Complete! Goodreads data and Romantasy tags enriched.
echo ======================================================================
pause

