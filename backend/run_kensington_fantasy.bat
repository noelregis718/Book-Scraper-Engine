@echo off
title Kensington Fantasy Fiction Scraper
echo ======================================================================
echo    POCKET FM - KENSINGTON FANTASY FICTION SCRAPER
echo ======================================================================
echo Target: https://www.kensingtonbooks.com/shop/product-category/fiction/fantasy-fiction/
echo Output: Kensington_Fantasy_Fiction_Catalog.xlsx
echo.

cd /d "%~dp0"
backend\venv\Scripts\python.exe backend\scrape_kensington_fantasy.py %*

echo.
echo ======================================================================
echo Scraper finished. Press any key to exit.
echo ======================================================================
pause

