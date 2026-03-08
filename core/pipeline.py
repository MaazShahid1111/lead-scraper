"""Full pipeline: scrape → validate → email"""
import asyncio
from core.scraper_cmd   import run_scrape
from core.validator_cmd import _validate
from core.emailer_cmd   import run_email
import json
import os


def run_all(args):
    print("🚀 FULL PIPELINE: Scrape → Validate → Email\n")

    # Step 1: Scrape
    print("━"*55)
    print("STEP 1/3  —  SCRAPING")
    print("━"*55)
    run_scrape(args)

    raw_file   = f"{args.country}_leads.json"
    valid_file = f"{args.country}_leads_valid.json"

    if not os.path.exists(raw_file):
        print("❌ Scrape produced no output file. Aborting.")
        return

    # Step 2: Validate
    print("\n" + "━"*55)
    print("STEP 2/3  —  VALIDATING EMAILS")
    print("━"*55)

    with open(raw_file, 'r', encoding='utf-8') as f:
        leads = json.load(f)

    asyncio.run(_validate(leads, delay=2.0, output_file=valid_file))

    if not os.path.exists(valid_file):
        print("❌ No valid emails found. Aborting email step.")
        return

    # Step 3: Email — reuse args but point to valid file
    print("\n" + "━"*55)
    print("STEP 3/3  —  SENDING EMAILS")
    print("━"*55)
    args.file      = valid_file
    args.delay_min = 3
    args.delay_max = 8
    args.template  = None
    run_email(args)

    print("\n✅ FULL PIPELINE COMPLETE!")