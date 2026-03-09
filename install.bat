@echo off
echo ══════════════════════════════════════════════════════════════
echo          LEAD SCRAPER — Windows Installer
echo ══════════════════════════════════════════════════════════════

where python >nul 2>&1
if errorlevel 1 (
    echo [X] Python not found. Install from https://python.org
    pause & exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo [OK] %%i found

echo [->] Creating virtual environment...
python -m venv venv
if errorlevel 1 ( echo [X] venv creation failed & pause & exit /b 1 )
echo [OK] venv created

echo [->] Installing dependencies...
venv\Scripts\pip install --upgrade pip -q
venv\Scripts\pip install playwright dnspython requests beautifulsoup4 lxml tqdm colorama python-dotenv -q
if errorlevel 1 ( echo [X] pip install failed & pause & exit /b 1 )
echo [OK] Python packages installed

echo [->] Installing Playwright Chromium...
venv\Scripts\python -m playwright install chromium
echo [OK] Chromium installed

echo [->] Creating launcher...
echo @echo off > lead_scraper_run.bat
echo cd /d "%%~dp0" >> lead_scraper_run.bat
echo call venv\Scripts\activate >> lead_scraper_run.bat
echo python lead_scrapper.py %%* >> lead_scraper_run.bat
echo [OK] Launcher created: lead_scraper_run.bat

echo.
echo ══════════════════════════════════════════════════════════════
echo   OK INSTALLATION COMPLETE!
echo ══════════════════════════════════════════════════════════════
echo.
echo   Quick start:
echo     venv\Scripts\activate
echo     python lead_scrapper.py --help
echo.
echo   Or use launcher:
echo     lead_scraper_run.bat --help
echo     lead_scraper_run.bat scrape --country usa --target 100
echo.
pause