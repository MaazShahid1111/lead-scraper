#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║              LEAD SCRAPER - AI Cold Outreach Tool            ║
║   Scrape → Validate → Email | Google Maps + Gmail SMTP       ║
╚══════════════════════════════════════════════════════════════╝

Usage:
    lead_scraper scrape   --country usa --target 500
    lead_scraper validate --file usa_leads.json
    lead_scraper email    --file usa_leads_valid.json --limit 20
    lead_scraper all      --country usa --target 100 --email you@gmail.com
"""

import argparse
import sys
import os

# ── make sure core/ is importable ────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from core.scraper_cmd   import run_scrape
from core.validator_cmd import run_validate
from core.emailer_cmd   import run_email
from core.pipeline      import run_all


BANNER = """
╔══════════════════════════════════════════════════════════════╗
║              LEAD SCRAPER  -  Cold Outreach Tool             ║
║        Scrape → Validate → Email  |  100% Automated          ║
╚══════════════════════════════════════════════════════════════╝
"""


def build_parser():
    parser = argparse.ArgumentParser(
        prog='lead_scraper',
        description='Automated lead generation & cold outreach tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Scrape 500 USA businesses with emails (no website)
  python lead_scraper.py scrape --country usa --target 500

  # Scrape specific cities and niches
  python lead_scraper.py scrape --country usa --cities "Austin TX" "Denver CO" --niches "Coffee Shop" "Gym" --target 200

  # Validate collected emails
  python lead_scraper.py validate --file usa_leads.json

  # Send cold emails (20 per day limit recommended)
  python lead_scraper.py email --file usa_leads_valid.json --from you@gmail.com --app-password "xxxx xxxx xxxx xxxx" --name "Your Name" --limit 20

  # Run full pipeline (scrape → validate → email) in one go
  python lead_scraper.py all --country usa --target 100 --from you@gmail.com --app-password "xxxx xxxx xxxx xxxx" --name "Your Name"

COUNTRIES SUPPORTED:
  usa, uk, canada, australia, ireland, new_zealand

TIPS:
  • Gmail daily limit: 20 emails/day (new account), 50/day (older account)
  • Always use a burner Gmail + App Password (not your real password)
  • Run scrape first, then validate, then email — or use 'all' to do it in one shot
        """
    )

    subparsers = parser.add_subparsers(dest='command', metavar='COMMAND')
    subparsers.required = True

    # ── SCRAPE ────────────────────────────────────────────────
    p_scrape = subparsers.add_parser(
        'scrape',
        help='Scrape Google Maps for businesses without websites',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Scrape Google Maps for businesses that have no website but have an email.'
    )
    p_scrape.add_argument('--country',   required=True,
                          choices=['usa', 'uk', 'canada', 'australia', 'ireland', 'new_zealand'],
                          help='Target country')
    p_scrape.add_argument('--target',    type=int, default=500, metavar='N',
                          help='Stop after collecting N leads (default: 500)')
    p_scrape.add_argument('--cities',    nargs='+', metavar='CITY',
                          help='Override default city list (e.g. "Austin TX" "Denver CO")')
    p_scrape.add_argument('--niches',    nargs='+', metavar='NICHE',
                          help='Override default niche list (e.g. "Coffee Shop" "Gym")')
    p_scrape.add_argument('--output',    default=None, metavar='FILE',
                          help='Output JSON file (default: <country>_leads.json)')
    p_scrape.add_argument('--headless',  action='store_true', default=True,
                          help='Run browser headless (default: True)')
    p_scrape.add_argument('--no-headless', dest='headless', action='store_false',
                          help='Show browser window while scraping')

    # ── VALIDATE ──────────────────────────────────────────────
    p_val = subparsers.add_parser(
        'validate',
        help='Validate email addresses via SMTP (free, no API)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Verify collected emails are real using free SMTP verification.'
    )
    p_val.add_argument('--file',   required=True, metavar='FILE',
                       help='JSON leads file to validate')
    p_val.add_argument('--delay',  type=float, default=2.0, metavar='SECONDS',
                       help='Delay between checks to avoid rate limiting (default: 2)')
    p_val.add_argument('--output', default=None, metavar='FILE',
                       help='Output file for valid leads only (default: <file>_valid.json)')

    # ── EMAIL ─────────────────────────────────────────────────
    p_email = subparsers.add_parser(
        'email',
        help='Send cold outreach emails to validated leads',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Send personalised cold emails via Gmail SMTP.'
    )
    p_email.add_argument('--file',         required=True, metavar='FILE',
                         help='JSON file of validated leads')
    p_email.add_argument('--from',         required=True, dest='gmail', metavar='EMAIL',
                         help='Your Gmail address')
    p_email.add_argument('--app-password', required=True, metavar='PASSWORD',
                         help='Gmail App Password (16 chars, spaces OK)')
    p_email.add_argument('--name',         required=True, metavar='NAME',
                         help='Your name (used in email signature)')
    p_email.add_argument('--limit',        type=int, default=20, metavar='N',
                         help='Max emails to send today (default: 20)')
    p_email.add_argument('--delay-min',    type=int, default=3, metavar='SECONDS',
                         help='Minimum delay between sends (default: 3)')
    p_email.add_argument('--delay-max',    type=int, default=8, metavar='SECONDS',
                         help='Maximum delay between sends (default: 8)')
    p_email.add_argument('--template',     default=None, metavar='FILE',
                         help='Custom email template file (optional)')

    # ── ALL ───────────────────────────────────────────────────
    p_all = subparsers.add_parser(
        'all',
        help='Run full pipeline: scrape → validate → email',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Run the complete pipeline in one command.'
    )
    p_all.add_argument('--country',      required=True,
                       choices=['usa', 'uk', 'canada', 'australia', 'ireland', 'new_zealand'])
    p_all.add_argument('--target',       type=int, default=100, metavar='N',
                       help='Leads to scrape before emailing (default: 100)')
    p_all.add_argument('--from',         required=True, dest='gmail', metavar='EMAIL')
    p_all.add_argument('--app-password', required=True, metavar='PASSWORD')
    p_all.add_argument('--name',         required=True, metavar='NAME')
    p_all.add_argument('--limit',        type=int, default=20, metavar='N',
                       help='Max emails to send (default: 20)')

    return parser


def main():
    print(BANNER)
    parser = build_parser()
    args   = parser.parse_args()

    if args.command == 'scrape':
        run_scrape(args)
    elif args.command == 'validate':
        run_validate(args)
    elif args.command == 'email':
        run_email(args)
    elif args.command == 'all':
        run_all(args)


if __name__ == '__main__':
    main()