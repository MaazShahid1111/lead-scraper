#!/bin/bash
set -e

echo "══════════════════════════════════════════════════════════════"
echo "         LEAD SCRAPER — Installer"
echo "══════════════════════════════════════════════════════════════"

# ── Python check ──────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo "[❌] Python3 not found. Install it first."
    exit 1
fi
PY_VER=$(python3 --version 2>&1)
echo "[✅] $PY_VER found"

# ── pip check ─────────────────────────────────────────────────
if ! command -v pip3 &>/dev/null && ! python3 -m pip --version &>/dev/null; then
    echo "[→]  Installing pip..."
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3
fi
echo "[✅] pip found"

# ── Create venv ───────────────────────────────────────────────
echo "[→]  Creating virtual environment..."
python3 -m venv venv
echo "[✅] venv created at ./venv"

# ── Activate venv ─────────────────────────────────────────────
source venv/bin/activate

# ── Install dependencies into venv ────────────────────────────
echo "[→]  Installing Python dependencies into venv..."
venv/bin/pip install --upgrade pip -q
venv/bin/pip install \
    playwright \
    dnspython \
    requests \
    google-search-results \
    selenium \
    beautifulsoup4 \
    lxml \
    smtplib2 \
    tqdm \
    colorama \
    python-dotenv -q 2>/dev/null || \
venv/bin/pip install \
    playwright \
    dnspython \
    requests \
    beautifulsoup4 \
    lxml \
    tqdm \
    colorama \
    python-dotenv -q
echo "[✅] Python packages installed"

# ── Install Playwright browser ────────────────────────────────
echo "[→]  Installing Playwright browser (Chromium)..."
venv/bin/python -m playwright install chromium
echo "[✅] Chromium installed"

# ── Install Playwright system libs ────────────────────────────
echo "[→]  Installing Playwright system libs..."
venv/bin/python -m playwright install-deps chromium 2>/dev/null || \
sudo apt-get install -y \
    libglib2.0-0t64 libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 \
    libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 \
    libxrandr2 libgbm1 libasound2t64 libpango-1.0-0 libcairo2 \
    libnspr4 libnss3 2>/dev/null || true
echo "[✅] System libs installed"

# ── Fix circular imports ──────────────────────────────────────
# scraper_cmd importing itself
if grep -q "^from core.scraper_cmd" core/scraper_cmd.py 2>/dev/null; then
    sed -i '/^from core\.scraper_cmd/d' core/scraper_cmd.py
    echo "[✅] Fixed self-import in scraper_cmd.py"
fi

# pipeline.py importing scraper_cmd at top level (causes circular import)
if grep -q "^from core.scraper_cmd\|^from core.validator_cmd\|^from core.emailer_cmd\|^from core.whatsapp_cmd" core/pipeline.py 2>/dev/null; then
    sed -i '/^from core\.scraper_cmd/d' core/pipeline.py
    sed -i '/^from core\.validator_cmd/d' core/pipeline.py
    sed -i '/^from core\.emailer_cmd/d' core/pipeline.py
    sed -i '/^from core\.whatsapp_cmd/d' core/pipeline.py
    echo "[✅] Fixed circular imports in pipeline.py"
    # Add lazy imports inside run_all function
    venv/bin/python3 - << 'PYEOF'
import re
path = 'core/pipeline.py'
src = open(path).read()
old = 'def run_all(args):'
new = '''def run_all(args):
    from core.scraper_cmd   import run_scrape
    from core.validator_cmd import run_validate
    from core.emailer_cmd   import run_email
    from core.whatsapp_cmd  import run_whatsapp'''
if old in src and 'from core.scraper_cmd' not in src.split('def run_all')[0]:
    open(path, 'w').write(src.replace(old, new, 1))
    print("[✅] Lazy imports added to run_all()")
PYEOF
fi

# Check run_scrape exists in scraper_cmd.py
if ! grep -q "^def run_scrape" core/scraper_cmd.py 2>/dev/null; then
    echo "[⚠️]  run_scrape missing from scraper_cmd.py — appending wrapper..."
    cat >> core/scraper_cmd.py << 'WRAPPER'

def run_scrape(args):
    """Entry point called by lead_scrapper.py"""
    import asyncio
    asyncio.run(main_async(args))
WRAPPER
    # If main_async doesn't exist either, add a simple sync wrapper
    if ! grep -q "def main_async\|def main" core/scraper_cmd.py 2>/dev/null; then
        cat >> core/scraper_cmd.py << 'WRAPPER2'

def main_async(args):
    main()
WRAPPER2
    fi
    echo "[✅] run_scrape wrapper added"
fi

# ── Create launcher script ────────────────────────────────────
echo "[→]  Creating launcher..."
cat > lead_scraper_run.sh << 'LAUNCHER'
#!/bin/bash
cd "$(dirname "$0")"
source "$(dirname "$0")/venv/bin/activate" 2>/dev/null || true
python lead_scrapper.py "$@"
LAUNCHER
chmod +x lead_scraper_run.sh
echo "[✅] Launcher created: ./lead_scraper_run.sh"

echo ""
echo "══════════════════════════════════════════════════════════════"
echo "  ✅ INSTALLATION COMPLETE!"
echo "══════════════════════════════════════════════════════════════"
echo ""
echo "  Quick start:"
echo "    source venv/bin/activate"
echo "    python lead_scrapper.py --help"
echo ""
echo "  Or use the launcher (no activation needed):"
echo "    ./lead_scraper_run.sh --help"
echo "    ./lead_scraper_run.sh scrape --country usa --target 100"
echo ""
echo "══════════════════════════════════════════════════════════════"