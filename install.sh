#!/bin/bash
# ══════════════════════════════════════════════════════════════
#  LEAD SCRAPER — Linux / macOS Installer
# ══════════════════════════════════════════════════════════════

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

ok()   { echo -e "${GREEN}[✅]${NC} $1"; }
fail() { echo -e "${RED}[❌]${NC} $1"; exit 1; }
info() { echo -e "${CYAN}[→]${NC}  $1"; }

echo ""
echo "══════════════════════════════════════════════════════════════"
echo "         LEAD SCRAPER — Installer"
echo "══════════════════════════════════════════════════════════════"
echo ""

# ── Python check ──────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    fail "Python 3 not found. Install from https://python.org"
fi
PY_VER=$(python3 --version | cut -d' ' -f2)
ok "Python $PY_VER found"

# ── pip check ─────────────────────────────────────────────────
if ! command -v pip3 &>/dev/null && ! python3 -m pip --version &>/dev/null; then
    fail "pip not found. Run: sudo apt install python3-pip  OR  brew install python"
fi
ok "pip found"

# ── Virtual environment ───────────────────────────────────────
info "Creating virtual environment..."
python3 -m venv venv
ok "venv created"

# ── Activate and install ──────────────────────────────────────
info "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
ok "Python packages installed"

# ── Playwright browsers ───────────────────────────────────────
info "Installing Playwright browser (Chromium)..."
playwright install chromium
ok "Chromium installed"

# ── Kali/Debian Playwright system deps (optional) ────────────
if command -v apt-get &>/dev/null; then
    info "Installing Playwright system libs (Kali/Debian)..."
    sudo apt-get install -y \
        libglib2.0-0 libnss3 libnspr4 libdbus-1-3 \
        libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
        libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 \
        libxrandr2 libgbm1 libasound2 2>/dev/null || true
    ok "System libs installed"
fi

# ── Wrapper script ────────────────────────────────────────────
info "Creating 'lead_scraper' launcher..."
cat > lead_scraper_run.sh << 'EOF'
#!/bin/bash
DIR="$(cd "$(dirname "$0")"; pwd)"
source "$DIR/venv/bin/activate"
python "$DIR/lead_scraper.py" "$@"
EOF
chmod +x lead_scraper_run.sh
ok "Launcher created: ./lead_scraper_run.sh"

echo ""
echo "══════════════════════════════════════════════════════════════"
echo -e "${GREEN}  ✅ INSTALLATION COMPLETE!${NC}"
echo "══════════════════════════════════════════════════════════════"
echo ""
echo "  Quick start:"
echo ""
echo "    source venv/bin/activate"
echo "    python lead_scraper.py --help"
echo ""
echo "  Or use the launcher directly (no activation needed):"
echo ""
echo "    ./lead_scraper_run.sh --help"
echo "    ./lead_scraper_run.sh scrape --country usa --target 100"
echo ""
echo "══════════════════════════════════════════════════════════════"