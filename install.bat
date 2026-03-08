@echo off
:: ══════════════════════════════════════════════════════════════
::  LEAD SCRAPER — Windows Installer
:: ══════════════════════════════════════════════════════════════

echo.
echo ══════════════════════════════════════════════════════════════
echo          LEAD SCRAPER — Windows Installer
echo ══════════════════════════════════════════════════════════════
echo.

:: ── Python check ─────────────────────────────────────────────
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Python not found!
    echo     Download from: https://www.python.org/downloads/
    echo     Make sure to check "Add Python to PATH" during install
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version') do echo [OK] Python %%v found

:: ── Virtual environment ───────────────────────────────────────
echo [ ] Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 ( echo [X] venv creation failed & pause & exit /b 1 )
echo [OK] venv created

:: ── Activate and install ─────────────────────────────────────
echo [ ] Installing Python packages...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q
if %errorlevel% neq 0 ( echo [X] Package install failed & pause & exit /b 1 )
echo [OK] Packages installed

:: ── Playwright browser ───────────────────────────────────────
echo [ ] Installing Playwright browser...
playwright install chromium
if %errorlevel% neq 0 ( echo [X] Playwright install failed & pause & exit /b 1 )
echo [OK] Chromium installed

:: ── Launcher bat ─────────────────────────────────────────────
echo [ ] Creating launcher...
(
echo @echo off
echo set DIR=%%~dp0
echo call "%%DIR%%venv\Scripts\activate.bat"
echo python "%%DIR%%lead_scraper.py" %%*
) > lead_scraper_run.bat
echo [OK] Launcher created: lead_scraper_run.bat

echo.
echo ══════════════════════════════════════════════════════════════
echo   INSTALLATION COMPLETE!
echo ══════════════════════════════════════════════════════════════
echo.
echo   Quick start:
echo.
echo     lead_scraper_run.bat --help
echo     lead_scraper_run.bat scrape --country usa --target 100
echo     lead_scraper_run.bat validate --file usa_leads.json
echo     lead_scraper_run.bat email --file usa_leads_valid.json --from you@gmail.com --app-password "xxxx xxxx xxxx xxxx" --name "Your Name"
echo.
echo ══════════════════════════════════════════════════════════════
pause