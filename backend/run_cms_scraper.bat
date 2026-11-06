@echo off
title Pocket FM CMS Live Scraper & Sheet Sync
echo ======================================================================
echo           Pocket FM CMS Live Scraper (Argus Show Data Sync)
echo ======================================================================
echo.
echo [STEP 1] Launching Chromium browser...
echo [STEP 2] Enter your credentials and JumpCloud 2FA code in the browser.
echo [STEP 3] Once the CMS dashboard loads, press ENTER here to start scraping!
echo.
cd /d "%~dp0"
if exist "venv\Scripts\python.exe" (
    call venv\Scripts\activate.bat 2>nul
    venv\Scripts\python.exe cms_scraper_final.py
) else if exist "..\backend\venv\Scripts\python.exe" (
    call ..\backend\venv\Scripts\activate.bat 2>nul
    ..\backend\venv\Scripts\python.exe cms_scraper_final.py
) else (
    python cms_scraper_final.py
)
echo.
echo ======================================================================
echo Execution complete. Check 'Argus Show Data' tab.
echo ======================================================================
pause
