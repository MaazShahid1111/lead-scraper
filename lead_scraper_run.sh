#!/bin/bash
cd "$(dirname "$0")"
source "$(dirname "$0")/venv/bin/activate" 2>/dev/null || true
python lead_scrapper.py "$@"
