@echo off
title Step 1: Fetch Kensington Fantasy Books
echo ======================================================================
echo   STEP 1: FETCH KENSINGTON FANTASY ^& ROMANTASY TITLES
echo   (Bypasses Cloudflare automatically via Library Database Catalog)
echo ======================================================================
echo Output: Kensington_Fantasy_Fiction_Catalog.xlsx
echo.

cd /d "%~dp0"
backend\venv\Scripts\python.exe backend\fetch_kensington_catalog.py

echo.
echo ======================================================================
echo Step 1 Complete! 266 Books saved to Excel.
echo You can now run '2_enrich_goodreads_data.bat' to get Goodreads data.
echo ======================================================================
pause

