@echo off
title Pocket FM Revenue Statement Generator & Live Vercel Sync
echo ======================================================================
echo       Pocket FM Revenue Statement Generator (Google Sheet to Vercel)
echo ======================================================================
echo.
echo [1/3] Reading latest show details from Google Sheets / Excel...
echo [2/3] Generating branded statements with secure private links...
echo [3/3] Deploying live to https://pocketfm-statements.vercel.app...
echo.
cd /d "%~dp0"
if exist "C:\Users\noelr\AppData\Local\Programs\Python\Python312\python.exe" (
    "C:\Users\noelr\AppData\Local\Programs\Python\Python312\python.exe" generate_revenue_statements.py
) else if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe generate_revenue_statements.py
) else (
    python generate_revenue_statements.py
)
echo.
echo ======================================================================
echo Generation & Deployment Complete! Check your Internal Hub:
echo https://pocketfm-statements.vercel.app/internal_hub
echo ======================================================================
pause

